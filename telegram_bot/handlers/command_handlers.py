"""
Handlers de comandos básicos do bot Telegram
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Apresentação inicial do bot"""
    user_id = str(update.effective_user.id)
    first_name = update.effective_user.first_name or "usuário"
    
    from core.user_profile_db import UserProfileDB as UserService
    user_service = UserService()
    
    # Verificar se usuário já existe
    user_profile = user_service.get_profile(user_id)
    if user_profile:
        user_name = user_profile.get('user_name', first_name)
        await update.message.reply_text(
            f"Oi de novo, {user_name}! 😊 É bom te ver novamente!\n\n"
            f"Como posso te ajudar hoje? Você pode:\n"
            f"• Conversar comigo normalmente\n"
            f"• Usar /menu para ver opções\n"
            f"• Usar /help para ajuda\n"
            f"• Usar /personalizar para ajustar suas preferências"
        )
    else:
        # Usuário novo - mostrar menu de personalização
        keyboard = [
            [InlineKeyboardButton("✨ Sim, personalizar!", callback_data="start_full_personalization")],
            [InlineKeyboardButton("💬 Começar sem personalizar", callback_data="start_conversation")],
            [InlineKeyboardButton("❓ Ajuda", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Olá! Eu sou o Eron, seu assistente de IA personalizado!\n\n"
            "🎯 Para melhorar sua experiência, gostaria de me personalizar?",
            reply_markup=reply_markup
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help - Mostrar ajuda e comandos disponíveis"""
    help_text = """
🤖 **COMANDOS DISPONÍVEIS:**

**Básicos:**
• /start - Iniciar o bot
• /help - Mostrar esta ajuda
• /menu - Menu principal
• /clear - ⚠️ RESETAR todas as configurações

**Personalização:**
• /personalizar - Configurar o bot
• /preferencias - Configurar preferências
• /emocoes - Sistema de emoções

**Sistema Adulto:**
• /adult_mode - Ativar modo adulto
• /adult_config - Configurações adulto
• /adult_status - Status do modo adulto

**Chat:**
• Digite qualquer mensagem para conversar!
• O bot lembra do contexto da conversa
• Use feedback com 👍 👎 para melhorar respostas

**Dicas:**
- Seja específico em suas perguntas
- O bot aprende com suas preferências
- Use /personalizar para ajustar como eu respondo
- ⚠️ /clear apaga TODAS as configurações (irreversível)
"""
    
    await update.message.reply_text(help_text)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /menu - Mostrar menu principal"""
    keyboard = [
        [
            InlineKeyboardButton("🎯 Personalizar", callback_data="start_personalization"),
            InlineKeyboardButton("⚙️ Preferências", callback_data="preferences_menu")
        ],
        [
            InlineKeyboardButton("😊 Emoções", callback_data="emotions_menu"),
            InlineKeyboardButton("🔞 Modo Adulto", callback_data="adult_menu")
        ],
        [
            InlineKeyboardButton("💬 Conversar", callback_data="start_chat"),
            InlineKeyboardButton("❓ Ajuda", callback_data="help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎯 **MENU PRINCIPAL**\n\nEscolha uma opção:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /clear - Resetar/apagar todas as personalizações do bot"""
    user_id = str(update.effective_user.id)
    
    # Log para debug
    print(f"[DEBUG] Comando /clear chamado pelo usuário {user_id}")
    
    try:
        # Importar serviços necessários
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from core.user_profile_db import UserProfileDB as UserService
        
        user_service = UserService()
        
        print(f"[DEBUG] Criando keyboard de confirmação...")
        
        # Criar keyboard de confirmação
        keyboard = [
            [
                InlineKeyboardButton("✅ Sim, Resetar Tudo", callback_data="confirm_clear_all"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_clear")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        print(f"[DEBUG] Enviando mensagem de confirmação...")
        
        await update.message.reply_text(
            "🚨 **RESETAR PERSONALIZAÇÃO**\n\n"
            "⚠️ **ATENÇÃO**: Esta ação irá apagar TODAS suas configurações:\n\n"
            "• Seu nome e informações pessoais\n"
            "• Nome e configurações do bot\n"
            "• Personalidade escolhida\n"
            "• Idioma e tópicos de interesse\n"
            "• Preferências e configurações\n"
            "• Histórico de emoções\n"
            "• Configurações adultas (se ativadas)\n\n"
            "**Esta ação NÃO PODE ser desfeita!**\n\n"
            "Tem certeza que deseja continuar?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        print(f"[DEBUG] Mensagem de confirmação enviada com sucesso!")
        
    except Exception as e:
        print(f"[DEBUG] Erro no comando /clear: {e}")
        await update.message.reply_text(
            "❌ Erro ao processar comando de reset. Tente novamente."
        )
