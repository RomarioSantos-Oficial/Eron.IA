"""
Handlers de conversação para personalização do bot
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

# Estados da conversa de personalização
PERSONALIZATION_INTRO = 4
GET_USER_NAME = 5
GET_USER_AGE = 6
GET_USER_GENDER = 7
GET_BOT_NAME = 8
GET_BOT_GENDER = 9
SELECT_PERSONALITY = 10
SELECT_LANGUAGE = 11
SELECT_TOPICS = 12
PERSONALIZATION_COMPLETE = 13

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_personalization_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Iniciar menu de personalização"""
    keyboard = [
        [
            InlineKeyboardButton("👤 Sobre Você", callback_data="personalize_user"),
            InlineKeyboardButton("🤖 Sobre o Bot", callback_data="personalize_bot")
        ],
        [
            InlineKeyboardButton("🎭 Personalidade", callback_data="personalize_personality"),
            InlineKeyboardButton("🗣️ Idioma", callback_data="personalize_language")
        ],
        [
            InlineKeyboardButton("📚 Tópicos", callback_data="personalize_topics"),
            InlineKeyboardButton("✅ Finalizar", callback_data="complete_personalization")
        ],
        [InlineKeyboardButton("❌ Cancelar", callback_data="cancel_personalization")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🎯 **PERSONALIZAÇÃO DO BOT**

Vamos configurar como você quer que eu seja!

**Opções disponíveis:**
• **Sobre Você**: Nome, idade, gênero
• **Sobre o Bot**: Nome que prefere para mim, gênero
• **Personalidade**: Como prefere que eu responda
• **Idioma**: Português, Inglês, etc.
• **Tópicos**: Assuntos de seu interesse
"""
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text, reply_markup=reply_markup, parse_mode='Markdown'
        )

async def handle_personalization_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para callbacks de personalização"""
    query = update.callback_query
    callback_data = query.data
    user_id = str(query.from_user.id)
    
    try:
        from core.user_profile_db import UserProfileDB as UserService
        user_service = UserService()
        
        if callback_data == "personalize_user":
            await personalize_user_info(update, context)
        
        elif callback_data == "personalize_bot":
            await personalize_bot_info(update, context)
        
        elif callback_data == "personalize_personality":
            await show_personality_options(update, context)
        
        elif callback_data == "personalize_language":
            await show_language_options(update, context)
        
        elif callback_data == "personalize_topics":
            await show_topics_options(update, context)
        
        elif callback_data == "complete_personalization":
            await complete_personalization(update, context)
        
        elif callback_data == "cancel_personalization":
            await cancel_personalization(update, context)
        
        # Callbacks específicos de personalização
        elif callback_data.startswith("save_user_gender_"):
            gender = callback_data.replace("save_user_gender_", "")
            await save_user_data(update, context, "user_gender", gender)
        
        elif callback_data.startswith("save_bot_gender_"):
            gender = callback_data.replace("save_bot_gender_", "")
            await save_user_data(update, context, "bot_gender", gender)
        
        elif callback_data.startswith("save_personality_"):
            personality = callback_data.replace("save_personality_", "")
            await save_user_data(update, context, "bot_personality", personality)
        
        elif callback_data.startswith("save_language_"):
            language = callback_data.replace("save_language_", "")
            await save_user_data(update, context, "bot_language", language)
        
        elif callback_data.startswith("toggle_topic_"):
            topic = callback_data.replace("toggle_topic_", "")
            await toggle_user_topic(update, context, topic)
        
        elif callback_data == "save_topics":
            await save_user_topics(update, context)
        
        elif callback_data == "set_user_name":
            await request_user_name(update, context)
        
        elif callback_data == "set_user_age":
            await request_user_age(update, context)
        
        elif callback_data == "set_bot_name":
            await request_bot_name(update, context)
            
        elif callback_data.startswith("save_"):
            await save_personalization_data(update, context)
    
    except Exception as e:
        logger.error(f"Erro em personalização: {e}")
        await query.edit_message_text("❌ Erro ao processar personalização.")

async def personalize_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configurar informações do usuário"""
    keyboard = [
        [
            InlineKeyboardButton("✏️ Nome", callback_data="set_user_name"),
            InlineKeyboardButton("🎂 Idade", callback_data="set_user_age")
        ],
        [
            InlineKeyboardButton("♂️ Masculino", callback_data="save_user_gender_masculine"),
            InlineKeyboardButton("♀️ Feminino", callback_data="save_user_gender_feminine")
        ],
        [
            InlineKeyboardButton("🏳️‍⚧️ Não-binário", callback_data="save_user_gender_nonbinary"),
            InlineKeyboardButton("❔ Prefiro não dizer", callback_data="save_user_gender_unspecified")
        ],
        [InlineKeyboardButton("🔙 Voltar", callback_data="start_personalization")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "👤 **SOBRE VOCÊ**\n\nClique nas opções para configurar suas informações:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def personalize_bot_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configurar informações do bot"""
    keyboard = [
        [
            InlineKeyboardButton("✏️ Nome do Bot", callback_data="set_bot_name")
        ],
        [
            InlineKeyboardButton("♀️ Feminino", callback_data="save_bot_gender_feminine"),
            InlineKeyboardButton("♂️ Masculino", callback_data="save_bot_gender_masculine")
        ],
        [
            InlineKeyboardButton("🤖 Neutro", callback_data="save_bot_gender_neutral"),
            InlineKeyboardButton("🔙 Voltar", callback_data="start_personalization")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🤖 **SOBRE O BOT**\n\nComo você quer que eu seja?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_personality_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar opções de personalidade"""
    keyboard = [
        [
            InlineKeyboardButton("😊 Amigável", callback_data="save_personality_friendly"),
            InlineKeyboardButton("🤓 Intelectual", callback_data="save_personality_intellectual")
        ],
        [
            InlineKeyboardButton("😄 Divertida", callback_data="save_personality_funny"),
            InlineKeyboardButton("💼 Profissional", callback_data="save_personality_professional")
        ],
        [
            InlineKeyboardButton("🌟 Motivadora", callback_data="save_personality_motivational"),
            InlineKeyboardButton("😌 Calma", callback_data="save_personality_calm")
        ],
        [InlineKeyboardButton("🔙 Voltar", callback_data="start_personalization")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🎭 **PERSONALIDADE**\n\nEscolha como prefere que eu me comporte:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_language_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar opções de idioma"""
    keyboard = [
        [
            InlineKeyboardButton("🇧🇷 Português", callback_data="save_language_portuguese"),
            InlineKeyboardButton("🇺🇸 English", callback_data="save_language_english")
        ],
        [
            InlineKeyboardButton("🇪🇸 Español", callback_data="save_language_spanish"),
            InlineKeyboardButton("🇫🇷 Français", callback_data="save_language_french")
        ],
        [InlineKeyboardButton("🔙 Voltar", callback_data="start_personalization")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🗣️ **IDIOMA**\n\nEm que idioma prefere conversar?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_topics_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar opções de tópicos"""
    keyboard = [
        [
            InlineKeyboardButton("💻 Tecnologia", callback_data="toggle_topic_technology"),
            InlineKeyboardButton("🎨 Arte", callback_data="toggle_topic_art")
        ],
        [
            InlineKeyboardButton("⚽ Esportes", callback_data="toggle_topic_sports"),
            InlineKeyboardButton("🎵 Música", callback_data="toggle_topic_music")
        ],
        [
            InlineKeyboardButton("📚 Estudos", callback_data="toggle_topic_education"),
            InlineKeyboardButton("🍳 Culinária", callback_data="toggle_topic_cooking")
        ],
        [
            InlineKeyboardButton("✅ Salvar Tópicos", callback_data="save_topics"),
            InlineKeyboardButton("🔙 Voltar", callback_data="start_personalization")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "📚 **TÓPICOS DE INTERESSE**\n\nSelecione assuntos que gosta de conversar:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def save_personalization_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Salvar dados de personalização"""
    query = update.callback_query
    callback_data = query.data
    user_id = str(query.from_user.id)
    
    try:
        from core.user_profile_db import UserProfileDB as UserService
        user_service = UserService()
        
        success = user_service.save_personalization_setting(user_id, callback_data)
        
        if success:
            await query.answer("✅ Salvo!")
            await start_personalization_menu(update, context)
        else:
            await query.answer("❌ Erro ao salvar")
    
    except Exception as e:
        logger.error(f"Erro ao salvar personalização: {e}")
        await query.answer("❌ Erro interno")

async def complete_personalization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Finalizar personalização"""
    await update.callback_query.edit_message_text(
        "✅ **PERSONALIZAÇÃO CONCLUÍDA!**\n\n"
        "Perfeito! Agora posso conversar com você do jeito que prefere.\n\n"
        "Digite qualquer mensagem para começarmos a conversar! 😊\n\n"
        "Você pode usar /personalizar a qualquer momento para ajustar suas preferências."
    )
    return ConversationHandler.END

async def cancel_personalization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancelar personalização"""
    await update.callback_query.edit_message_text(
        "❌ **PERSONALIZAÇÃO CANCELADA**\n\n"
        "Tudo bem! Você pode usar /personalizar quando quiser configurar o bot.\n\n"
        "Por enquanto, pode conversar comigo normalmente! 😊"
    )
    return ConversationHandler.END

async def save_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE, field: str, value: str):
    """Salvar dados do usuário"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    try:
        from core.user_profile_db import UserProfileDB as UserService
        user_service = UserService()
        
        # Mapear valores para o banco
        value_map = {
            "masculine": "masculino",
            "feminine": "feminino", 
            "nonbinary": "não-binário",
            "unspecified": "prefiro não dizer",
            "neutral": "neutro",
            "friendly": "amigável",
            "intellectual": "intelectual",
            "funny": "divertida",
            "professional": "profissional",
            "motivational": "motivadora",
            "calm": "calma",
            "portuguese": "português",
            "english": "inglês",
            "spanish": "espanhol",
            "french": "francês"
        }
        
        final_value = value_map.get(value, value)
        
        # Salvar no banco
        profile_data = {field: final_value}
        user_service.update_user_profile(user_id, **profile_data)
        
        await query.answer("✅ Salvo!")
        await start_personalization_menu(update, context)
        
    except Exception as e:
        logger.error(f"Erro ao salvar {field}: {e}")
        await query.answer("❌ Erro ao salvar")

async def toggle_user_topic(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    """Toggle tópico do usuário"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    try:
        # Armazenar tópicos temporariamente no contexto
        if 'selected_topics' not in context.user_data:
            context.user_data['selected_topics'] = set()
        
        if topic in context.user_data['selected_topics']:
            context.user_data['selected_topics'].remove(topic)
            await query.answer(f"❌ {topic.title()} removido")
        else:
            context.user_data['selected_topics'].add(topic)
            await query.answer(f"✅ {topic.title()} adicionado")
            
        # Atualizar a interface com tópicos selecionados
        await show_topics_options(update, context)
        
    except Exception as e:
        logger.error(f"Erro ao toggle tópico: {e}")
        await query.answer("❌ Erro")

async def save_user_topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Salvar tópicos selecionados"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    try:
        from core.user_profile_db import UserProfileDB as UserService
        user_service = UserService()
        
        selected_topics = context.user_data.get('selected_topics', set())
        topics_string = ",".join(selected_topics) if selected_topics else ""
        
        user_service.update_user_profile(user_id, preferred_topics=topics_string)
        
        await query.answer("✅ Tópicos salvos!")
        await start_personalization_menu(update, context)
        
    except Exception as e:
        logger.error(f"Erro ao salvar tópicos: {e}")
        await query.answer("❌ Erro ao salvar")

async def request_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Solicitar nome do usuário"""
    await update.callback_query.edit_message_text(
        "✏️ **SEU NOME**\n\n"
        "Por favor, digite seu nome:"
    )
    context.user_data['waiting_for'] = 'user_name'

async def request_user_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Solicitar idade do usuário"""
    await update.callback_query.edit_message_text(
        "🎂 **SUA IDADE**\n\n"
        "Por favor, digite sua idade:"
    )
    context.user_data['waiting_for'] = 'user_age'

async def request_bot_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Solicitar nome do bot"""
    await update.callback_query.edit_message_text(
        "🤖 **NOME DO BOT**\n\n"
        "Como você quer que eu me chame?\n"
        "Digite o nome que prefere:"
    )
    context.user_data['waiting_for'] = 'bot_name'
