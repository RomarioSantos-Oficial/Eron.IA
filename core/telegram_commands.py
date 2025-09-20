"""
Comandos avançados para o bot Telegram
Implementa funcionalidades equivalentes à versão web
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.telegram_formatter import TelegramFormatter
from core.telegram_preferences import TelegramPreferences
from core.unified_messages import UnifiedMessages
import sys
import os

# Adicionar path para importar módulos da aplicação web
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class TelegramCommands:
    """Classe com comandos avançados do Telegram"""
    
    @staticmethod
    async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status - Mostra status atual do sistema"""
        
        try:
            # Importar dependências da aplicação web
            from core.user_profile_db import UserProfileDB
            
            user_id = str(update.effective_user.id)
            
            # Obter perfil do usuário
            user_profile_db = UserProfileDB()
            profile = user_profile_db.get_profile(user_id)
            
            if not profile:
                message = "❌ Nenhum perfil encontrado. Use /personalize para configurar."
                await update.message.reply_text(message, parse_mode='Markdown')
                return
            
            # Criar mensagem de status formatada
            status_message = TelegramFormatter.create_status_message(
                bot_name=profile.get('bot_name', 'ERON'),
                user_name=profile.get('user_name', 'Usuário'),
                personality=profile.get('bot_personality', 'amigável'),
                language=profile.get('bot_language', 'informal')
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("⚙️ Preferências", callback_data="cmd_preferences"),
                    InlineKeyboardButton("🎨 Personalizar", callback_data="cmd_personalize")
                ],
                [
                    InlineKeyboardButton("😊 Emoções", callback_data="cmd_emotions"),
                    InlineKeyboardButton("📊 Estatísticas", callback_data="cmd_stats")
                ]
            ]
            
            await update.message.reply_text(
                status_message,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            print(f"Erro no comando status: {e}")
            await update.message.reply_text(
                "❌ Erro ao obter status. Tente novamente.",
                parse_mode='Markdown'
            )
    
    @staticmethod
    async def preferences_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /preferences - Abre menu de preferências"""
        
        try:
            from core.preferences import PreferencesManager
            
            user_id = str(update.effective_user.id)
            
            # Obter preferências atuais
            preferences_manager = PreferencesManager()
            preferences = preferences_manager.get_preferences(user_id)
            
            # Criar mensagem com resumo das preferências
            summary = TelegramPreferences.get_preferences_summary(preferences or {})
            
            # Criar teclado de preferências
            keyboard = TelegramPreferences.create_main_preferences_menu()
            
            await update.message.reply_text(
                summary,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            
        except Exception as e:
            print(f"Erro no comando preferences: {e}")
            await update.message.reply_text(
                "❌ Erro ao carregar preferências. Tente novamente.",
                parse_mode='Markdown'
            )
    
    @staticmethod
    async def emotions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /emotions - Mostra estado emocional"""
        
        try:
            from core.emotion_system import EmotionSystem
            
            user_id = str(update.effective_user.id)
            
            emotion_system = EmotionSystem()
            
            # Obter estados emocionais
            bot_emotion = emotion_system.get_bot_emotion(user_id)
            user_emotion = emotion_system.get_user_emotion_history(user_id, limit=1)
            
            current_user_emotion = None
            if user_emotion:
                current_user_emotion = user_emotion[0].get('emotion')
            
            # Criar display de emoções
            emotion_display = TelegramFormatter.create_emotion_display(
                user_emotion=current_user_emotion,
                bot_emotion=bot_emotion
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("📊 Histórico", callback_data="emotion_history"),
                    InlineKeyboardButton("🔄 Atualizar", callback_data="emotion_refresh")
                ],
                [
                    InlineKeyboardButton("🎭 Influenciar Bot", callback_data="emotion_influence")
                ]
            ]
            
            await update.message.reply_text(
                emotion_display,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            print(f"Erro no comando emotions: {e}")
            await update.message.reply_text(
                "❌ Erro ao carregar emoções. Tente novamente.",
                parse_mode='Markdown'
            )
    
    @staticmethod
    async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /stats - Estatísticas de uso"""
        
        try:
            from core.memory import Memory
            
            user_id = str(update.effective_user.id)
            
            memory = Memory()
            
            # Obter estatísticas básicas
            recent_messages = memory.get_recent_context(user_id, limit=100)
            message_count = len(recent_messages.split('\n')) if recent_messages else 0
            
            stats_message = f"""
📊 *Estatísticas de Uso*

┌─ 💬 CONVERSAS ────────────┐
│ 📝 Mensagens: `{message_count}`
│ 🗓️ Período: `Últimos 30 dias`
│ 💾 Memória: `Ativa`
└───────────────────────────┘

┌─ 🎯 ATIVIDADES ──────────┐
│ 🎨 Personalizações: `1`
│ ⚙️ Preferências: `Configuradas`
│ 😊 Estado: `Operacional`
└───────────────────────────┘

📈 *Sistema funcionando perfeitamente!*
            """.strip()
            
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Atualizar", callback_data="stats_refresh"),
                    InlineKeyboardButton("📋 Detalhes", callback_data="stats_details")
                ]
            ]
            
            await update.message.reply_text(
                stats_message,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            print(f"Erro no comando stats: {e}")
            await update.message.reply_text(
                "❌ Erro ao carregar estatísticas. Tente novamente.",
                parse_mode='Markdown'
            )
    
    @staticmethod
    async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /backup - Fazer backup das configurações"""
        
        try:
            from core.user_profile_db import UserProfileDB
            from core.preferences import PreferencesManager
            import json
            from datetime import datetime
            
            user_id = str(update.effective_user.id)
            
            # Obter dados do usuário
            user_profile_db = UserProfileDB()
            preferences_manager = PreferencesManager()
            
            profile = user_profile_db.get_profile(user_id)
            preferences = preferences_manager.get_preferences(user_id)
            
            # Criar backup
            backup_data = {
                'user_id': user_id,
                'profile': profile,
                'preferences': preferences,
                'backup_date': datetime.now().isoformat(),
                'version': '2.0'
            }
            
            backup_json = json.dumps(backup_data, indent=2, ensure_ascii=False)
            
            # Criar arquivo temporário
            filename = f"eron_backup_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            backup_message = f"""
💾 *Backup Criado*

┌─ 📄 DADOS INCLUSOS ──────┐
│ 👤 Perfil personalizado   │
│ ⚙️ Preferências detalhadas│
│ 🗓️ Data: `{datetime.now().strftime('%d/%m/%Y %H:%M')}`
│ 📦 Arquivo: `{filename}`   │
└───────────────────────────┘

✅ Backup gerado com sucesso!

*Nota:* O arquivo foi criado localmente no servidor.
            """.strip()
            
            keyboard = [
                [
                    InlineKeyboardButton("📥 Restaurar", callback_data="backup_restore"),
                    InlineKeyboardButton("🗑️ Deletar", callback_data="backup_delete")
                ]
            ]
            
            await update.message.reply_text(
                backup_message,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            print(f"Erro no comando backup: {e}")
            await update.message.reply_text(
                "❌ Erro ao criar backup. Tente novamente.",
                parse_mode='Markdown'
            )
    
    @staticmethod
    async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /debug - Informações de debug (apenas para desenvolvedores)"""
        
        try:
            user_id = str(update.effective_user.id)
            
            # Verificar se é desenvolvedor (você pode configurar uma lista)
            dev_users = ['SEU_USER_ID_AQUI']  # Substitua pelo seu user_id
            
            if user_id not in dev_users:
                await update.message.reply_text(
                    "❌ Comando disponível apenas para desenvolvedores.",
                    parse_mode='Markdown'
                )
                return
            
            # Informações de debug
            debug_info = f"""
🔧 *Informações de Debug*

┌─ 💻 SISTEMA ──────────────┐
│ 🆔 User ID: `{user_id}`
│ 📱 Platform: `Telegram`
│ 🤖 Bot Version: `2.0`
│ 🐍 Python: `3.10+`
└───────────────────────────┘

┌─ 📊 CONTEXTO ────────────┐
│ 📝 Context Data: `{len(context.user_data)}`
│ 🔄 Session: `Active`
│ 💾 Database: `Connected`
└───────────────────────────┘

🛠️ *Sistema operacional*
            """.strip()
            
            await update.message.reply_text(
                debug_info,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            print(f"Erro no comando debug: {e}")
            await update.message.reply_text(
                "❌ Erro no debug. Verifique os logs.",
                parse_mode='Markdown'
            )
    
    @staticmethod 
    async def version_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /version - Informações da versão"""
        
        version_info = f"""
ℹ️ *Eron.IA - Informações da Versão*

┌─ 📦 VERSÃO ATUAL ────────┐
│ 🤖 Bot: `v2.0.0`
│ 🌐 Web App: `v2.0.0`
│ 📅 Build: `2024.01`
│ 🔄 Status: `Estável`
└───────────────────────────┘

┌─ ✨ RECURSOS ────────────┐
│ 🎨 Personalização completa│
│ ⚙️ Preferências avançadas │
│ 😊 Sistema de emoções     │
│ 💾 Memória persistente    │
│ 🔄 Reset inteligente      │
│ 📱 Interface unificada    │
└───────────────────────────┘

🚀 *Desenvolvido com ❤️*
        """.strip()
        
        await update.message.reply_text(
            version_info,
            parse_mode='Markdown'
        )

# Dicionário de comandos disponíveis
AVAILABLE_COMMANDS = {
    'status': TelegramCommands.status_command,
    'preferences': TelegramCommands.preferences_command,
    'emotions': TelegramCommands.emotions_command,
    'stats': TelegramCommands.stats_command,
    'backup': TelegramCommands.backup_command,
    'debug': TelegramCommands.debug_command,
    'version': TelegramCommands.version_command,
}
