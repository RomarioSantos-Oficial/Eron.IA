"""
Handlers para sistema de preferências
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def show_preferences_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar menu principal de preferências"""
    keyboard = [
        [
            InlineKeyboardButton("💬 Chat", callback_data="pref_chat"),
            InlineKeyboardButton("🎨 Visual", callback_data="pref_visual")
        ],
        [
            InlineKeyboardButton("🔔 Notificações", callback_data="pref_notifications"),
            InlineKeyboardButton("🔒 Privacidade", callback_data="pref_privacy")
        ],
        [
            InlineKeyboardButton("🌡️ Temperatura", callback_data="pref_temperature"),
            InlineKeyboardButton("⚡ Velocidade", callback_data="pref_speed")
        ],
        [
            InlineKeyboardButton("🔄 Resetar Tudo", callback_data="reset_all_preferences"),
            InlineKeyboardButton("❌ Fechar", callback_data="close_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
⚙️ **PREFERÊNCIAS DO BOT**

Configure como eu me comporto e respondo:

• **Chat**: Estilo de conversa, formalidade
• **Visual**: Emojis, formatação das mensagens  
• **Notificações**: Quando e como avisar
• **Privacidade**: O que lembrar sobre você
• **Temperatura**: Criatividade das respostas
• **Velocidade**: Rapidez vs detalhamento
"""
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text, reply_markup=reply_markup, parse_mode='Markdown'
        )

async def handle_preferences_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler principal para callbacks de preferências"""
    query = update.callback_query
    callback_data = query.data
    user_id = str(query.from_user.id)
    
    try:
        if callback_data == "pref_chat":
            await show_chat_preferences(update, context)
        
        elif callback_data == "pref_visual":
            await show_visual_preferences(update, context)
        
        elif callback_data == "pref_notifications":
            await show_notification_preferences(update, context)
        
        elif callback_data == "pref_privacy":
            await show_privacy_preferences(update, context)
        
        elif callback_data == "pref_temperature":
            await show_temperature_preferences(update, context)
        
        elif callback_data == "pref_speed":
            await show_speed_preferences(update, context)
        
        elif callback_data == "reset_all_preferences":
            await confirm_reset_preferences(update, context)
        
        elif callback_data.startswith("save_pref_"):
            await save_preference(update, context)
        
        elif callback_data == "confirm_reset_all":
            await execute_reset_preferences(update, context)
    
    except Exception as e:
        logger.error(f"Erro em preferências: {e}")
        await query.edit_message_text("❌ Erro ao processar preferência.")

async def show_chat_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Preferências de chat"""
    keyboard = [
        [
            InlineKeyboardButton("😊 Casual", callback_data="save_pref_chat_casual"),
            InlineKeyboardButton("💼 Formal", callback_data="save_pref_chat_formal")
        ],
        [
            InlineKeyboardButton("📝 Detalhado", callback_data="save_pref_chat_detailed"),
            InlineKeyboardButton("⚡ Conciso", callback_data="save_pref_chat_concise")
        ],
        [
            InlineKeyboardButton("🎭 Criativo", callback_data="save_pref_chat_creative"),
            InlineKeyboardButton("📊 Objetivo", callback_data="save_pref_chat_objective")
        ],
        [InlineKeyboardButton("🔙 Voltar", callback_data="preferences_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "💬 **PREFERÊNCIAS DE CHAT**\n\nComo prefere que eu converse?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_visual_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Preferências visuais"""
    keyboard = [
        [
            InlineKeyboardButton("😀 Muitos Emojis", callback_data="save_pref_visual_many_emojis"),
            InlineKeyboardButton("😊 Poucos Emojis", callback_data="save_pref_visual_few_emojis")
        ],
        [
            InlineKeyboardButton("🚫 Sem Emojis", callback_data="save_pref_visual_no_emojis"),
            InlineKeyboardButton("✨ Formatação Rica", callback_data="save_pref_visual_rich_format")
        ],
        [
            InlineKeyboardButton("📄 Texto Simples", callback_data="save_pref_visual_plain_text"),
            InlineKeyboardButton("🔙 Voltar", callback_data="preferences_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🎨 **PREFERÊNCIAS VISUAIS**\n\nComo prefere ver as mensagens?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_temperature_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Preferências de criatividade (temperatura)"""
    keyboard = [
        [
            InlineKeyboardButton("🧊 Conservadora", callback_data="save_pref_temp_low"),
            InlineKeyboardButton("⚖️ Equilibrada", callback_data="save_pref_temp_medium")
        ],
        [
            InlineKeyboardButton("🔥 Criativa", callback_data="save_pref_temp_high"),
            InlineKeyboardButton("🎲 Imprevisível", callback_data="save_pref_temp_very_high")
        ],
        [InlineKeyboardButton("🔙 Voltar", callback_data="preferences_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🌡️ **TEMPERATURA DE CRIATIVIDADE**

• **Conservadora**: Respostas precisas e previsíveis
• **Equilibrada**: Balance entre precisão e criatividade
• **Criativa**: Respostas mais originais e variadas
• **Imprevisível**: Máxima criatividade e surpresa
"""
    
    await update.callback_query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode='Markdown'
    )

async def show_speed_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Preferências de velocidade"""
    keyboard = [
        [
            InlineKeyboardButton("⚡ Rápido", callback_data="save_pref_speed_fast"),
            InlineKeyboardButton("⚖️ Normal", callback_data="save_pref_speed_normal")
        ],
        [
            InlineKeyboardButton("🐌 Detalhado", callback_data="save_pref_speed_detailed"),
            InlineKeyboardButton("🔙 Voltar", callback_data="preferences_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
⚡ **VELOCIDADE DE RESPOSTA**

• **Rápido**: Respostas concisas e diretas
• **Normal**: Balance entre rapidez e detalhes
• **Detalhado**: Respostas completas e elaboradas
"""
    
    await update.callback_query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode='Markdown'
    )

async def show_notification_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Preferências de notificações"""
    keyboard = [
        [
            InlineKeyboardButton("🔔 Tudo", callback_data="save_pref_notif_all"),
            InlineKeyboardButton("📢 Importantes", callback_data="save_pref_notif_important")
        ],
        [
            InlineKeyboardButton("🔕 Mínimas", callback_data="save_pref_notif_minimal"),
            InlineKeyboardButton("⏰ Horário Específico", callback_data="save_pref_notif_scheduled")
        ],
        [InlineKeyboardButton("🔙 Voltar", callback_data="preferences_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🔔 **PREFERÊNCIAS DE NOTIFICAÇÕES**\n\nQuando devo te avisar sobre novidades?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_privacy_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Preferências de privacidade"""
    keyboard = [
        [
            InlineKeyboardButton("🧠 Lembrar Tudo", callback_data="save_pref_privacy_remember_all"),
            InlineKeyboardButton("📝 Básico", callback_data="save_pref_privacy_basic")
        ],
        [
            InlineKeyboardButton("🔒 Mínimo", callback_data="save_pref_privacy_minimal"),
            InlineKeyboardButton("❌ Não Lembrar", callback_data="save_pref_privacy_no_memory")
        ],
        [InlineKeyboardButton("🔙 Voltar", callback_data="preferences_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🔒 **PREFERÊNCIAS DE PRIVACIDADE**

• **Lembrar Tudo**: Histórico completo de conversas
• **Básico**: Apenas preferências e contexto atual
• **Mínimo**: Só informações essenciais
• **Não Lembrar**: Cada conversa é independente
"""
    
    await update.callback_query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode='Markdown'
    )

async def save_preference(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Salvar preferência selecionada"""
    query = update.callback_query
    callback_data = query.data
    user_id = str(query.from_user.id)
    
    try:
        from core.preferences import PreferencesManager
        preferences_manager = PreferencesManager()
        
        # Extrair tipo e valor da preferência
        parts = callback_data.split('_')
        if len(parts) >= 4:
            pref_category = parts[2]
            pref_value = '_'.join(parts[3:])
            
            success = preferences_manager.set_preference(user_id, pref_category, pref_value)
            
            if success:
                await query.answer("✅ Preferência salva!")
                await show_preferences_menu(update, context)
            else:
                await query.answer("❌ Erro ao salvar preferência")
    
    except Exception as e:
        logger.error(f"Erro ao salvar preferência: {e}")
        await query.answer("❌ Erro interno")

async def confirm_reset_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirmar reset de preferências"""
    keyboard = [
        [
            InlineKeyboardButton("⚠️ Sim, Resetar Tudo", callback_data="confirm_reset_all"),
            InlineKeyboardButton("❌ Cancelar", callback_data="preferences_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "⚠️ **CONFIRMAR RESET**\n\n"
        "Tem certeza que quer resetar TODAS as preferências?\n"
        "Esta ação não pode ser desfeita.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def execute_reset_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executar reset de preferências"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    try:
        from core.preferences import PreferencesManager
        preferences_manager = PreferencesManager()
        
        success = preferences_manager.reset_all_preferences(user_id)
        
        if success:
            await query.edit_message_text(
                "✅ **PREFERÊNCIAS RESETADAS**\n\n"
                "Todas as suas preferências foram restauradas para o padrão.\n"
                "Use /preferencias para configurar novamente."
            )
        else:
            await query.edit_message_text("❌ Erro ao resetar preferências.")
    
    except Exception as e:
        logger.error(f"Erro ao resetar preferências: {e}")
        await query.edit_message_text("❌ Erro interno ao resetar preferências.")
