#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 ERON.IA TELEGRAM BOT - LAUNCHER SIMPLIFICADO
Sistema completo funcionando sem dependências complexas
"""

import os
import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

class EronTelegramBot:
    """Bot Telegram Simplificado do Eron.IA"""
    
    def __init__(self):
        """Inicializar bot"""
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            print("❌ Token do Telegram não encontrado no .env")
            sys.exit(1)
        
        # Tentar importar módulos opcionais
        try:
            # Adicionar diretório raiz ao path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            sys.path.insert(0, parent_dir)
            
            from src.memory import EronMemory
            from src.emotion_system import EmotionSystem
            from src.user_profile_db import UserProfileDB
            
            self.memory = EronMemory()
            self.emotion_system = EmotionSystem()
            self.user_db = UserProfileDB()
            print("✅ Módulos avançados carregados")
            
        except ImportError as e:
            print(f"⚠️ Alguns módulos não disponíveis: {e}")
            self.memory = None
            self.emotion_system = None
            self.user_db = None
            print("✅ Executando em modo básico")
        
        # Criar aplicação
        self.application = ApplicationBuilder().token(self.token).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Configurar handlers básicos"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("adult_mode", self.adult_mode_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        user = update.effective_user
        welcome_message = f"""
🤖 **Olá {user.first_name}! Eu sou o Eron.IA**

🎯 **Sistema Unificado Web + Telegram**
- 🌐 Interface Web: http://localhost:5000
- 📱 Telegram: Você está aqui!

📋 **Comandos disponíveis:**
/help - Ajuda e comandos
/status - Status do sistema
/adult_mode - Sistema adulto (18+)

💬 **Como usar:**
- Digite qualquer mensagem para conversar
- Use os comandos acima para funcionalidades especiais

✨ **Recursos:**
- Chat inteligente
- Sistema de personalidades
- Treinamento de vocabulário
- Interface web integrada

Digite qualquer coisa para começar nossa conversa! 🚀
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        help_text = """
📚 **AJUDA - ERON.IA BOT**

🔧 **Comandos Básicos:**
/start - Inicializar bot
/help - Esta mensagem de ajuda
/status - Status do sistema

🔞 **Sistema Adulto (18+):**
/adult_mode - Ativar modo adulto
/adult_config - Configurações adultas
/adult_train - Treinamento de vocabulário
/adult_status - Status do modo adulto

🌐 **Interface Web:**
- Acesse: http://localhost:5000
- Login/Registro disponível
- Dashboard completo
- Sistema adulto web

💬 **Chat:**
- Digite qualquer mensagem
- Conversa natural com IA
- Respostas contextuais

🎯 **Recursos Especiais:**
- Personalidades múltiplas
- Sistema emocional
- Memória persistente
- Treinamento adaptativo

⚠️ **Importante:**
- Sistema adulto requer 18+ anos
- Dados protegidos e criptografados
- Funcionalidades normais para menores
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status"""
        user_id = str(update.effective_user.id)
        
        status_text = f"""
📊 **STATUS DO SISTEMA ERON.IA**

👤 **Usuário:** {update.effective_user.first_name}
🆔 **ID:** {user_id}

🤖 **Bot Status:** ✅ Online
🌐 **Web Interface:** Disponível
📱 **Telegram:** Ativo
🔄 **Sincronização:** Ativada

📚 **Módulos:**
        """
        
        if self.memory:
            status_text += "✅ Memória: Ativo\n"
        else:
            status_text += "⚠️ Memória: Modo básico\n"
            
        if self.emotion_system:
            status_text += "✅ Sistema emocional: Ativo\n"
        else:
            status_text += "⚠️ Sistema emocional: Modo básico\n"
            
        if self.user_db:
            status_text += "✅ Banco de usuários: Ativo\n"
        else:
            status_text += "⚠️ Banco de usuários: Modo básico\n"
        
        status_text += """
🔞 **Modo Adulto:** Use /adult_mode para verificar

🚀 **Sistema funcionando normalmente!**
        """
        
        await update.message.reply_text(status_text, parse_mode='Markdown')

    async def adult_mode_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /adult_mode"""
        user_id = str(update.effective_user.id)
        
        try:
            # Tentar verificar modo adulto avançado
            from telegram_bot.handlers.adult_integration import is_advanced_adult_active
            adult_active = is_advanced_adult_active(user_id)
            
            if adult_active:
                message = "🌶️ **MODO ADULTO ATIVO**\n\nSistema avançado funcionando!\nUse /adult_config para configurações."
            else:
                message = """
🔞 **SISTEMA ADULTO DISPONÍVEL**

⚠️ **Requisitos:**
- Idade mínima: 18 anos
- Verificação obrigatória
- Consentimento explícito

📱 **Comandos:**
/adult_config - Configurações
/adult_train - Treinamento
/adult_status - Status detalhado

🌐 **Interface Web:**
Acesse /adult/ nas rotas web para configuração completa.

⚡ **Ativação:**
Use os comandos acima para configurar o sistema adulto.
                """
                
        except ImportError:
            message = """
🔞 **SISTEMA ADULTO - MODO BÁSICO**

⚠️ Para funcionalidade completa:
- Execute o sistema web: python app.py
- Acesse: http://localhost:5000/adult/
- Configure idade e preferências

📱 **Telegram:**
Recursos básicos disponíveis.
            """
        
        await update.message.reply_text(message, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lidar com mensagens de texto"""
        user_message = update.message.text
        user_id = str(update.effective_user.id)
        user_name = update.effective_user.first_name
        
        # Verificar modo adulto e aplicar emoji se necessário
        try:
            from telegram_bot.handlers.adult_integration import is_advanced_adult_active
            adult_active = is_advanced_adult_active(user_id)
            adult_indicator = "🌶️ " if adult_active else ""
        except ImportError:
            adult_indicator = ""
        
        # Resposta básica (pode ser substituída por IA mais avançada)
        if "olá" in user_message.lower() or "oi" in user_message.lower():
            response = f"Olá {user_name}! Como posso ajudá-lo hoje?"
        elif "como você está" in user_message.lower():
            response = "Estou funcionando perfeitamente! Pronto para conversar com você."
        elif "obrigado" in user_message.lower():
            response = "De nada! Sempre à disposição para ajudar."
        else:
            response = f"Entendi sua mensagem: '{user_message}'. Como um sistema de IA, estou aqui para conversar e ajudar!"
        
        # Aplicar indicador adulto se necessário
        final_response = adult_indicator + response
        
        await update.message.reply_text(final_response)

    def run(self):
        """Executar bot"""
        print("🚀 INICIANDO ERON.IA TELEGRAM BOT")
        print("=" * 40)
        print("✅ Bot configurado e pronto!")
        print("📱 Aguardando mensagens...")
        print("🛑 Pressione Ctrl+C para parar")
        print("=" * 40)
        
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Função principal"""
    try:
        bot = EronTelegramBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar bot: {e}")

if __name__ == "__main__":
    main()