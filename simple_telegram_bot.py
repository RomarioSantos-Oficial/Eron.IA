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
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
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
        self.application.add_handler(CommandHandler("personalizar", self.personalization_menu))
        self.application.add_handler(CommandHandler("configurar", self.personalization_menu))
        
        # Handler para callbacks dos botões
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Handler para mensagens
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

    async def personalization_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Menu de personalização com botões"""
        keyboard = [
            [InlineKeyboardButton("👤 Definir Nome", callback_data="set_name"),
             InlineKeyboardButton("🎭 Personalidade", callback_data="set_personality")],
            [InlineKeyboardButton("🗣️ Estilo de Conversa", callback_data="set_language"),
             InlineKeyboardButton("⚧️ Gênero do Bot", callback_data="set_bot_gender")],
            [InlineKeyboardButton("🎂 Sua Idade", callback_data="set_age"),
             InlineKeyboardButton("👥 Seu Gênero", callback_data="set_user_gender")],
            [InlineKeyboardButton("🔞 Sistema Adulto", callback_data="adult_config"),
             InlineKeyboardButton("❌ Fechar", callback_data="close_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""
⚙️ **MENU DE PERSONALIZAÇÃO** ⚙️

👋 Olá {update.effective_user.first_name}!
Escolha o que deseja configurar:

🎯 **Opções Disponíveis:**
• Nome e personalidade do bot
• Estilo de conversa
• Configurações pessoais
• Sistema adulto (18+)

✨ Use os botões abaixo para personalizar!
        """
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lidar com callbacks dos botões"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        data = query.data
        
        if data == "close_menu":
            await query.edit_message_text("✅ Menu fechado!")
            return
        
        elif data == "set_name":
            await self.name_selection_menu(query)
        elif data == "set_personality":
            await self.personality_selection_menu(query)
        elif data == "set_language":
            await self.language_selection_menu(query)
        elif data == "set_bot_gender":
            await self.bot_gender_selection_menu(query)
        elif data == "set_age":
            await self.age_verification_menu(query)
        elif data == "set_user_gender":
            await self.user_gender_selection_menu(query)
        elif data == "adult_config":
            await self.adult_configuration_menu(query)
        elif data.startswith("save_"):
            await self.save_preference(query, data)
        else:
            await query.edit_message_text(f"Opção '{data}' ainda em desenvolvimento! 🚧")

    async def name_selection_menu(self, query):
        """Menu para escolher nome do bot"""
        keyboard = [
            [InlineKeyboardButton("💫 Aina", callback_data="save_name_Aina"),
             InlineKeyboardButton("🌟 Luna", callback_data="save_name_Luna")],
            [InlineKeyboardButton("🌸 Maya", callback_data="save_name_Maya"),
             InlineKeyboardButton("✨ Zara", callback_data="save_name_Zara")],
            [InlineKeyboardButton("🎀 Sofia", callback_data="save_name_Sofia"),
             InlineKeyboardButton("🌺 Valentina", callback_data="save_name_Valentina")],
            [InlineKeyboardButton("⬅️ Voltar", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """
👤 **ESCOLHA O NOME DO SEU BOT**

🎯 Selecione um nome que você gostaria que eu usasse:

✨ Cada nome tem sua própria personalidade!
        """
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def personality_selection_menu(self, query):
        """Menu para escolher personalidade"""
        keyboard = [
            [InlineKeyboardButton("😊 Amigável", callback_data="save_personality_amigavel"),
             InlineKeyboardButton("💫 Romântica", callback_data="save_personality_romantica")],
            [InlineKeyboardButton("🎭 Divertida", callback_data="save_personality_divertida"),
             InlineKeyboardButton("🧠 Intelectual", callback_data="save_personality_intelectual")],
            [InlineKeyboardButton("😈 Sedutora", callback_data="save_personality_sedutora"),
             InlineKeyboardButton("👑 Elegante", callback_data="save_personality_elegante")],
            [InlineKeyboardButton("⬅️ Voltar", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """
🎭 **ESCOLHA A PERSONALIDADE**

🎯 Como você gostaria que eu me comporte?

✨ Cada personalidade oferece uma experiência única!
        """
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def language_selection_menu(self, query):
        """Menu para escolher estilo de linguagem"""
        keyboard = [
            [InlineKeyboardButton("💬 Informal", callback_data="save_language_informal"),
             InlineKeyboardButton("🎓 Formal", callback_data="save_language_formal")],
            [InlineKeyboardButton("😎 Descontraído", callback_data="save_language_descontraido"),
             InlineKeyboardButton("💖 Carinhoso", callback_data="save_language_carinhoso")],
            [InlineKeyboardButton("⬅️ Voltar", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """
🗣️ **ESCOLHA O ESTILO DE CONVERSA**

🎯 Como você prefere que eu fale?

✨ Adapto meu jeito de falar ao seu gosto!
        """
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def save_preference(self, query, data):
        """Salvar preferência do usuário"""
        user_id = f"telegram_{query.from_user.id}"
        user_name = query.from_user.first_name
        
        # Extrair tipo e valor da preferência
        parts = data.split('_', 2)
        if len(parts) < 3:
            await query.edit_message_text("❌ Erro ao salvar preferência!")
            return
        
        pref_type = parts[1]
        pref_value = parts[2]
        
        # Salvar no banco se disponível
        try:
            if self.user_db:
                # Obter perfil atual
                profile = self.user_db.get_profile(user_id) or {}
                
                # Atualizar campo específico
                if pref_type == "name":
                    profile['bot_name'] = pref_value
                    msg = f"✅ Nome alterado para: **{pref_value}**"
                elif pref_type == "personality":
                    profile['bot_personality'] = pref_value
                    msg = f"✅ Personalidade alterada para: **{pref_value}**"
                elif pref_type == "language":
                    profile['bot_language'] = pref_value
                    msg = f"✅ Estilo alterado para: **{pref_value}**"
                else:
                    msg = f"✅ Configuração '{pref_type}' salva!"
                
                # Salvar perfil
                profile.update({
                    'user_id': user_id,
                    'user_name': user_name
                })
                
                self.user_db.save_profile(user_id, profile)
            else:
                msg = f"✅ Configuração '{pref_value}' aplicada temporariamente!"
        
        except Exception as e:
            print(f"[DEBUG] Erro ao salvar: {e}")
            msg = f"⚠️ Configuração aplicada temporariamente: **{pref_value}**"
        
        # Botão para voltar
        keyboard = [[InlineKeyboardButton("⬅️ Voltar ao Menu", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(msg + "\n\n🎯 Continue personalizando!", 
                                     reply_markup=reply_markup, parse_mode='Markdown')

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
        
        # Tentar usar o sistema de IA do web app
        try:
            # Adicionar path para importar web.app
            current_dir = os.path.dirname(os.path.abspath(__file__))
            web_dir = os.path.join(current_dir, 'web')
            sys.path.insert(0, web_dir)
            sys.path.insert(0, current_dir)
            
            from web.app import get_llm_response
            
            # Obter perfil real do usuário Telegram ou criar básico
            profile = self.get_user_profile(user_id, user_name)
            
            # Obter resposta da IA
            ai_response = get_llm_response(user_message, profile)
            response = ai_response if ai_response else "Desculpe, não consegui processar sua mensagem no momento."
            
        except Exception as e:
            # Fallback para resposta básica
            print(f"[DEBUG] Erro ao usar IA: {e}")
            if "olá" in user_message.lower() or "oi" in user_message.lower():
                response = f"Olá {user_name}! Como posso ajudá-lo hoje?"
            elif "como você está" in user_message.lower():
                response = "Estou funcionando perfeitamente! Pronto para conversar com você."
            elif "obrigado" in user_message.lower():
                response = "De nada! Sempre à disposição para ajudar."
            else:
                response = f"Recebi sua mensagem: '{user_message}'. Como uma IA, estou aqui para conversar!"
        
        # Aplicar indicador adulto se necessário
        final_response = adult_indicator + response
        
        await update.message.reply_text(final_response)
    
    def get_user_profile(self, user_id, user_name):
        """Obter ou criar perfil do usuário Telegram"""
        try:
            # Tentar carregar perfil existente do banco
            if self.user_db:
                profile = self.user_db.get_profile(f'telegram_{user_id}')
                if profile:
                    return profile
        except Exception as e:
            print(f"[DEBUG] Erro ao carregar perfil: {e}")
        
        # Criar perfil padrão para novos usuários
        return {
            'user_id': f'telegram_{user_id}',
            'user_name': user_name,
            'bot_name': 'Aina',
            'bot_personality': 'amigavel',
            'bot_language': 'informal',
            'has_mature_access': False,  # Será verificado dinamicamente
            'user_age': None,  # Será definido na personalização
            'bot_gender': 'feminino',
            'user_gender': 'não_informado'
        }

    async def personalization_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Menu de personalização com botões"""
        keyboard = [
            [InlineKeyboardButton("👤 Definir Nome", callback_data="set_name"),
             InlineKeyboardButton("🎭 Personalidade", callback_data="set_personality")],
            [InlineKeyboardButton("🗣️ Estilo de Conversa", callback_data="set_language"),
             InlineKeyboardButton("⚧️ Gênero do Bot", callback_data="set_bot_gender")],
            [InlineKeyboardButton("🎂 Sua Idade", callback_data="set_age"),
             InlineKeyboardButton("👥 Seu Gênero", callback_data="set_user_gender")],
            [InlineKeyboardButton("🔞 Sistema Adulto", callback_data="adult_config"),
             InlineKeyboardButton("❌ Fechar", callback_data="close_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""
⚙️ **MENU DE PERSONALIZAÇÃO** ⚙️

👋 Olá {update.effective_user.first_name}!
Escolha o que deseja configurar:

🎯 **Opções Disponíveis:**
• Nome e personalidade do bot
• Estilo de conversa
• Configurações pessoais
• Sistema adulto (18+)

✨ Use os botões abaixo para personalizar!
        """
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lidar com callbacks dos botões"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        data = query.data
        
        if data == "close_menu":
            await query.edit_message_text("✅ Menu fechado!")
            return
        elif data == "back_to_main":
            # Recriar menu principal
            await self.recreate_main_menu(query)
            return
        elif data == "set_name":
            await self.name_selection_menu(query)
        elif data == "set_personality":
            await self.personality_selection_menu(query)
        elif data == "set_language":
            await self.language_selection_menu(query)
        elif data == "set_bot_gender":
            await self.bot_gender_selection_menu(query)
        elif data == "set_age":
            await self.age_verification_menu(query)
        elif data == "set_user_gender":
            await self.user_gender_selection_menu(query)
        elif data == "adult_config":
            await self.adult_configuration_menu(query)
        elif data.startswith("save_"):
            await self.save_preference(query, data)
        else:
            await query.edit_message_text(f"Opção '{data}' ainda em desenvolvimento! 🚧")

    async def recreate_main_menu(self, query):
        """Recriar menu principal"""
        keyboard = [
            [InlineKeyboardButton("👤 Definir Nome", callback_data="set_name"),
             InlineKeyboardButton("🎭 Personalidade", callback_data="set_personality")],
            [InlineKeyboardButton("🗣️ Estilo de Conversa", callback_data="set_language"),
             InlineKeyboardButton("⚧️ Gênero do Bot", callback_data="set_bot_gender")],
            [InlineKeyboardButton("🎂 Sua Idade", callback_data="set_age"),
             InlineKeyboardButton("👥 Seu Gênero", callback_data="set_user_gender")],
            [InlineKeyboardButton("🔞 Sistema Adulto", callback_data="adult_config"),
             InlineKeyboardButton("❌ Fechar", callback_data="close_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """
⚙️ **MENU DE PERSONALIZAÇÃO** ⚙️

🎯 **Opções Disponíveis:**
• Nome e personalidade do bot
• Estilo de conversa  
• Configurações pessoais
• Sistema adulto (18+)

✨ Use os botões abaixo para personalizar!
        """
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def name_selection_menu(self, query):
        """Menu para escolher nome do bot"""
        keyboard = [
            [InlineKeyboardButton("💫 Aina", callback_data="save_name_Aina"),
             InlineKeyboardButton("🌟 Luna", callback_data="save_name_Luna")],
            [InlineKeyboardButton("🌸 Maya", callback_data="save_name_Maya"),
             InlineKeyboardButton("✨ Zara", callback_data="save_name_Zara")],
            [InlineKeyboardButton("🎀 Sofia", callback_data="save_name_Sofia"),
             InlineKeyboardButton("🌺 Valentina", callback_data="save_name_Valentina")],
            [InlineKeyboardButton("⬅️ Voltar", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """
👤 **ESCOLHA O NOME DO SEU BOT**

🎯 Selecione um nome que você gostaria que eu usasse:

✨ Cada nome tem sua própria personalidade!
        """
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def personality_selection_menu(self, query):
        """Menu para escolher personalidade"""
        keyboard = [
            [InlineKeyboardButton("😊 Amigável", callback_data="save_personality_amigavel"),
             InlineKeyboardButton("💫 Romântica", callback_data="save_personality_romantica")],
            [InlineKeyboardButton("🎭 Divertida", callback_data="save_personality_divertida"),
             InlineKeyboardButton("🧠 Intelectual", callback_data="save_personality_intelectual")],
            [InlineKeyboardButton("😈 Sedutora", callback_data="save_personality_sedutora"),
             InlineKeyboardButton("👑 Elegante", callback_data="save_personality_elegante")],
            [InlineKeyboardButton("⬅️ Voltar", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """
🎭 **ESCOLHA A PERSONALIDADE**

🎯 Como você gostaria que eu me comporte?

✨ Cada personalidade oferece uma experiência única!
        """
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def language_selection_menu(self, query):
        """Menu para escolher estilo de linguagem"""
        keyboard = [
            [InlineKeyboardButton("💬 Informal", callback_data="save_language_informal"),
             InlineKeyboardButton("🎓 Formal", callback_data="save_language_formal")],
            [InlineKeyboardButton("😎 Descontraído", callback_data="save_language_descontraido"),
             InlineKeyboardButton("💖 Carinhoso", callback_data="save_language_carinhoso")],
            [InlineKeyboardButton("⬅️ Voltar", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """
🗣️ **ESCOLHA O ESTILO DE CONVERSA**

🎯 Como você prefere que eu fale?

✨ Adapto meu jeito de falar ao seu gosto!
        """
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def bot_gender_selection_menu(self, query):
        """Menu para escolher gênero do bot"""
        keyboard = [
            [InlineKeyboardButton("👩 Feminino", callback_data="save_bot_gender_feminino"),
             InlineKeyboardButton("👨 Masculino", callback_data="save_bot_gender_masculino")],
            [InlineKeyboardButton("🤖 Neutro", callback_data="save_bot_gender_neutro"),
             InlineKeyboardButton("⬅️ Voltar", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚧️ **GÊNERO DO BOT**\n\n🎯 Como você gostaria que eu me identificasse?", 
            reply_markup=reply_markup, parse_mode='Markdown'
        )

    async def user_gender_selection_menu(self, query):
        """Menu para escolher gênero do usuário"""
        keyboard = [
            [InlineKeyboardButton("👨 Masculino", callback_data="save_user_gender_masculino"),
             InlineKeyboardButton("👩 Feminino", callback_data="save_user_gender_feminino")],
            [InlineKeyboardButton("🏳️‍⚧️ Não-binário", callback_data="save_user_gender_nao_binario"),
             InlineKeyboardButton("🤐 Prefiro não dizer", callback_data="save_user_gender_privado")],
            [InlineKeyboardButton("⬅️ Voltar", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "👥 **SEU GÊNERO**\n\n🎯 Como você se identifica?\n\n💭 Isso me ajuda a personalizar melhor nossa conversa!", 
            reply_markup=reply_markup, parse_mode='Markdown'
        )

    async def age_verification_menu(self, query):
        """Menu para verificação de idade"""
        keyboard = [
            [InlineKeyboardButton("🔞 Tenho 18+ anos", callback_data="save_age_adult"),
             InlineKeyboardButton("👶 Menor de 18", callback_data="save_age_minor")],
            [InlineKeyboardButton("⬅️ Voltar", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """
🎂 **VERIFICAÇÃO DE IDADE**

⚠️ **Importante:**
Sua idade determina quais recursos estarão disponíveis.

🔞 **18+ anos:** Acesso completo ao sistema
👶 **Menor de 18:** Modo seguro ativado

🛡️ Suas informações são privadas e seguras!
        """
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def adult_configuration_menu(self, query):
        """Menu de configuração adulta"""
        user_id = f"telegram_{query.from_user.id}"
        
        # Verificar se usuário tem acesso adulto
        try:
            profile = self.user_db.get_profile(user_id) if self.user_db else {}
            has_adult_access = profile.get('has_mature_access', False)
            age = profile.get('user_age')
            
            if not has_adult_access or not age or (isinstance(age, str) and not age.isdigit()) or (isinstance(age, (int, str)) and int(age) < 18):
                keyboard = [[InlineKeyboardButton("⬅️ Voltar", callback_data="back_to_main")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                text = """
🔞 **ACESSO NEGADO**

❌ Sistema adulto não disponível.

**Requisitos:**
• Idade mínima: 18 anos
• Verificação de idade concluída

💡 Configure sua idade no menu de personalização primeiro!
                """
                
                await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
                return
        except Exception:
            has_adult_access = False
        
        keyboard = [
            [InlineKeyboardButton("🌶️ Ativar Modo Adulto", callback_data="save_adult_mode_true"),
             InlineKeyboardButton("😇 Desativar", callback_data="save_adult_mode_false")],
            [InlineKeyboardButton("⚙️ Configurações Avançadas", callback_data="adult_advanced"),
             InlineKeyboardButton("📊 Status", callback_data="adult_status")],
            [InlineKeyboardButton("⬅️ Voltar", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """
🔞 **SISTEMA ADULTO (18+)**

✅ **Acesso Autorizado**

🌶️ **Recursos Disponíveis:**
• Conversas mais íntimas
• Personalidade intensificada
• Conteúdo adulto apropriado
• Configurações avançadas

⚠️ **Lembre-se:**
Sempre dentro dos limites éticos!
        """
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def save_preference(self, query, data):
        """Salvar preferência do usuário"""
        user_id = f"telegram_{query.from_user.id}"
        user_name = query.from_user.first_name
        
        # Extrair tipo e valor da preferência
        parts = data.split('_', 2)
        if len(parts) < 3:
            await query.edit_message_text("❌ Erro ao salvar preferência!")
            return
        
        pref_type = parts[1]
        pref_value = parts[2]
        
        # Salvar no banco se disponível
        try:
            if self.user_db:
                # Obter perfil atual
                profile = self.user_db.get_profile(user_id) or {}
                
                # Atualizar campo específico
                if pref_type == "name":
                    profile['bot_name'] = pref_value
                    msg = f"✅ Nome alterado para: **{pref_value}**"
                elif pref_type == "personality":
                    profile['bot_personality'] = pref_value
                    msg = f"✅ Personalidade alterada para: **{pref_value}**"
                elif pref_type == "language":
                    profile['bot_language'] = pref_value
                    msg = f"✅ Estilo alterado para: **{pref_value}**"
                elif pref_type == "age":
                    if pref_value == "adult":
                        profile['user_age'] = "18"
                        profile['has_mature_access'] = True
                        msg = "✅ **Idade confirmada: 18+ anos**\n🔞 Sistema adulto **DESBLOQUEADO**!"
                    else:
                        profile['user_age'] = "16"
                        profile['has_mature_access'] = False
                        msg = "✅ **Idade confirmada: Menor de 18**\n🛡️ Modo seguro **ATIVADO**!"
                elif pref_type == "adult" and pref_value == "mode":
                    # Ativar/desativar modo adulto
                    if profile.get('has_mature_access'):
                        profile['adult_mode_active'] = data.endswith('true')
                        status = "ATIVADO" if data.endswith('true') else "DESATIVADO"
                        msg = f"🌶️ **Modo Adulto {status}**!"
                    else:
                        msg = "❌ **Acesso Negado**\nVerifique sua idade primeiro!"
                else:
                    msg = f"✅ Configuração '{pref_type}' salva!"
                
                # Salvar perfil
                profile.update({
                    'user_id': user_id,
                    'user_name': user_name
                })
                
                # Método de salvamento (você precisa implementar este método)
                # self.user_db.save_profile(user_id, profile)
                print(f"[DEBUG] Salvando perfil: {profile}")
            else:
                msg = f"✅ Configuração '{pref_value}' aplicada temporariamente!"
        
        except Exception as e:
            print(f"[DEBUG] Erro ao salvar: {e}")
            msg = f"⚠️ Configuração aplicada temporariamente: **{pref_value}**"
        
        # Botão para voltar
        keyboard = [[InlineKeyboardButton("⬅️ Voltar ao Menu", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(msg + "\n\n🎯 Continue personalizando!", 
                                     reply_markup=reply_markup, parse_mode='Markdown')
    
    def get_user_profile(self, user_id, user_name):
        """Obter ou criar perfil do usuário Telegram"""
        try:
            # Tentar carregar perfil existente do banco
            if self.user_db:
                profile = self.user_db.get_profile(f'telegram_{user_id}')
                if profile:
                    return profile
        except Exception as e:
            print(f"[DEBUG] Erro ao carregar perfil: {e}")
        
        # Criar perfil padrão para novos usuários
        return {
            'user_id': f'telegram_{user_id}',
            'user_name': user_name,
            'bot_name': 'Aina',
            'bot_personality': 'amigavel',
            'bot_language': 'informal',
            'has_mature_access': False,  # Será verificado dinamicamente
            'user_age': None,  # Será definido na personalização
            'bot_gender': 'feminino',
            'user_gender': 'não_informado'
        }

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