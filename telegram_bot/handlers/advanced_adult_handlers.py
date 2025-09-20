"""
Sistema Adulto Avançado para Telegram Bot
Integração completa com AdultPersonalitySystem
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler
from core.adult_personality_system import AdultPersonalitySystem

# Estados para conversação avançada
ADULT_PERSONALITY_SELECT = 35
ADULT_ADVANCED_CONFIG = 36
ADULT_PREFERENCES_SETUP = 37
ADULT_MOOD_SELECTION = 38

logger = logging.getLogger(__name__)
adult_system = AdultPersonalitySystem()

async def adult_config_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /adult_config - Menu principal de configuração"""
    user_id = str(update.effective_user.id)
    
    # Verificar se modo adulto está ativo
    try:
        from core.check import check_age
        adult_status = check_age(user_id)
        
        if not adult_status.get('adult_mode_active'):
            await update.message.reply_text(
                "❌ **Modo adulto não está ativo**\n\n"
                "Use /adult_mode para ativar primeiro.",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
    except:
        await update.message.reply_text(
            "❌ Erro ao verificar status adulto. Use /adult_mode primeiro.",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    # Verificar se já tem perfil avançado
    profile = adult_system.get_adult_profile(user_id)
    
    if profile:
        return await show_existing_profile_menu(update, context, profile)
    else:
        return await show_personality_selection_menu(update, context)

async def show_personality_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar menu de seleção de personalidade"""
    personalities = adult_system.get_personality_types()
    
    keyboard = []
    for personality_id, personality_data in personalities.items():
        emoji = personality_data.get('emoji', '🎭')
        name = personality_data.get('name', personality_id.title())
        description = personality_data.get('short_description', '')
        
        keyboard.append([InlineKeyboardButton(
            f"{emoji} {name} - {description[:20]}...", 
            callback_data=f"select_personality_{personality_id}"
        )])
    
    keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="cancel_adult_config")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🎭 **CONFIGURAÇÃO AVANÇADA ADULTA**

Escolha sua personalidade base:

� **Romântico Apaixonado** - Conexão emocional profunda
🎯 **Brincalhão Sedutor** - Divertido e espontâneo  
� **Intensamente Apaixonado** - Paixão ardente e intensa
� **Dominante Carinhoso** - Liderança carinhosa
💖 **Devotado Carinhoso** - Foco em agradar e cuidar
� **Misterioso Sedutor** - Charme enigmático

Após escolher, você poderá ajustar todos os parâmetros!
"""
    
    await update.message.reply_text(
        text, reply_markup=reply_markup, parse_mode='Markdown'
    )
    return ADULT_PERSONALITY_SELECT

async def show_existing_profile_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, profile):
    """Mostrar menu para perfil existente"""
    personality_type = profile.get('personality_type', 'Não definido')
    personalities = adult_system.get_personality_types()
    personality_info = personalities.get(personality_type, {})
    
    keyboard = [
        [InlineKeyboardButton("⚙️ Ajustar Configurações", callback_data="adjust_adult_config")],
        [InlineKeyboardButton("🎭 Mudar Personalidade", callback_data="change_personality")],
        [InlineKeyboardButton("🌡️ Definir Humor", callback_data="set_mood")],
        [InlineKeyboardButton("📊 Ver Estatísticas", callback_data="view_adult_stats")],
        [InlineKeyboardButton("🔄 Resetar Perfil", callback_data="reset_adult_profile")],
        [InlineKeyboardButton("❌ Fechar", callback_data="close_adult_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    emoji = personality_info.get('emoji', '🎭')
    name = personality_info.get('name', personality_type.title())
    
    text = f"""
🎯 **SEU PERFIL ADULTO ATUAL**

🎭 **Personalidade**: {emoji} {name}
📊 **Configurações**:
• Confiança: {profile.get('confidence_level', 0)}%
• Brincadeira: {profile.get('playfulness', 0)}%
• Dominância: {profile.get('dominance', 0)}%
• Intimidade: {profile.get('intimacy_level', 0)}%
• Criatividade: {profile.get('creativity', 0)}%
• Responsividade: {profile.get('responsiveness', 0)}%

🌡️ **Humor Atual**: {profile.get('current_mood', 'Neutro')}

O que deseja fazer?
"""
    
    await update.message.reply_text(
        text, reply_markup=reply_markup, parse_mode='Markdown'
    )
    return ADULT_ADVANCED_CONFIG

async def handle_personality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processar seleção de personalidade"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    callback_data = query.data
    
    if callback_data.startswith("select_personality_"):
        personality_id = callback_data.replace("select_personality_", "")
        
        # Salvar personalidade selecionada no contexto
        context.user_data['selected_personality'] = personality_id
        
        # Mostrar configurações detalhadas
        return await show_detailed_config(update, context, personality_id)
        
    elif callback_data == "cancel_adult_config":
        await query.edit_message_text("❌ Configuração cancelada.")
        return ConversationHandler.END

async def show_detailed_config(update: Update, context: ContextTypes.DEFAULT_TYPE, personality_id):
    """Mostrar configurações detalhadas para personalidade"""
    query = update.callback_query
    
    personalities = adult_system.get_personality_types()
    personality_data = personalities.get(personality_id, {})
    
    emoji = personality_data.get('emoji', '🎭')
    name = personality_data.get('name', personality_id.title())
    description = personality_data.get('description', 'Personalidade única')
    
    # Valores padrão da personalidade
    defaults = personality_data.get('defaults', {})
    
    keyboard = [
        [InlineKeyboardButton("✅ Usar Configuração Padrão", callback_data=f"use_default_{personality_id}")],
        [InlineKeyboardButton("⚙️ Personalizar Valores", callback_data=f"customize_{personality_id}")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="back_to_personality_selection")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"""
{emoji} **{name.upper()}**

📝 **Descrição**: {description}

⚙️ **Configurações Padrão**:
• Confiança: {defaults.get('confidence_level', 75)}%
• Brincadeira: {defaults.get('playfulness', 70)}%
• Dominância: {defaults.get('dominance', 50)}%
• Intimidade: {defaults.get('intimacy_level', 60)}%
• Criatividade: {defaults.get('creativity', 80)}%
• Responsividade: {defaults.get('responsiveness', 85)}%

**Escolha uma opção**:
"""
    
    await query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode='Markdown'
    )
    return ADULT_PREFERENCES_SETUP

async def handle_config_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processar escolha de configuração"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    callback_data = query.data
    
    if callback_data.startswith("use_default_"):
        personality_id = callback_data.replace("use_default_", "")
        
        # Criar perfil com valores padrão
        personalities = adult_system.get_personality_types()
        personality_data = personalities.get(personality_id, {})
        defaults = personality_data.get('defaults', {})
        
        profile_data = {
            'personality_type': personality_id,
            **defaults
        }
        
        try:
            adult_system.create_adult_profile(user_id, profile_data)
            
            emoji = personality_data.get('emoji', '🎭')
            name = personality_data.get('name', personality_id.title())
            
            await query.edit_message_text(
                f"✅ **PERFIL CRIADO COM SUCESSO!**\n\n"
                f"🎭 **Personalidade**: {emoji} {name}\n"
                f"📊 **Configuração**: Padrão\n\n"
                f"Agora suas conversas adultas terão essa personalidade!\n\n"
                f"Use /adult_config para ajustar ou /adult_status para ver detalhes.",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Erro ao criar perfil: {e}")
            await query.edit_message_text("❌ Erro ao criar perfil. Tente novamente.")
            return ConversationHandler.END
            
    elif callback_data.startswith("customize_"):
        await query.edit_message_text(
            "⚙️ **Customização Avançada**\n\n"
            "🚧 Esta função será implementada em breve!\n"
            "Por enquanto, use a configuração padrão.\n\n"
            "Use /adult_config para tentar novamente.",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
        
    elif callback_data == "back_to_personality_selection":
        return await show_personality_selection_menu(update, context)

async def adult_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /adult_status - Mostrar status atual"""
    user_id = str(update.effective_user.id)
    
    try:
        from core.check import check_age
        adult_status = check_age(user_id)
        
        if not adult_status.get('adult_mode_active'):
            await update.message.reply_text(
                "❌ **Modo adulto não está ativo**\n\n"
                "Use /adult_mode para ativar.",
                parse_mode='Markdown'
            )
            return
    except:
        await update.message.reply_text(
            "❌ Erro ao verificar status.",
            parse_mode='Markdown'
        )
        return
    
    # Buscar perfil avançado
    profile = adult_system.get_adult_profile(user_id)
    
    if profile:
        personality_type = profile.get('personality_type', 'Não definido')
        personalities = adult_system.get_personality_types()
        personality_info = personalities.get(personality_type, {})
        
        emoji = personality_info.get('emoji', '🎭')
        name = personality_info.get('name', personality_type.title())
        
        # Buscar estatísticas
        sessions = adult_system.get_user_session_history(user_id)
        total_sessions = len(sessions) if sessions else 0
        
        text = f"""
🎯 **STATUS DO MODO ADULTO**

✅ **Status**: Ativo com perfil avançado
🎭 **Personalidade**: {emoji} {name}

📊 **Configurações Atuais**:
• Confiança: {profile.get('confidence_level', 0)}%
• Brincadeira: {profile.get('playfulness', 0)}%
• Dominância: {profile.get('dominance', 0)}%
• Intimidade: {profile.get('intimacy_level', 0)}%
• Criatividade: {profile.get('creativity', 0)}%
• Responsividade: {profile.get('responsiveness', 0)}%

🌡️ **Humor Atual**: {profile.get('current_mood', 'Neutro')}
📈 **Sessões Realizadas**: {total_sessions}

🔧 Use /adult_config para modificar
"""
    else:
        text = """
🎯 **STATUS DO MODO ADULTO**

✅ **Status**: Ativo (configuração básica)
❓ **Perfil Avançado**: Não configurado

🎭 Para uma experiência personalizada:
• Use /adult_config para criar perfil avançado
• Escolha entre 6 personalidades diferentes
• Configure parâmetros detalhados
• Sistema de humores e feedback

🚀 **Upgrade para o sistema avançado agora!**
"""
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def adult_mood_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /adult_mood - Definir humor"""
    user_id = str(update.effective_user.id)
    
    # Verificar se tem perfil avançado
    profile = adult_system.get_adult_profile(user_id)
    
    if not profile:
        await update.message.reply_text(
            "❌ **Perfil avançado não encontrado**\n\n"
            "Use /adult_config para criar primeiro.",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    # Mostrar opções de humor
    moods = ['apaixonada', 'travessa', 'dominante', 'carinhosa', 'misteriosa', 'brincalhona', 'sensual', 'romântica']
    
    keyboard = []
    mood_emojis = {
        'apaixonada': '💕',
        'travessa': '😈', 
        'dominante': '🔥',
        'carinhosa': '😊',
        'misteriosa': '🌙',
        'brincalhona': '😜',
        'sensual': '💋',
        'romântica': '🌹'
    }
    
    for mood in moods:
        emoji = mood_emojis.get(mood, '🌡️')
        keyboard.append([InlineKeyboardButton(
            f"{emoji} {mood.title()}", 
            callback_data=f"set_mood_{mood}"
        )])
    
    keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="cancel_mood")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    current_mood = profile.get('current_mood', 'Neutro')
    
    await update.message.reply_text(
        f"🌡️ **DEFINIR HUMOR**\n\n"
        f"**Humor atual**: {current_mood}\n\n"
        f"Escolha o novo humor para suas conversas:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return ADULT_MOOD_SELECTION

async def handle_mood_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processar seleção de humor"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    callback_data = query.data
    
    if callback_data.startswith("set_mood_"):
        mood = callback_data.replace("set_mood_", "")
        
        try:
            # Atualizar humor no perfil
            adult_system.update_user_mood(user_id, mood)
            
            mood_emojis = {
                'apaixonada': '💕',
                'travessa': '😈', 
                'dominante': '🔥',
                'carinhosa': '😊',
                'misteriosa': '🌙',
                'brincalhona': '😜',
                'sensual': '💋',
                'romântica': '🌹'
            }
            
            emoji = mood_emojis.get(mood, '🌡️')
            
            await query.edit_message_text(
                f"✅ **HUMOR DEFINIDO!**\n\n"
                f"🌡️ **Novo humor**: {emoji} {mood.title()}\n\n"
                f"Suas próximas conversas adultas terão essa energia!",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Erro ao definir humor: {e}")
            await query.edit_message_text(
                "❌ Erro ao definir humor. Tente novamente.",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
            
    elif callback_data == "cancel_mood":
        await query.edit_message_text("❌ Definição de humor cancelada.")
        return ConversationHandler.END

# Handlers de conversação
adult_config_conversation = ConversationHandler(
    entry_points=[CommandHandler('adult_config', adult_config_command)],
    states={
        ADULT_PERSONALITY_SELECT: [CallbackQueryHandler(handle_personality_selection)],
        ADULT_PREFERENCES_SETUP: [CallbackQueryHandler(handle_config_choice)],
        ADULT_ADVANCED_CONFIG: [CallbackQueryHandler(handle_personality_selection)],
    },
    fallbacks=[CallbackQueryHandler(handle_personality_selection, pattern="cancel_adult_config")]
)

adult_mood_conversation = ConversationHandler(
    entry_points=[CommandHandler('adult_mood', adult_mood_command)],
    states={
        ADULT_MOOD_SELECTION: [CallbackQueryHandler(handle_mood_selection)],
    },
    fallbacks=[CallbackQueryHandler(handle_mood_selection, pattern="cancel_mood")]
)

# Comandos individuais
adult_status_handler = CommandHandler('adult_status', adult_status_command)

# Lista de handlers para registrar
advanced_adult_handlers = [
    adult_config_conversation,
    adult_mood_conversation, 
    adult_status_handler
]

# Adicionar comandos de descoberta
try:
    from .adult_discovery_commands import discovery_commands
    advanced_adult_handlers.extend(discovery_commands)
except ImportError:
    pass