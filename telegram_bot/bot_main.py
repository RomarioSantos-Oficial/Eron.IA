"""
Bot Telegram Principal - Sistema Completo Reorganizado
"""
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

class TelegramBot:
    """Classe principal do bot Telegram organizado"""
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN não encontrado nas variáveis de ambiente")
        
        self.application = None
        self.setup_application()
    
    def setup_application(self):
        """Configurar aplicação do bot"""
        self.application = Application.builder().token(self.token).build()
        self.register_all_handlers()
    
    def register_all_handlers(self):
        """Registrar todos os handlers do bot"""
        
        # Importar handlers dos módulos organizados
        try:
            from telegram_bot.handlers.command_handlers import start, help_command, menu_command, clear_command
            from telegram_bot.handlers.message_handlers import handle_message
            from telegram_bot.handlers.callback_handlers import handle_callback_query
            from telegram_bot.handlers.personalization_handlers import start_personalization_menu
            from telegram_bot.handlers.preferences_handlers import show_preferences_menu
            from telegram_bot.handlers.emotions_handlers import show_emotions_menu
            from telegram_bot.handlers.adult_handlers import (
                start_adult_activation, handle_adult_callbacks,
                show_adult_config_menu, show_adult_status
            )
            from telegram_bot.handlers.age_verification import (
                age_verification_command, age_callback_handler, adult_status_command
            )
        except ImportError as e:
            logger.error(f"Erro ao importar handlers: {e}")
            # Handlers básicos em caso de falha
            def start(update, context): return update.message.reply_text("🤖 Eron.IA Bot Ativo!")
            def help_command(update, context): return update.message.reply_text("📚 Ajuda em construção...")
            def menu_command(update, context): return update.message.reply_text("📋 Menu em construção...")
            def clear_command(update, context): return update.message.reply_text("🧹 Chat limpo!")
            def handle_message(update, context): return update.message.reply_text("💬 Mensagem recebida!")
            def handle_callback_query(update, context): return update.callback_query.answer("✅ OK")
            def start_personalization_menu(update, context): return update.message.reply_text("⚙️ Personalização em construção...")
            def show_preferences_menu(update, context): return update.message.reply_text("🎛️ Preferências em construção...")
            def show_emotions_menu(update, context): return update.message.reply_text("😊 Emoções em construção...")
            def start_adult_activation(update, context): return update.message.reply_text("🔞 Sistema adulto em construção...")
            def handle_adult_callbacks(update, context): return update.callback_query.answer("🔞 OK")
            def show_adult_config_menu(update, context): return update.message.reply_text("⚙️ Config adulto em construção...")
            def show_adult_status(update, context): return update.message.reply_text("📊 Status adulto em construção...")
            def age_verification_command(update, context): return update.message.reply_text("🆔 Verificação em construção...")
            def age_callback_handler(update, context): return update.callback_query.answer("🆔 OK")
            def adult_status_command(update, context): return update.message.reply_text("📊 Status em construção...")
        
        # Registrar handlers de comandos básicos
        self.application.add_handler(CommandHandler("start", start))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("menu", menu_command))
        self.application.add_handler(CommandHandler("clear", clear_command))
        self.application.add_handler(CommandHandler("clean", clear_command))  # Sinônimo
        
        # Registrar comandos de personalização
        self.application.add_handler(CommandHandler("personalizar", start_personalization_menu))
        self.application.add_handler(CommandHandler("preferencias", show_preferences_menu))
        self.application.add_handler(CommandHandler("emocoes", show_emotions_menu))
        
        # Registrar comandos de verificação de idade
        self.application.add_handler(CommandHandler("idade", age_verification_command))
        self.application.add_handler(CommandHandler("adulto", adult_status_command))
        
        # Registrar comandos adultos
        self.application.add_handler(CommandHandler("adult_mode", start_adult_activation))
        self.application.add_handler(CommandHandler("adult_config", show_adult_config_menu))
        self.application.add_handler(CommandHandler("adult_status", show_adult_status))
        
        # Sistema Adulto Avançado - INTEGRAÇÃO COMPLETA
        try:
            from telegram_bot.handlers.advanced_adult_handlers import advanced_adult_handlers
            for handler in advanced_adult_handlers:
                self.application.add_handler(handler)
            logger.info("✅ Sistema adulto avançado integrado com sucesso!")
        except ImportError as e:
            logger.error(f"⚠️ Erro ao carregar sistema adulto avançado: {e}")
        except Exception as e:
            logger.error(f"⚠️ Erro inesperado no sistema adulto avançado: {e}")
        
        # Registrar handlers de callback (ordem importa!)
        self.application.add_handler(CallbackQueryHandler(age_callback_handler, pattern='^age_.*'))
        self.application.add_handler(CallbackQueryHandler(handle_adult_callbacks, pattern='^adult_.*'))
        self.application.add_handler(CallbackQueryHandler(handle_callback_query))
        
        # Handler de mensagens (deve ficar por último)
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        logger.info("Handlers básicos foram registrados com sucesso")
        logger.info("Handlers adultos foram registrados com sucesso")
        
        logger.info("Todos os handlers foram registrados com sucesso")
    
    def run(self):
        """Executar o bot"""
        if not self.application:
            raise RuntimeError("Aplicação não foi configurada")
        
        logger.info("Iniciando bot Telegram...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    def stop(self):
        """Parar o bot"""
        if self.application:
            logger.info("Parando bot Telegram...")
            self.application.stop()

def create_telegram_bot():
    """Criar e configurar o bot Telegram (função de conveniência)"""
    return TelegramBot()

def run_bot():
    """Executar o bot (função de conveniência)"""
    bot = create_telegram_bot()
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot interrompido pelo usuário")
        bot.stop()
    except Exception as e:
        logger.error(f"Erro ao executar bot: {e}")
        raise

# Script principal para execução direta
if __name__ == '__main__':
    run_bot()
