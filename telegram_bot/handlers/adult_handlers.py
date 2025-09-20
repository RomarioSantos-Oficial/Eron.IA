"""
Handlers para sistema adulto/NSFW
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

# Estados para sistema adulto
ADULT_TERMS = 30
ADULT_AGE_VERIFICATION = 31

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_adult_activation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Iniciar processo de ativação do modo adulto"""
    user_id = str(update.effective_user.id)
    
    # Verificar se já está ativado
    try:
        from src.check import check_age
        adult_status = check_age(user_id)
        
        if adult_status.get('adult_mode_active'):
            await update.message.reply_text(
                "🔞 **Modo adulto já está ativo!**\n\n"
                "Use /adult_config para configurações ou /adult_status para ver o status."
            )
            return ConversationHandler.END
    except:
        pass
    
    # Mostrar termos e condições
    keyboard = [
        [InlineKeyboardButton("✅ Aceito", callback_data="adult_accept_terms")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="adult_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    terms_text = """
🔞 **ATIVAÇÃO DO MODO ADULTO**

⚠️ **IMPORTANTE**: Este modo permite conversas de natureza adulta.

**Termos e Condições:**
• Você deve ter 18 anos ou mais
• Conteúdo adulto será gerado apenas mediante solicitação
• O uso é de sua responsabilidade
• Dados são privados e seguros
• Você pode desativar a qualquer momento

**Você concorda com os termos?**
"""
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            terms_text, reply_markup=reply_markup, parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            terms_text, reply_markup=reply_markup, parse_mode='Markdown'
        )

async def handle_adult_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler principal para callbacks do sistema adulto"""
    query = update.callback_query
    callback_data = query.data
    user_id = str(query.from_user.id)
    
    try:
        if callback_data == "adult_accept_terms":
            await handle_adult_terms_acceptance(update, context)
        
        elif callback_data == "adult_cancel":
            await cancel_adult_activation(update, context)
        
        elif callback_data == "verify_adult_age":
            await request_age_verification(update, context)
        
        elif callback_data == "adult_config_menu":
            await show_adult_config_menu(update, context)
        
        elif callback_data == "deactivate_adult":
            await confirm_adult_deactivation(update, context)
        
        elif callback_data == "confirm_deactivate_adult":
            await deactivate_adult_mode(update, context)
        
        elif callback_data.startswith("adult_gender_"):
            await set_adult_gender(update, context)
        
        elif callback_data == "adult_status_check":
            await show_adult_status(update, context)
    
    except Exception as e:
        logger.error(f"Erro em sistema adulto: {e}")
        await query.edit_message_text("❌ Erro ao processar solicitação adulta.")

async def handle_adult_terms_acceptance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processar aceitação dos termos"""
    keyboard = [
        [InlineKeyboardButton("🔞 Sim, tenho 18+", callback_data="verify_adult_age")],
        [InlineKeyboardButton("❌ Não, cancelar", callback_data="adult_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🎂 **VERIFICAÇÃO DE IDADE**\n\n"
        "Para ativar o modo adulto, confirme que você tem 18 anos ou mais.\n\n"
        "Esta é uma verificação de responsabilidade legal.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def request_age_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Solicitar verificação de idade"""
    user_id = str(update.callback_query.from_user.id)
    
    try:
        from src.check import activate_adult_mode
        
        # Ativar modo adulto
        success = activate_adult_mode(user_id)
        
        if success:
            keyboard = [
                [InlineKeyboardButton("⚙️ Configurar", callback_data="adult_config_menu")],
                [InlineKeyboardButton("📊 Status", callback_data="adult_status_check")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                "✅ **MODO ADULTO ATIVADO**\n\n"
                "O modo adulto foi ativado com sucesso!\n\n"
                "• Conversas adultas agora são permitidas\n"
                "• Use com responsabilidade\n"
                "• Dados permanecem privados\n\n"
                "Use /adult_config para configurações.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.callback_query.edit_message_text("❌ Erro ao ativar modo adulto.")
    
    except Exception as e:
        logger.error(f"Erro ao verificar idade: {e}")
        await update.callback_query.edit_message_text("❌ Erro na verificação de idade.")

async def show_adult_config_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar menu de configurações adultas"""
    keyboard = [
        [
            InlineKeyboardButton("♀️ Feminino", callback_data="adult_gender_feminine"),
            InlineKeyboardButton("♂️ Masculino", callback_data="adult_gender_masculine")
        ],
        [
            InlineKeyboardButton("📊 Status", callback_data="adult_status_check"),
            InlineKeyboardButton("🔒 Desativar", callback_data="deactivate_adult")
        ],
        [InlineKeyboardButton("❌ Fechar", callback_data="close_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
⚙️ **CONFIGURAÇÕES ADULTAS**

Configure como o modo adulto deve funcionar:

• **Gênero**: Como deve se dirigir a você
• **Status**: Ver informações do modo adulto
• **Desativar**: Remover modo adulto
"""
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text, reply_markup=reply_markup, parse_mode='Markdown'
        )

async def show_adult_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar status do modo adulto"""
    user_id = str(update.callback_query.from_user.id)
    
    try:
        from src.check import check_age
        adult_data = check_age(user_id)
        
        if adult_data.get('adult_mode_active'):
            status_text = "🔞 **MODO ADULTO ATIVO**\n\n"
            status_text += f"• **Status**: Ativado\n"
            status_text += f"• **Gênero**: {adult_data.get('gender', 'Não definido')}\n"
            status_text += f"• **Ativado em**: {adult_data.get('activation_date', 'N/A')}\n"
        else:
            status_text = "❌ **MODO ADULTO INATIVO**\n\nUse /adult_mode para ativar."
        
        keyboard = [
            [InlineKeyboardButton("⚙️ Configurações", callback_data="adult_config_menu")],
            [InlineKeyboardButton("❌ Fechar", callback_data="close_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            status_text, reply_markup=reply_markup, parse_mode='Markdown'
        )
    
    except Exception as e:
        logger.error(f"Erro ao verificar status adulto: {e}")
        await update.callback_query.edit_message_text("❌ Erro ao carregar status.")

async def set_adult_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Definir gênero para modo adulto"""
    query = update.callback_query
    callback_data = query.data
    user_id = str(query.from_user.id)
    
    try:
        gender = callback_data.split('_')[2]  # adult_gender_feminine -> feminine
        
        # Salvar gênero adulto
        from src.check import set_adult_gender as save_adult_gender
        success = save_adult_gender(user_id, gender)
        
        if success:
            await query.answer("✅ Gênero salvo!")
            await show_adult_config_menu(update, context)
        else:
            await query.answer("❌ Erro ao salvar gênero")
    
    except Exception as e:
        logger.error(f"Erro ao salvar gênero adulto: {e}")
        await query.answer("❌ Erro interno")

async def confirm_adult_deactivation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirmar desativação do modo adulto"""
    keyboard = [
        [
            InlineKeyboardButton("⚠️ Sim, Desativar", callback_data="confirm_deactivate_adult"),
            InlineKeyboardButton("❌ Cancelar", callback_data="adult_config_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "⚠️ **CONFIRMAR DESATIVAÇÃO**\n\n"
        "Tem certeza que quer desativar o modo adulto?\n"
        "Todas as configurações adultas serão removidas.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def deactivate_adult_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Desativar modo adulto"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    try:
        from src.check import deactivate_adult_mode as deactivate_adult
        success = deactivate_adult(user_id)
        
        if success:
            await query.edit_message_text(
                "✅ **MODO ADULTO DESATIVADO**\n\n"
                "O modo adulto foi desativado com sucesso.\n"
                "Todas as configurações foram removidas.\n\n"
                "Use /adult_mode para reativar quando desejar."
            )
        else:
            await query.edit_message_text("❌ Erro ao desativar modo adulto.")
    
    except Exception as e:
        logger.error(f"Erro ao desativar modo adulto: {e}")
        await query.edit_message_text("❌ Erro interno ao desativar modo adulto.")

async def cancel_adult_activation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancelar ativação do modo adulto"""
    await update.callback_query.edit_message_text(
        "❌ **ATIVAÇÃO CANCELADA**\n\n"
        "A ativação do modo adulto foi cancelada.\n"
        "Use /adult_mode quando estiver pronto para ativar."
    )
    return ConversationHandler.END