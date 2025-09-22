"""
Middleware de Moderação para Telegram Bot - Eron.IA
===================================================

Middleware que integra o sistema de moderação com o bot do Telegram,
interceptando mensagens e aplicando ações de moderação automaticamente.

Funcionalidades:
- Interceptação automática de mensagens
- Aplicação de ações de moderação
- Feedback educativo para usuários
- Logging integrado
- Bypass para administradores
- Filtros de conteúdo em tempo real

Uso:
from src.telegram_moderation_middleware import ModerationMiddleware
middleware = ModerationMiddleware()

Autor: Eron.IA System
Data: 2024
"""

from typing import Dict, Any, Optional
from telegram import Update, Message
from telegram.ext import ContextTypes, BaseHandler
import asyncio
from datetime import datetime

try:
    from src.adult_content_moderator import (
        analyze_content, 
        get_user_feedback_message, 
        is_user_blocked,
        ModerationAction
    )
    from src.logging_system import get_logger, LogCategory, log_user_interaction
    from core.config import config
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from src.adult_content_moderator import (
        analyze_content, 
        get_user_feedback_message, 
        is_user_blocked,
        ModerationAction
    )
    from src.logging_system import get_logger, LogCategory, log_user_interaction
    from core.config import config


class ModerationMiddleware:
    """Middleware de moderação para o Telegram Bot"""
    
    def __init__(self, bypass_admin_ids=None):
        self.logger = get_logger(LogCategory.SECURITY, "telegram_moderation")
        self.bypass_admin_ids = set(bypass_admin_ids or [])
        self.enabled = config.moderation['enabled']
        
        # Estatísticas em memória
        self.stats = {
            'messages_checked': 0,
            'messages_blocked': 0,
            'messages_warned': 0,
            'messages_filtered': 0
        }
        
        self.logger.info("Middleware de moderação inicializado")
    
    def add_admin(self, user_id: int):
        """Adiciona administrador que bypassa moderação"""
        self.bypass_admin_ids.add(user_id)
        self.logger.info(f"Administrador {user_id} adicionado ao bypass")
    
    def remove_admin(self, user_id: int):
        """Remove administrador do bypass"""
        self.bypass_admin_ids.discard(user_id)
        self.logger.info(f"Administrador {user_id} removido do bypass")
    
    async def check_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Verifica mensagem e aplica moderação
        
        Returns:
            True: Mensagem pode prosseguir
            False: Mensagem deve ser bloqueada
        """
        if not self.enabled:
            return True
        
        message = update.message
        if not message or not message.text:
            return True
        
        user_id = str(update.effective_user.id)
        
        # Bypass para administradores
        if update.effective_user.id in self.bypass_admin_ids:
            return True
        
        # Verificar se usuário já está bloqueado
        if is_user_blocked(user_id):
            await self._send_blocked_user_message(update, context)
            return False
        
        # Analisar conteúdo
        self.stats['messages_checked'] += 1
        
        try:
            result = analyze_content(message.text, user_id)
            
            # Log da verificação
            log_user_interaction(
                user_id=int(user_id),
                chat_id=update.effective_chat.id,
                action="content_moderation_check",
                details={
                    'severity': result['severity'],
                    'action': str(result['action']),
                    'confidence': result['confidence']
                }
            )
            
            # Aplicar ação baseada no resultado
            return await self._apply_moderation_action(update, context, result)
            
        except Exception as e:
            self.logger.error(f"Erro na moderação: {e}")
            # Em caso de erro, permitir mensagem (fail-safe)
            return True
    
    async def _apply_moderation_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                     result: Dict[str, Any]) -> bool:
        """Aplica ação de moderação baseada no resultado"""
        
        action = ModerationAction(result['action']) if isinstance(result['action'], str) else result['action']
        
        if action == ModerationAction.ALLOW:
            return True
        
        # Obter mensagem de feedback
        feedback_message = get_user_feedback_message(result)
        
        # Aplicar ação específica
        if action == ModerationAction.WARN:
            await self._handle_warn_action(update, context, feedback_message)
            self.stats['messages_warned'] += 1
            return True  # Permite mensagem com aviso
        
        elif action == ModerationAction.FILTER:
            await self._handle_filter_action(update, context, result, feedback_message)
            self.stats['messages_filtered'] += 1
            return False  # Bloqueia mensagem original
        
        elif action in [ModerationAction.QUARANTINE, ModerationAction.BLOCK, ModerationAction.BAN]:
            await self._handle_block_action(update, context, action, feedback_message)
            self.stats['messages_blocked'] += 1
            return False  # Bloqueia mensagem
        
        return True
    
    async def _handle_warn_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                feedback_message: str):
        """Lida com ação de aviso"""
        if feedback_message:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=feedback_message,
                    reply_to_message_id=update.message.message_id
                )
                
                # Agendar remoção da mensagem de aviso após 30 segundos
                asyncio.create_task(self._schedule_message_deletion(
                    context, update.effective_chat.id, delay=30
                ))
                
            except Exception as e:
                self.logger.error(f"Erro ao enviar aviso: {e}")
    
    async def _handle_filter_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                  result: Dict[str, Any], feedback_message: str):
        """Lida com ação de filtragem"""
        try:
            # Tentar deletar mensagem original
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
            
            # Enviar versão filtrada
            filtered_content = self._filter_content(update.message.text, result['flagged_words'])
            
            if filtered_content.strip():
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"👤 **{update.effective_user.first_name}** (mensagem filtrada):\n\n{filtered_content}",
                    parse_mode='Markdown'
                )
            
            # Enviar feedback privado para o usuário
            if feedback_message:
                await context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text=feedback_message
                )
                
        except Exception as e:
            self.logger.error(f"Erro na filtragem: {e}")
    
    async def _handle_block_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                 action: ModerationAction, feedback_message: str):
        """Lida com ações de bloqueio"""
        try:
            # Deletar mensagem original
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
            
            # Determinar mensagem baseada no tipo de ação
            if action == ModerationAction.QUARANTINE:
                public_message = "🛡️ *Mensagem removida por moderação*"
                action_name = "quarentena"
            elif action == ModerationAction.BLOCK:
                public_message = "🚫 *Usuário temporariamente restrito*"
                action_name = "bloqueio"
            elif action == ModerationAction.BAN:
                public_message = "⛔ *Usuário banido do sistema*"
                action_name = "banimento"
            else:
                public_message = "🛡️ *Ação de moderação aplicada*"
                action_name = "moderação"
            
            # Mensagem pública discreta
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=public_message,
                parse_mode='Markdown'
            )
            
            # Remover mensagem pública após 10 segundos
            asyncio.create_task(self._schedule_message_deletion(
                context, update.effective_chat.id, message.message_id, 10
            ))
            
            # Feedback privado detalhado para o usuário
            if feedback_message:
                try:
                    await context.bot.send_message(
                        chat_id=update.effective_user.id,
                        text=f"{feedback_message}\n\n"
                             f"📋 **Informações:**\n"
                             f"• Ação: {action_name.title()}\n"
                             f"• Tempo: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                             f"• Motivo: Violação das diretrizes da comunidade\n\n"
                             f"💡 **Para dúvidas:**\n"
                             f"Use /ajuda para mais informações sobre nossas diretrizes.",
                        parse_mode='Markdown'
                    )
                except Exception:
                    # Se não puder enviar privado, usuário provavelmente bloqueou o bot
                    pass
            
        except Exception as e:
            self.logger.error(f"Erro na ação de bloqueio: {e}")
    
    async def _send_blocked_user_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Envia mensagem para usuário já bloqueado"""
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
            
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🚫 *Este usuário está temporariamente restrito*",
                parse_mode='Markdown'
            )
            
            # Remover após 5 segundos
            asyncio.create_task(self._schedule_message_deletion(
                context, update.effective_chat.id, message.message_id, 5
            ))
            
        except Exception as e:
            self.logger.error(f"Erro ao lidar com usuário bloqueado: {e}")
    
    def _filter_content(self, content: str, flagged_words: list) -> str:
        """Filtra conteúdo removendo palavras flagradas"""
        filtered = content
        
        for word in flagged_words:
            # Substituir palavra por asteriscos mantendo primeira e última letra
            if len(word) > 2:
                replacement = word[0] + '*' * (len(word) - 2) + word[-1]
            else:
                replacement = '*' * len(word)
            
            # Substituição case-insensitive
            import re
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            filtered = pattern.sub(replacement, filtered)
        
        return filtered
    
    async def _schedule_message_deletion(self, context: ContextTypes.DEFAULT_TYPE, 
                                       chat_id: int, message_id: int = None, delay: int = 30):
        """Agenda remoção de mensagem após delay"""
        await asyncio.sleep(delay)
        
        try:
            if message_id:
                await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            # Mensagem pode já ter sido deletada ou não existir
            pass
    
    def get_stats(self) -> Dict[str, int]:
        """Retorna estatísticas do middleware"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reseta estatísticas"""
        self.stats = {
            'messages_checked': 0,
            'messages_blocked': 0,
            'messages_warned': 0,
            'messages_filtered': 0
        }
        
        self.logger.info("Estatísticas do middleware resetadas")


class TelegramModerationHandler(BaseHandler):
    """Handler personalizado para integrar moderação com python-telegram-bot"""
    
    def __init__(self, middleware: ModerationMiddleware):
        super().__init__(self.callback)
        self.middleware = middleware
    
    def check_update(self, update: Update) -> bool:
        """Verifica se update deve ser processado"""
        return update.message is not None and update.message.text is not None
    
    async def callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Callback do handler - retorna True se mensagem pode prosseguir"""
        return await self.middleware.check_message(update, context)


# Função conveniente para criar e configurar middleware
def create_moderation_middleware(admin_ids=None) -> ModerationMiddleware:
    """
    Cria e configura middleware de moderação
    
    Args:
        admin_ids: Lista de IDs de usuários administradores
        
    Returns:
        ModerationMiddleware configurado
    """
    middleware = ModerationMiddleware(bypass_admin_ids=admin_ids)
    return middleware


# Exemplo de uso com o bot
if __name__ == "__main__":
    print("🛡️ MIDDLEWARE DE MODERAÇÃO - TELEGRAM")
    print("=" * 50)
    
    # Criar middleware
    middleware = create_moderation_middleware(admin_ids=[123456789])  # ID do admin
    
    # Simulação de uso
    print("✅ Middleware criado")
    print(f"   Moderação ativa: {middleware.enabled}")
    print(f"   Admins bypass: {len(middleware.bypass_admin_ids)}")
    
    print("\n📊 Estatísticas:")
    stats = middleware.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n💡 Para usar no bot:")
    print("   from src.telegram_moderation_middleware import create_moderation_middleware")
    print("   middleware = create_moderation_middleware([ADMIN_ID])")
    print("   # Integrar com handlers do bot...")