import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, CallbackQueryHandler, filters
from src.memory import EronMemory
from src.preferences import PreferencesManager
from src.emotion_system import EmotionSystem
from app import get_llm_response
import re
import json

# Estados da conversa
GET_NAME = 1
GET_AGE = 2
GET_GENDER = 3

# Estados para preferências
PREF_MENU = 10
PREF_CHAT = 11
PREF_VISUAL = 12
PREF_NOTIFY = 13

# Estados para emoções
EMOTION_MENU = 20
EMOTION_DETECTION = 21
EMOTION_RANGE = 22

# Configurar o logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Instância da memória de conversa (mantém-se local)
memory = EronMemory()

# Instâncias dos gerenciadores
preferences_manager = PreferencesManager()
emotion_system = EmotionSystem()

# Funções de conversação para /definir_perfil
async def definir_perfil_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Vamos definir seu perfil! Qual é o seu nome?")
    return GET_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_name = update.message.text
    user_profile_db = context.application.user_profile_db
    
    profile = user_profile_db.get_profile(user_id) or {}
    profile['user_name'] = user_name
    
    user_profile_db.save_profile(user_id=user_id, **profile)
    await update.message.reply_text(f"Obrigado, {user_name}! E qual a sua idade?")
    return GET_AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_age_str = update.message.text.strip()
    user_profile_db = context.application.user_profile_db
    try:
        user_age = int(user_age_str)
        if user_age < 18:
            await update.message.reply_text("Você deve ter 18 anos ou mais para usar este bot. A conversa será cancelada.")
            return ConversationHandler.END
        
        profile = user_profile_db.get_profile(user_id) or {}
        profile['user_age'] = user_age_str
        
        user_profile_db.save_profile(user_id=user_id, **profile)
        await update.message.reply_text("Ótimo! E qual o seu gênero? (Masculino, Feminino, Outro)")
        return GET_GENDER
    except ValueError:
        await update.message.reply_text("Idade inválida. Por favor, digite um número.")
        return GET_AGE
        
async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_gender = update.message.text
    user_profile_db = context.application.user_profile_db
    
    profile = user_profile_db.get_profile(user_id) or {}
    profile['user_gender'] = user_gender
    
    user_profile_db.save_profile(user_id=user_id, **profile)
    await update.message.reply_text("Tudo pronto! Seu perfil foi salvo. Você pode começar a conversar.")
    return ConversationHandler.END
    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("A definição do perfil foi cancelada.")
    return ConversationHandler.END

# Funções para preferências
async def preferences_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra o menu principal de preferências"""
    keyboard = [
        [InlineKeyboardButton("💬 Preferências de Chat", callback_data='pref_chat')],
        [InlineKeyboardButton("🎨 Preferências Visuais", callback_data='pref_visual')],
        [InlineKeyboardButton("🔔 Notificações", callback_data='pref_notify')],
        [InlineKeyboardButton("❌ Fechar", callback_data='close')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🛠 Configure suas preferências:\n"
        "Escolha uma categoria para ajustar suas configurações.",
        reply_markup=reply_markup
    )
    return PREF_MENU

async def handle_chat_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gerencia as preferências de chat"""
    query = update.callback_query
    user_id = str(update.effective_user.id)
    
    # Obter preferências atuais
    prefs = preferences_manager.get_preferences(user_id)
    chat_prefs = prefs['chat']
    
    keyboard = [
        [
            InlineKeyboardButton(
                "🗣 Estilo: " + chat_prefs['message_style'],
                callback_data='chat_style'
            )
        ],
        [
            InlineKeyboardButton(
                "📏 Comprimento: " + chat_prefs['response_length'],
                callback_data='chat_length'
            )
        ],
        [
            InlineKeyboardButton(
                "😊 Emojis: " + ("Ligado" if chat_prefs['include_emojis'] else "Desligado"),
                callback_data='chat_emoji'
            )
        ],
        [InlineKeyboardButton("⬅️ Voltar", callback_data='back_to_menu')]
    ]
    
    await query.edit_message_text(
        "💬 Preferências de Chat\n"
        "Clique em uma opção para alternar:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_chat_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alterna entre os estilos de chat"""
    query = update.callback_query
    user_id = str(update.effective_user.id)
    
    # Obter e atualizar preferências
    prefs = preferences_manager.get_preferences(user_id)
    styles = ['casual', 'formal', 'friendly']
    current = prefs['chat']['message_style']
    next_style = styles[(styles.index(current) + 1) % len(styles)]
    
    prefs['chat']['message_style'] = next_style
    preferences_manager.update_preferences(user_id, prefs)
    
    # Retornar ao menu de chat
    await handle_chat_preferences(update, context)

async def handle_chat_length(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alterna entre os comprimentos de resposta"""
    query = update.callback_query
    user_id = str(update.effective_user.id)
    
    # Obter e atualizar preferências
    prefs = preferences_manager.get_preferences(user_id)
    lengths = ['short', 'medium', 'long']
    current = prefs['chat']['response_length']
    next_length = lengths[(lengths.index(current) + 1) % len(lengths)]
    
    prefs['chat']['response_length'] = next_length
    preferences_manager.update_preferences(user_id, prefs)
    
    # Retornar ao menu de chat
    await handle_chat_preferences(update, context)

async def handle_chat_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alterna o uso de emojis"""
    query = update.callback_query
    user_id = str(update.effective_user.id)
    
    # Obter e atualizar preferências
    prefs = preferences_manager.get_preferences(user_id)
    prefs['chat']['include_emojis'] = not prefs['chat']['include_emojis']
    preferences_manager.update_preferences(user_id, prefs)
    
    # Retornar ao menu de chat
    await handle_chat_preferences(update, context)

async def handle_preference_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gerencia todos os callbacks de preferências"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'pref_chat':
        await handle_chat_preferences(update, context)
    elif query.data == 'chat_style':
        await handle_chat_style(update, context)
    elif query.data == 'chat_length':
        await handle_chat_length(update, context)
    elif query.data == 'chat_emoji':
        await handle_chat_emoji(update, context)
    elif query.data == 'back_to_menu':
        keyboard = [
            [InlineKeyboardButton("💬 Preferências de Chat", callback_data='pref_chat')],
            [InlineKeyboardButton("🎨 Preferências Visuais", callback_data='pref_visual')],
            [InlineKeyboardButton("🔔 Notificações", callback_data='pref_notify')],
            [InlineKeyboardButton("❌ Fechar", callback_data='close')]
        ]
        await query.edit_message_text(
            "🛠 Configure suas preferências:\n"
            "Escolha uma categoria para ajustar suas configurações.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif query.data == 'close':
        await query.delete_message()

# Funções para emoções
async def emotions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra o menu principal de emoções"""
    user_id = str(update.effective_user.id)
    prefs = emotion_system.get_emotion_preferences(user_id)
    bot_emotion = emotion_system.get_bot_emotion(user_id)
    
    # Formatando o estado emocional atual
    current_emotion = "Neutra"
    if bot_emotion:
        current_emotion = f"{bot_emotion['emotion']} (Intensidade: {bot_emotion['intensity']})"
    
    keyboard = [
        [
            InlineKeyboardButton(
                "🎭 Detecção: " + ("Ligada" if prefs['emotion_detection_enabled'] else "Desligada"),
                callback_data='emotion_detection'
            )
        ],
        [
            InlineKeyboardButton(
                "📊 Intensidade: " + str(prefs['emotional_range']),
                callback_data='emotion_range'
            )
        ],
        [InlineKeyboardButton("❌ Fechar", callback_data='close')]
    ]
    
    await update.message.reply_text(
        f"🎭 Configurações Emocionais\n\n"
        f"Estado Atual: {current_emotion}\n\n"
        "Ajuste como eu expresso minhas emoções:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return EMOTION_MENU

async def handle_emotion_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gerencia todos os callbacks de emoções"""
    query = update.callback_query
    await query.answer()
    user_id = str(update.effective_user.id)
    
    if query.data == 'emotion_detection':
        # Alternar detecção de emoções
        prefs = emotion_system.get_emotion_preferences(user_id)
        prefs['emotion_detection_enabled'] = not prefs['emotion_detection_enabled']
        emotion_system.update_emotion_preferences(
            user_id=user_id,
            emotion_detection_enabled=prefs['emotion_detection_enabled']
        )
        
        # Atualizar menu
        bot_emotion = emotion_system.get_bot_emotion(user_id)
        current_emotion = "Neutra"
        if bot_emotion:
            current_emotion = f"{bot_emotion['emotion']} (Intensidade: {bot_emotion['intensity']})"
            
        keyboard = [
            [
                InlineKeyboardButton(
                    "🎭 Detecção: " + ("Ligada" if prefs['emotion_detection_enabled'] else "Desligada"),
                    callback_data='emotion_detection'
                )
            ],
            [
                InlineKeyboardButton(
                    "📊 Intensidade: " + str(prefs['emotional_range']),
                    callback_data='emotion_range'
                )
            ],
            [InlineKeyboardButton("❌ Fechar", callback_data='close')]
        ]
        
        await query.edit_message_text(
            f"🎭 Configurações Emocionais\n\n"
            f"Estado Atual: {current_emotion}\n\n"
            "Ajuste como eu expresso minhas emoções:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    elif query.data == 'emotion_range':
        # Alternar intensidade emocional
        prefs = emotion_system.get_emotion_preferences(user_id)
        current_range = prefs['emotional_range']
        new_range = (current_range % 3) + 1  # Alterna entre 1, 2 e 3
        
        emotion_system.update_emotion_preferences(
            user_id=user_id,
            emotional_range=new_range
        )
        
        # Atualizar menu
        bot_emotion = emotion_system.get_bot_emotion(user_id)
        current_emotion = "Neutra"
        if bot_emotion:
            current_emotion = f"{bot_emotion['emotion']} (Intensidade: {bot_emotion['intensity']})"
            
        keyboard = [
            [
                InlineKeyboardButton(
                    "🎭 Detecção: " + ("Ligada" if prefs['emotion_detection_enabled'] else "Desligada"),
                    callback_data='emotion_detection'
                )
            ],
            [
                InlineKeyboardButton(
                    "📊 Intensidade: " + str(new_range),
                    callback_data='emotion_range'
                )
            ],
            [InlineKeyboardButton("❌ Fechar", callback_data='close')]
        ]
        
        await query.edit_message_text(
            f"🎭 Configurações Emocionais\n\n"
            f"Estado Atual: {current_emotion}\n\n"
            "Ajuste como eu expresso minhas emoções:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    elif query.data == 'close':
        await query.delete_message()

# Função para o comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Olá, {user_name}! Eu sou o Eron, seu assistente pessoal. O que posso fazer por você? Diga "meu nome é [seu nome]" para eu me lembrar de você!'
    )

# Função para o comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Olá! Sou um assistente de apoio emocional. Estou aqui para conversar e ajudar com o que precisar. Use os seguintes comandos:\n'
             '/definir_perfil - Para eu me lembrar do seu nome, idade e gênero.\n'
             '/cancelar - Para cancelar a definição do perfil.\n'
             '/chat - Para iniciar uma conversa normal.\n'
             '/personalizar - Para mudar meu nome, gênero e outras configurações.\n'
             '/preferencias - Para ajustar como eu me comunico com você.\n'
             '/emocoes - Para configurar minhas respostas emocionais.\n\n'
             'Fique à vontade para desabafar ou fazer qualquer pergunta.'
    )

# Função de chat
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    
    profile = user_profile_db.get_profile(user_id)
    if profile:
        user_name = profile.get('user_name', update.effective_user.first_name)
        bot_name = profile.get('bot_name', 'Eron')
    else:
        user_name = update.effective_user.first_name
        bot_name = 'Eron'

    # Obter preferências e estado emocional
    user_preferences = preferences_manager.get_preferences(user_id)
    emotion_prefs = emotion_system.get_emotion_preferences(user_id)

    # Detectar emoção do usuário se habilitado
    if emotion_prefs['emotion_detection_enabled']:
        user_emotion, confidence = emotion_system.detect_user_emotion(user_id, user_message)
        
        # Ajustar emoção do bot se a confiança for alta
        if confidence > 0.5:
            emotion_system.set_bot_emotion(
                user_id=user_id,
                emotion=user_emotion,
                intensity=emotion_prefs['emotional_range'],
                trigger=f"Resposta à mensagem: {user_message[:50]}..."
            )

    response = get_llm_response(user_message, user_profile=profile)
    if not response:
        response = "Desculpe, não consegui me conectar com a IA no momento. Por favor, verifique se o servidor do LM Studio está rodando."
    
    memory.save_message(user_message, response)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response
    )

def main(application, user_profile_db):
    logging.info("Adicionando handlers...")
    
    # Adiciona a instância do banco de dados ao objeto de aplicação
    application.user_profile_db = user_profile_db
    
    # ConversationHandler para definir o perfil
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('definir_perfil', definir_perfil_start)],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            GET_GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
        },
        fallbacks=[CommandHandler('cancelar', cancel)]
    )
    
    # Adicionar os handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("preferencias", preferences_menu))
    application.add_handler(CommandHandler("emocoes", emotions_menu))
    application.add_handler(CallbackQueryHandler(handle_preference_button, pattern='^(pref_|chat_)'))
    application.add_handler(CallbackQueryHandler(handle_emotion_button, pattern='^emotion_'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))