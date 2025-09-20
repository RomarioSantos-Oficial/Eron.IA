"""
Handlers para sistema de emoções
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def show_emotions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar menu principal de emoções"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Status Emocional", callback_data="emotion_status"),
            InlineKeyboardButton("🎯 Detecção", callback_data="emotion_detection")
        ],
        [
            InlineKeyboardButton("🌡️ Sensibilidade", callback_data="emotion_sensitivity"),
            InlineKeyboardButton("📈 Histórico", callback_data="emotion_history")
        ],
        [
            InlineKeyboardButton("🎭 Expressar Emoção", callback_data="emotion_express"),
            InlineKeyboardButton("🔄 Resetar", callback_data="emotion_reset")
        ],
        [InlineKeyboardButton("❌ Fechar", callback_data="close_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
😊 **SISTEMA DE EMOÇÕES**

Configure como o bot detecta e responde às suas emoções:

• **Status**: Ver estado emocional atual
• **Detecção**: Configurar sensibilidade
• **Sensibilidade**: Ajustar intensidade
• **Histórico**: Ver evolução emocional
• **Expressar**: Definir como se sente
• **Resetar**: Limpar dados emocionais
"""
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text, reply_markup=reply_markup, parse_mode='Markdown'
        )

async def handle_emotions_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler principal para callbacks de emoções"""
    query = update.callback_query
    callback_data = query.data
    user_id = str(query.from_user.id)
    
    try:
        if callback_data == "emotion_status":
            await show_emotion_status(update, context)
        
        elif callback_data == "emotion_detection":
            await show_emotion_detection_settings(update, context)
        
        elif callback_data == "emotion_sensitivity":
            await show_emotion_sensitivity(update, context)
        
        elif callback_data == "emotion_history":
            await show_emotion_history(update, context)
        
        elif callback_data == "emotion_express":
            await show_emotion_expression(update, context)
        
        elif callback_data == "emotion_reset":
            await confirm_emotion_reset(update, context)
        
        elif callback_data.startswith("set_emotion_"):
            await set_user_emotion(update, context)
        
        elif callback_data.startswith("save_emotion_"):
            await save_emotion_setting(update, context)
        
        elif callback_data == "confirm_emotion_reset":
            await execute_emotion_reset(update, context)
    
    except Exception as e:
        logger.error(f"Erro em sistema de emoções: {e}")
        await query.edit_message_text("❌ Erro ao processar emoção.")

async def show_emotion_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar status emocional atual"""
    user_id = str(update.callback_query.from_user.id)
    
    try:
        from src.emotion_system import EmotionSystem
        emotion_system = EmotionSystem()
        
        current_emotion = emotion_system.get_current_emotion(user_id)
        emotion_history = emotion_system.get_recent_emotions(user_id, limit=5)
        
        if current_emotion:
            emotion_text = f"😊 **Emoção Atual**: {current_emotion.name}\n"
            emotion_text += f"📊 **Intensidade**: {current_emotion.intensity}/10\n"
            emotion_text += f"⏰ **Desde**: {current_emotion.timestamp}\n\n"
        else:
            emotion_text = "😐 **Estado Neutro**\n\n"
        
        if emotion_history:
            emotion_text += "📈 **Últimas Emoções**:\n"
            for emotion in emotion_history:
                emotion_text += f"• {emotion.name} ({emotion.intensity}/10)\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Atualizar", callback_data="emotion_status")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="emotions_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            emotion_text, reply_markup=reply_markup, parse_mode='Markdown'
        )
    
    except Exception as e:
        logger.error(f"Erro ao mostrar status emocional: {e}")
        await update.callback_query.edit_message_text("❌ Erro ao carregar status emocional.")

async def show_emotion_detection_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configurações de detecção emocional"""
    keyboard = [
        [
            InlineKeyboardButton("🎯 Automática", callback_data="save_emotion_detection_auto"),
            InlineKeyboardButton("🤔 Perguntar", callback_data="save_emotion_detection_ask")
        ],
        [
            InlineKeyboardButton("👤 Manual", callback_data="save_emotion_detection_manual"),
            InlineKeyboardButton("❌ Desligada", callback_data="save_emotion_detection_off")
        ],
        [InlineKeyboardButton("🔙 Voltar", callback_data="emotions_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🎯 **DETECÇÃO EMOCIONAL**

Como prefere que eu detecte suas emoções?

• **Automática**: Analiso suas mensagens automaticamente
• **Perguntar**: Pergunto como você está se sentindo
• **Manual**: Você me conta quando quiser
• **Desligada**: Não analiso emoções
"""
    
    await update.callback_query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode='Markdown'
    )

async def show_emotion_sensitivity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configurar sensibilidade emocional"""
    keyboard = [
        [
            InlineKeyboardButton("🔥 Alta", callback_data="save_emotion_sensitivity_high"),
            InlineKeyboardButton("⚖️ Média", callback_data="save_emotion_sensitivity_medium")
        ],
        [
            InlineKeyboardButton("❄️ Baixa", callback_data="save_emotion_sensitivity_low"),
            InlineKeyboardButton("🔙 Voltar", callback_data="emotions_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🌡️ **SENSIBILIDADE EMOCIONAL**

Quão sensível deve ser a detecção?

• **Alta**: Detecta sutilezas emocionais
• **Média**: Balance entre precisão e estabilidade
• **Baixa**: Só detecta emoções evidentes
"""
    
    await update.callback_query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode='Markdown'
    )

async def show_emotion_expression(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu para expressar emoção atual"""
    keyboard = [
        [
            InlineKeyboardButton("😊 Feliz", callback_data="set_emotion_happy"),
            InlineKeyboardButton("😢 Triste", callback_data="set_emotion_sad")
        ],
        [
            InlineKeyboardButton("😠 Bravo", callback_data="set_emotion_angry"),
            InlineKeyboardButton("😰 Ansioso", callback_data="set_emotion_anxious")
        ],
        [
            InlineKeyboardButton("😴 Cansado", callback_data="set_emotion_tired"),
            InlineKeyboardButton("🤗 Animado", callback_data="set_emotion_excited")
        ],
        [
            InlineKeyboardButton("😐 Neutro", callback_data="set_emotion_neutral"),
            InlineKeyboardButton("🔙 Voltar", callback_data="emotions_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🎭 **COMO VOCÊ ESTÁ SE SENTINDO?**\n\nSelecione sua emoção atual:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_emotion_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar histórico emocional"""
    user_id = str(update.callback_query.from_user.id)
    
    try:
        from src.emotion_system import EmotionSystem
        emotion_system = EmotionSystem()
        
        emotions = emotion_system.get_recent_emotions(user_id, limit=10)
        
        if emotions:
            history_text = "📈 **HISTÓRICO EMOCIONAL**\n\n"
            for emotion in emotions:
                history_text += f"• {emotion.name} ({emotion.intensity}/10) - {emotion.timestamp}\n"
        else:
            history_text = "📭 **Nenhum histórico emocional ainda**\n\nComece a conversar para que eu aprenda sobre suas emoções!"
        
        keyboard = [
            [InlineKeyboardButton("🗑️ Limpar Histórico", callback_data="emotion_reset")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="emotions_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            history_text, reply_markup=reply_markup, parse_mode='Markdown'
        )
    
    except Exception as e:
        logger.error(f"Erro ao mostrar histórico emocional: {e}")
        await update.callback_query.edit_message_text("❌ Erro ao carregar histórico emocional.")

async def set_user_emotion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Definir emoção do usuário"""
    query = update.callback_query
    callback_data = query.data
    user_id = str(query.from_user.id)
    
    try:
        emotion_name = callback_data.split('_')[2]
        
        from src.emotion_system import EmotionSystem, Emotion
        emotion_system = EmotionSystem()
        
        # Criar objeto de emoção
        emotion = Emotion(
            name=emotion_name,
            intensity=7,  # Intensidade padrão
            category="user_defined"
        )
        
        success = emotion_system.add_emotion(user_id, emotion)
        
        if success:
            await query.answer("✅ Emoção registrada!")
            await show_emotions_menu(update, context)
        else:
            await query.answer("❌ Erro ao registrar emoção")
    
    except Exception as e:
        logger.error(f"Erro ao definir emoção: {e}")
        await query.answer("❌ Erro interno")

async def save_emotion_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Salvar configuração de emoção"""
    query = update.callback_query
    callback_data = query.data
    user_id = str(query.from_user.id)
    
    try:
        # Extrair configuração
        parts = callback_data.split('_')
        setting_type = parts[2]
        setting_value = '_'.join(parts[3:])
        
        from src.emotion_system import EmotionSystem
        emotion_system = EmotionSystem()
        
        success = emotion_system.save_user_setting(user_id, setting_type, setting_value)
        
        if success:
            await query.answer("✅ Configuração salva!")
            await show_emotions_menu(update, context)
        else:
            await query.answer("❌ Erro ao salvar configuração")
    
    except Exception as e:
        logger.error(f"Erro ao salvar configuração emocional: {e}")
        await query.answer("❌ Erro interno")

async def confirm_emotion_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirmar reset do sistema de emoções"""
    keyboard = [
        [
            InlineKeyboardButton("⚠️ Sim, Limpar Tudo", callback_data="confirm_emotion_reset"),
            InlineKeyboardButton("❌ Cancelar", callback_data="emotions_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "⚠️ **CONFIRMAR LIMPEZA**\n\n"
        "Tem certeza que quer limpar todo o histórico emocional?\n"
        "Esta ação não pode ser desfeita.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def execute_emotion_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executar reset do sistema de emoções"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    try:
        from src.emotion_system import EmotionSystem
        emotion_system = EmotionSystem()
        
        success = emotion_system.reset_user_emotions(user_id)
        
        if success:
            await query.edit_message_text(
                "✅ **HISTÓRICO EMOCIONAL LIMPO**\n\n"
                "Todos os dados emocionais foram removidos.\n"
                "O sistema começará a aprender suas emoções novamente."
            )
        else:
            await query.edit_message_text("❌ Erro ao limpar histórico emocional.")
    
    except Exception as e:
        logger.error(f"Erro ao resetar emoções: {e}")
        await query.edit_message_text("❌ Erro interno ao limpar emoções.")