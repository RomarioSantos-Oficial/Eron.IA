"""
Bot Telegram com Moderação Integrada - Exemplo Prático
======================================================

Exemplo completo de como integrar o sistema de moderação
com seu bot do Telegram existente.

Funcionalidades:
- ✅ Moderação automática de conteúdo
- ✅ Comandos administrativos
- ✅ Relatórios em tempo real
- ✅ Configuração flexível por grupo
- ✅ Sistema de bypass para admins

Requisitos:
- python-telegram-bot
- Sistema de moderação Eron.IA

Uso:
1. Configure TOKEN_BOT no .env
2. Defina ADMIN_IDS 
3. Execute: python examples/moderated_telegram_bot.py

Autor: Eron.IA System
"""

import logging
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Adicionar diretório pai para imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    from telegram.constants import ParseMode
except ImportError:
    print("❌ Instale python-telegram-bot: pip install python-telegram-bot")
    sys.exit(1)

try:
    from src.telegram_moderation_middleware import create_moderation_middleware, TelegramModerationHandler
    from src.adult_content_moderator import get_moderation_stats, is_user_blocked
    from tools.moderation_manager import ModerationManager
    from core.config import config
except ImportError as e:
    print(f"❌ Erro ao importar sistema de moderação: {e}")
    sys.exit(1)

# ============================================================================
# CONFIGURAÇÕES DO BOT
# ============================================================================

# Token do bot (configurar no .env ou aqui)
TOKEN = os.getenv('TOKEN_BOT') or "SEU_TOKEN_AQUI"

# IDs dos administradores (IMPORTANTE: Configure seus IDs reais!)
ADMIN_IDS = [
    123456789,    # Substitua pelo seu ID
    987654321,    # Substitua por outros admins
]

# Configurações por grupo (opcional)
GROUP_CONFIGS = {
    # Exemplo: ID_DO_GRUPO: configuração
    -1001234567890: {
        'sensitivity': 'high',
        'auto_filter': True,
        'admin_notifications': True,
        'welcome_message': True
    }
}

# ============================================================================
# CLASSE PRINCIPAL DO BOT
# ============================================================================

class ModeratedTelegramBot:
    """Bot Telegram com sistema de moderação integrado"""
    
    def __init__(self, token: str, admin_ids: list):
        self.token = token
        self.admin_ids = set(admin_ids)
        self.app = None
        self.moderation_middleware = None
        self.manager = ModerationManager()
        self.start_time = datetime.now()
        
        # Configurar logging
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_moderation(self):
        """Configurar sistema de moderação"""
        self.logger.info("Configurando sistema de moderação...")
        
        # Criar middleware de moderação
        self.moderation_middleware = create_moderation_middleware(
            admin_ids=list(self.admin_ids)
        )
        
        self.logger.info(f"Moderação configurada para {len(self.admin_ids)} administradores")
    
    def is_admin(self, user_id: int) -> bool:
        """Verificar se usuário é administrador"""
        return user_id in self.admin_ids
    
    # ========================================================================
    # HANDLERS DE MENSAGENS COM MODERAÇÃO INTEGRADA
    # ========================================================================
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler principal para mensagens de texto com moderação"""
        
        # 1. VERIFICAÇÃO DE MODERAÇÃO PRIMEIRO
        if self.moderation_middleware:
            can_proceed = await self.moderation_middleware.check_message(update, context)
            if not can_proceed:
                # Mensagem foi bloqueada/filtrada pela moderação
                return
        
        # 2. PROCESSAR MENSAGEM NORMALMENTE
        user = update.effective_user
        message = update.message.text
        chat_id = update.effective_chat.id
        
        # Log da mensagem (opcional)
        self.logger.info(f"Mensagem de {user.first_name} ({user.id}): {message[:50]}...")
        
        # 3. LÓGICA DO BOT (substitua pela sua)
        
        # Exemplo: resposta simples
        response = f"👋 Olá {user.first_name}!\n\n"
        response += f"Recebi sua mensagem: _{message[:100]}_\n\n"
        response += f"🤖 Sou o Eron.IA com moderação integrada!"
        
        try:
            await update.message.reply_text(
                response,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            self.logger.error(f"Erro ao enviar resposta: {e}")
            await update.message.reply_text("Desculpe, houve um erro ao processar sua mensagem.")
    
    # ========================================================================
    # COMANDOS BÁSICOS DO BOT
    # ========================================================================
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        user = update.effective_user
        welcome_msg = f"""
🚀 **Bem-vindo ao Eron.IA Bot!**

👋 Olá {user.first_name}!

🛡️ **Sistema de Moderação Ativo**
Este bot possui moderação automática de conteúdo para manter um ambiente seguro e respeitoso.

📖 **Comandos disponíveis:**
/help - Ajuda e informações
/status - Status do sistema

👨‍💻 **Comandos administrativos:** (apenas para admins)
/modstats - Estatísticas de moderação
/checkuser <id> - Verificar usuário
/unblock <id> - Desbloquear usuário

Envie qualquer mensagem para começar a conversar!
"""
        
        await update.message.reply_text(welcome_msg, parse_mode=ParseMode.MARKDOWN)
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        help_text = """
📖 **AJUDA - Eron.IA Bot**

🤖 **Sobre o Bot:**
Sou um assistente com sistema de moderação integrado para manter conversas seguras e respeitosas.

💬 **Como usar:**
• Envie mensagens normalmente
• O sistema verifica automaticamente o conteúdo
• Mensagens inadequadas são filtradas automaticamente

🛡️ **Sistema de Moderação:**
• ✅ Conteúdo apropriado - permitido
• ⚠️ Conteúdo questionável - aviso
• 🚫 Conteúdo inadequado - bloqueado
• 📊 Estatísticas para administradores

❓ **Problemas?**
Entre em contato com os administradores.
"""
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status - Status do sistema"""
        uptime = datetime.now() - self.start_time
        uptime_str = str(uptime).split('.')[0]  # Remove microssegundos
        
        status_msg = f"""
📊 **STATUS DO SISTEMA**

🤖 **Bot:** Ativo e funcionando
🛡️ **Moderação:** {'✅ Ativa' if config.moderation['enabled'] else '❌ Desativa'}
⏰ **Uptime:** {uptime_str}
👥 **Administradores:** {len(self.admin_ids)}

🔧 **Configurações:**
• Sensibilidade: {config.moderation.get('sensitivity', 'medium')}
• Filtro automático: {'✅' if config.moderation.get('auto_filter', True) else '❌'}
• Avisos automáticos: {'✅' if config.moderation.get('auto_warn', True) else '❌'}
"""
        
        await update.message.reply_text(status_msg, parse_mode=ParseMode.MARKDOWN)
    
    # ========================================================================
    # COMANDOS ADMINISTRATIVOS
    # ========================================================================
    
    async def cmd_modstats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /modstats - Estatísticas de moderação (apenas admins)"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Comando disponível apenas para administradores")
            return
        
        try:
            # Obter estatísticas dos últimos 7 dias
            stats = get_moderation_stats(days=7)
            
            current = stats['current_stats']
            
            stats_msg = f"""
📊 **ESTATÍSTICAS DE MODERAÇÃO**

📈 **Hoje:**
• Verificações: {current['total_checks_today']:,}
• Bloqueios: {current['blocks_today']:,}
• Avisos: {current['warnings_today']:,}

📋 **Últimos 7 dias - Por tipo:**
"""
            
            # Adicionar estatísticas por ação
            if stats['action_stats']:
                for action, count in sorted(stats['action_stats'].items(), key=lambda x: x[1], reverse=True)[:5]:
                    severity, action_type = action.split('_', 1)
                    stats_msg += f"• {severity.title()} - {action_type.title()}: {count:,}\n"
            else:
                stats_msg += "• Nenhuma ação registrada\n"
            
            # Top violadores
            stats_msg += f"\n🚨 **Top Violadores:**\n"
            if stats['top_violators']:
                for i, violator in enumerate(stats['top_violators'][:3], 1):
                    stats_msg += f"{i}. User {violator['user_id']}: {violator['violations']} violações\n"
            else:
                stats_msg += "• Nenhum violador registrado\n"
            
            await update.message.reply_text(stats_msg, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            await update.message.reply_text("❌ Erro ao obter estatísticas de moderação")
    
    async def cmd_checkuser(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /checkuser USER_ID - Verificar status de usuário (apenas admins)"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Comando disponível apenas para administradores")
            return
        
        if not context.args:
            await update.message.reply_text("Uso: /checkuser USER_ID")
            return
        
        try:
            user_id = int(context.args[0])
            blocked = is_user_blocked(user_id)
            
            status_icon = "🚫" if blocked else "✅"
            status_text = "Bloqueado" if blocked else "Ativo"
            
            check_msg = f"👤 **Status do Usuário {user_id}:**\n{status_icon} {status_text}"
            
            await update.message.reply_text(check_msg, parse_mode=ParseMode.MARKDOWN)
            
        except ValueError:
            await update.message.reply_text("❌ ID de usuário inválido")
        except Exception as e:
            self.logger.error(f"Erro ao verificar usuário: {e}")
            await update.message.reply_text("❌ Erro ao verificar usuário")
    
    async def cmd_unblock(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /unblock USER_ID - Desbloquear usuário (apenas admins)"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Comando disponível apenas para administradores")
            return
        
        if not context.args:
            await update.message.reply_text("Uso: /unblock USER_ID")
            return
        
        try:
            user_id = context.args[0]
            
            # Usar ModerationManager para desbloquear
            self.manager.unblock_user(user_id)
            
            await update.message.reply_text(f"✅ Usuário {user_id} foi desbloqueado")
            
        except Exception as e:
            self.logger.error(f"Erro ao desbloquear usuário: {e}")
            await update.message.reply_text("❌ Erro ao desbloquear usuário")
    
    # ========================================================================
    # CONFIGURAÇÃO E EXECUÇÃO DO BOT
    # ========================================================================
    
    def setup_handlers(self):
        """Configurar todos os handlers do bot"""
        self.logger.info("Configurando handlers...")
        
        # Comandos básicos
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("status", self.cmd_status))
        
        # Comandos administrativos  
        self.app.add_handler(CommandHandler("modstats", self.cmd_modstats))
        self.app.add_handler(CommandHandler("checkuser", self.cmd_checkuser))
        self.app.add_handler(CommandHandler("unblock", self.cmd_unblock))
        
        # Handler de mensagens (COM MODERAÇÃO INTEGRADA)
        # IMPORTANTE: Este handler deve vir DEPOIS dos comandos
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_text_message
        ))
        
        self.logger.info("Handlers configurados com sucesso")
    
    async def run(self):
        """Iniciar o bot"""
        self.logger.info("Iniciando bot Telegram com moderação...")
        
        # Criar aplicação
        self.app = Application.builder().token(self.token).build()
        
        # Configurar moderação
        self.setup_moderation()
        
        # Configurar handlers
        self.setup_handlers()
        
        # Inicializar e executar
        self.logger.info("Bot configurado, iniciando polling...")
        await self.app.initialize()
        await self.app.start()
        
        print(f"""
🚀 BOT INICIADO COM SUCESSO!

🤖 **Bot:** @{(await self.app.bot.get_me()).username}
🛡️ **Moderação:** {'Ativa' if config.moderation['enabled'] else 'Inativa'}  
👨‍💻 **Administradores:** {len(self.admin_ids)}

📊 **Funcionalidades ativas:**
✅ Moderação automática de conteúdo
✅ Comandos administrativos
✅ Sistema de bloqueio/desbloqueio
✅ Estatísticas em tempo real

🔧 **Comandos administrativos:**
/modstats - Estatísticas
/checkuser <id> - Verificar usuário  
/unblock <id> - Desbloquear usuário

Pressione Ctrl+C para parar o bot.
""")
        
        # Manter bot rodando
        await self.app.updater.start_polling()
        
        # Aguardar até ser interrompido
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            self.logger.info("Parando bot...")
        finally:
            await self.app.stop()


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

async def main():
    """Função principal - inicia o bot"""
    
    # Verificar configurações
    if TOKEN == "SEU_TOKEN_AQUI":
        print("❌ Configure o TOKEN do bot no .env ou no código")
        return
    
    if 123456789 in ADMIN_IDS:
        print("⚠️ AVISO: Configure os IDs reais dos administradores!")
        print("   Substitua 123456789 pelo seu ID do Telegram")
    
    # Verificar sistema de moderação
    if not config.moderation['enabled']:
        print("⚠️ Sistema de moderação desabilitado!")
        print("   Configure ADULT_MODERATION_ENABLED=True no .env")
    
    # Criar e executar bot
    bot = ModeratedTelegramBot(TOKEN, ADMIN_IDS)
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        print("\n👋 Bot interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar bot: {e}")


if __name__ == "__main__":
    # Verificar dependências
    try:
        import telegram
        print(f"✅ python-telegram-bot versão: {telegram.__version__}")
    except ImportError:
        print("❌ Instale: pip install python-telegram-bot")
        sys.exit(1)
    
    # Executar bot
    asyncio.run(main())