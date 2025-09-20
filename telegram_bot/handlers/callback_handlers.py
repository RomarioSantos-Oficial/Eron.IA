"""
Handlers de callbacks (botões inline) do bot Telegram
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler principal para callbacks de botões inline"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    user_id = str(query.from_user.id)
    
    try:
        # Importar handlers específicos
        from .personalization_handlers import handle_personalization_callbacks
        from .preferences_handlers import handle_preferences_callbacks
        from .emotions_handlers import handle_emotions_callbacks
        from .adult_handlers import handle_adult_callbacks
        
        logger.info(f"Callback recebido de {user_id}: {callback_data}")
        
        # Roteamento de callbacks
        # Callbacks específicos do fluxo de personalização completa
        if callback_data.startswith("set_user_gender_"):
            await handle_user_gender_selection(update, context)
        
        elif callback_data.startswith("set_bot_gender_"):
            await handle_bot_gender_selection(update, context)
        
        elif callback_data.startswith("select_name_"):
            await handle_name_selection(update, context)
        
        elif callback_data == "custom_bot_name":
            await handle_custom_name_request(update, context)
        
        elif callback_data.startswith("set_personality_"):
            await handle_personality_selection(update, context)
        
        elif callback_data.startswith("set_language_style_"):
            await handle_language_style_selection(update, context)
        
        elif callback_data.startswith("toggle_topic_"):
            await handle_topic_toggle(update, context)
        
        elif callback_data == "finish_personalization":
            await finish_personalization(update, context)
        
        # Callbacks de personalização geral (handlers antigos)
        elif callback_data.startswith(('start_personalization', 'personalize_', 'save_', 'complete_personalization', 'cancel_personalization')):
            await handle_personalization_callbacks(update, context)
        
        elif callback_data.startswith(('preferences_', 'pref_')):
            await handle_preferences_callbacks(update, context)
        
        elif callback_data.startswith(('emotions_', 'emotion_')):
            await handle_emotions_callbacks(update, context)
        
        elif callback_data.startswith(('adult_', 'verify_adult')):
            await handle_adult_callbacks(update, context)
        
        # Callbacks gerais
        elif callback_data == "help":
            await show_help_menu(update, context)
        
        elif callback_data == "start_chat":
            await start_conversation(update, context)
        
        elif callback_data == "close_menu":
            await close_menu(update, context)
        
        elif callback_data == "confirm_clear_all":
            await confirm_clear_all(update, context)
        
        elif callback_data == "cancel_clear":
            await cancel_clear(update, context)
        
        elif callback_data == "start_full_personalization":
            await start_full_personalization(update, context)
        
        elif callback_data == "skip_personalization":
            await skip_personalization(update, context)

        else:
            await query.edit_message_text("❌ Opção não reconhecida.")
    
    except Exception as e:
        logger.error(f"Erro ao processar callback {callback_data}: {e}")
        await query.edit_message_text("❌ Erro interno. Tente novamente.")

async def show_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar menu de ajuda via callback"""
    help_text = """
🤖 **AJUDA DO BOT**

**Como usar:**
• Digite qualquer mensagem para conversar
• Use os botões para navegar pelos menus
• Personalize o bot para uma experiência única

**Comandos:**
• /start - Iniciar
• /menu - Menu principal  
• /help - Esta ajuda
• /personalizar - Configurações
"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_principal")],
        [InlineKeyboardButton("❌ Fechar", callback_data="close_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Iniciar conversação via callback"""
    await update.callback_query.edit_message_text(
        "💬 **Perfeito!** Agora você pode conversar comigo normalmente.\n\n"
        "Apenas digite qualquer mensagem e eu responderei! 😊\n\n"
        "Dica: Use /menu a qualquer momento para ver opções."
    )

async def close_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fechar menu via callback"""
    await update.callback_query.edit_message_text(
        "✅ Menu fechado.\n\n"
        "Digite qualquer mensagem para conversar ou use /menu para ver opções novamente."
    )

async def handle_feedback_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para feedback de mensagens"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    user_id = str(query.from_user.id)
    
    if callback_data.startswith('feedback_'):
        feedback_type = callback_data.split('_')[1]
        message_id = callback_data.split('_')[2] if len(callback_data.split('_')) > 2 else None
        
        try:
            # Registrar feedback
            from learning.feedback_system import FeedbackSystem as FeedbackService
            feedback_service = FeedbackService()
            
            success = feedback_service.register_feedback(
                user_id=user_id,
                message_id=message_id,
                feedback_type=feedback_type,
                platform='telegram'
            )
            
            if success:
                if feedback_type == 'positive':
                    await query.edit_message_text("👍 Obrigado pelo feedback positivo!")
                else:
                    await query.edit_message_text("👎 Obrigado pelo feedback. Vou melhorar!")
            else:
                await query.edit_message_text("❌ Erro ao registrar feedback.")
                
        except Exception as e:
            logger.error(f"Erro ao processar feedback: {e}")
            await query.edit_message_text("❌ Erro interno ao processar feedback.")

async def confirm_clear_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirmar e executar reset completo - iniciar fluxo de personalização"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    try:
        # Importar serviços necessários
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from src.user_profile_db import UserProfileDB as UserService
        from src.memory import EronMemory
        from src.preferences import PreferencesManager
        from src.emotion_system import EmotionSystem
        
        user_service = UserService()
        memory = EronMemory()
        preferences = PreferencesManager()
        emotions = EmotionSystem()
        
        # Resetar dados do usuário no banco
        reset_success = user_service.reset_user_profile(user_id)
        
        # Limpar memória de conversas
        try:
            memory.clear_user_memory(user_id)
        except:
            pass  # Continuar mesmo se houver erro na memória
        
        # Resetar preferências
        try:
            preferences.reset_user_preferences(user_id)
        except:
            pass
        
        # Resetar emoções
        try:
            emotions.reset_user_emotions(user_id)
        except:
            pass
        
        # Limpar dados de contexto do Telegram
        context.user_data.clear()
        
        if reset_success:
            # Iniciar fluxo de personalização completa como primeira vez
            keyboard = [
                [
                    InlineKeyboardButton("✅ Sim, vamos personalizar!", callback_data="start_full_personalization"),
                    InlineKeyboardButton("❌ Não, obrigado", callback_data="skip_personalization")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🎉 **RESET CONCLUÍDO COM SUCESSO!**\n\n"
                "Olá! Eu sou o **Eron**, seu assistente de IA personalizado!\n\n"
                "🎯 Para melhorar sua experiência, gostaria de me personalizar?\n\n"
                "**Com a personalização você pode:**\n"
                "• Escolher seu nome e informações pessoais\n"
                "• Definir meu nome e personalidade\n"
                "• Configurar idioma e tópicos de interesse\n"
                "• Ajustar preferências de conversa\n\n"
                "**Gostaria de começar a personalização completa?**",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "❌ **ERRO NO RESET**\n\n"
                "Houve um problema ao resetar algumas configurações.\n"
                "Tente usar /start para reconfigurar manualmente."
            )
    
    except Exception as e:
        logger.error(f"Erro ao resetar perfil: {e}")
        await query.edit_message_text(
            "❌ **ERRO TÉCNICO**\n\n"
            "Não foi possível completar o reset.\n"
            "Tente novamente em alguns instantes."
        )

async def cancel_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancelar operação de reset"""
    await update.callback_query.edit_message_text(
        "✅ **RESET CANCELADO**\n\n"
        "Suas configurações estão seguras! 😊\n\n"
        "Use /menu para ver outras opções ou continue conversando normalmente."
    )

async def start_full_personalization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Iniciar personalização completa após reset"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    await query.answer()
    
    # Marcar que está iniciando personalização
    context.user_data['personalizing'] = True
    context.user_data['personalization_step'] = 'user_name'
    
    await query.edit_message_text(
        "🎯 **VAMOS COMEÇAR A PERSONALIZAÇÃO!**\n\n"
        "**Passo 1/8: Informações Pessoais**\n\n"
        "👤 Como você gostaria de ser chamado?\n"
        "Digite seu nome ou apelido:",
        parse_mode='Markdown'
    )

async def skip_personalization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pular personalização após reset"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    await query.answer()
    
    # Limpar dados de personalização
    context.user_data.clear()
    
    keyboard = [
        [InlineKeyboardButton("📋 Menu Principal", callback_data="menu_principal")],
        [InlineKeyboardButton("🎨 Personalizar Depois", callback_data="start_personalization")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "👍 **Tudo bem!**\n\n"
        "Você pode personalizar o Eron a qualquer momento usando:\n"
        "• /personalizar - Menu de personalização\n"
        "• /menu - Menu principal\n\n"
        "💬 **Agora você já pode conversar comigo!**\n"
        "Digite qualquer mensagem para começar.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_user_gender_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processar seleção de gênero do usuário"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    gender = query.data.replace("set_user_gender_", "")
    
    print(f"[DEBUG] Processando seleção de gênero: {gender} para usuário {user_id}")
    
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from src.user_profile_db import UserProfileDB as UserService
        
        user_service = UserService()
        print(f"[DEBUG] Salvando gênero {gender} no banco...")
        user_service.update_profile(user_id, user_gender=gender)
        print(f"[DEBUG] Gênero salvo com sucesso!")
        
        # Próximo passo: data de nascimento
        context.user_data['personalization_step'] = 'birth_date'
        
        gender_display = {
            'masculino': '👨 Masculino',
            'feminino': '👩 Feminino',
            'outro': '🌟 Outro',
            'prefiro_nao_dizer': '🤐 Prefiro não dizer'
        }
        
        print(f"[DEBUG] Editando mensagem para próximo passo...")
        
        await query.edit_message_text(
            f"✅ Gênero salvo: **{gender_display.get(gender, gender)}**\n\n"
            "**Passo 3/8: Data de Nascimento**\n\n"
            "📅 Digite sua data de nascimento no formato **DD/MM/AAAA**\n"
            "Exemplo: 25/12/1995\n\n"
            "⚠️ *Sua idade real determinará acesso às funcionalidades*",
            parse_mode='Markdown'
        )
        
        print(f"[DEBUG] Mensagem editada com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao salvar gênero do usuário: {e}")
        print(f"[DEBUG] Erro completo: {e}")
        await query.edit_message_text("❌ Erro ao salvar gênero. Tente novamente.")

async def handle_bot_gender_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processar seleção de gênero do bot"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    gender = query.data.replace("set_bot_gender_", "")
    
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from src.user_profile_db import UserProfileDB as UserService
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        user_service = UserService()
        user_service.update_profile(user_id, bot_gender=gender)
        
        # Próximo passo: nome do bot com sugestões baseadas no gênero
        context.user_data['personalization_step'] = 'bot_name'
        context.user_data['bot_gender'] = gender
        
        gender_display = {
            'masculino': '👨 Masculino',
            'feminino': '👩 Feminino', 
            'neutro': '⚖️ Neutro'
        }
        
        # Sugestões de nomes baseadas no gênero
        names_suggestions = {
            'masculino': ["🤖 Eron", "⚡ Alex", "🎯 Bruno", "🔥 Carlos", "💫 Diego"],
            'feminino': ["🌟 Ana", "� Bella", "🌸 Clara", "✨ Diana", "🦋 Eva"],
            'neutro': ["🔮 Taylor", "🌈 Jordan", "⭐ Morgan", "🎨 Sage", "🌙 Phoenix"]
        }
        
        suggestions = names_suggestions.get(gender, names_suggestions['neutro'])
        
        # Criar keyboard com sugestões + opção personalizada
        keyboard = []
        for name in suggestions:
            callback_name = name.split(" ")[1]  # Remove emoji
            keyboard.append([InlineKeyboardButton(name, callback_data=f"select_name_{callback_name}")])
        
        # Adicionar opção para nome personalizado
        keyboard.append([InlineKeyboardButton("✏️ Outro nome (personalizar)", callback_data="custom_bot_name")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ Gênero do bot salvo: **{gender_display.get(gender, gender)}**\n\n"
            "**Passo 5/8: Nome do Bot**\n\n"
            "🤖 Escolha um nome sugerido ou personalize:\n\n"
            "💡 *Dica: Os nomes sugeridos foram selecionados com base no gênero escolhido*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro ao salvar gênero do bot: {e}")
        await query.edit_message_text("❌ Erro ao salvar gênero. Tente novamente.")

async def handle_personality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processar seleção de personalidade do bot"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    personality = query.data.replace("set_personality_", "")
    
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from src.user_profile_db import UserProfileDB as UserService
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        user_service = UserService()
        user_service.update_profile(user_id, bot_personality=personality)
        
        # Próximo passo: estilo de linguagem
        context.user_data['personalization_step'] = 'language_style'
        
        personality_display = {
            'amigavel': '😊 Amigável',
            'profissional': '💼 Profissional',
            'divertido': '🎉 Divertido',
            'formal': '🎭 Formal'
        }
        
        keyboard = [
            [InlineKeyboardButton("💬 Informal", callback_data="set_language_style_informal")],
            [InlineKeyboardButton("🎩 Formal", callback_data="set_language_style_formal")],
            [InlineKeyboardButton("🔬 Técnico", callback_data="set_language_style_tecnico")],
            [InlineKeyboardButton("📖 Simples", callback_data="set_language_style_simples")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ Personalidade salva: **{personality_display.get(personality, personality)}**\n\n"
            "**Passo 7/8: Estilo de Linguagem**\n\n"
            "🗣️ Como você prefere que eu me comunique?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro ao salvar personalidade: {e}")
        await query.edit_message_text("❌ Erro ao salvar personalidade. Tente novamente.")

async def handle_language_style_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processar seleção de estilo de linguagem"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    language_style = query.data.replace("set_language_style_", "")
    
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from src.user_profile_db import UserProfileDB as UserService
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        user_service = UserService()
        user_service.update_profile(user_id, bot_language=language_style)
        
        # Próximo passo: tópicos de interesse
        context.user_data['personalization_step'] = 'topics'
        context.user_data['selected_topics'] = []
        
        style_display = {
            'informal': '💬 Informal',
            'formal': '🎩 Formal',
            'tecnico': '🔬 Técnico',
            'simples': '📖 Simples'
        }
        
        # Tópicos disponíveis (mesmos da versão web)
        keyboard = [
            [InlineKeyboardButton("💻 Tecnologia", callback_data="toggle_topic_tecnologia")],
            [InlineKeyboardButton("🔬 Ciência", callback_data="toggle_topic_ciencia")],
            [InlineKeyboardButton("🎨 Arte", callback_data="toggle_topic_arte")],
            [InlineKeyboardButton("📚 Literatura", callback_data="toggle_topic_literatura")],
            [InlineKeyboardButton("🎵 Música", callback_data="toggle_topic_musica")],
            [InlineKeyboardButton("⚽ Esportes", callback_data="toggle_topic_esportes")],
            [InlineKeyboardButton("✈️ Viagens", callback_data="toggle_topic_viagens")],
            [InlineKeyboardButton("🍳 Culinária", callback_data="toggle_topic_culinaria")],
            [InlineKeyboardButton("🏥 Saúde", callback_data="toggle_topic_saude")],
            [InlineKeyboardButton("🤔 Filosofia", callback_data="toggle_topic_filosofia")],
            [InlineKeyboardButton("✅ Finalizar", callback_data="finish_personalization")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ Estilo salvo: **{style_display.get(language_style, language_style)}**\n\n"
            "**Passo 8/8: Tópicos de Interesse**\n\n"
            "📋 Selecione os tópicos que mais te interessam:\n"
            "(Clique nos tópicos para selecioná-los)\n\n"
            "🔹 **Selecionados:** Nenhum ainda\n\n"
            "Quando terminar, clique em ✅ Finalizar",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro ao salvar estilo de linguagem: {e}")
        await query.edit_message_text("❌ Erro ao salvar estilo. Tente novamente.")

async def handle_topic_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processar seleção/deseleção de tópicos de interesse"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    topic = query.data.replace("toggle_topic_", "")
    
    try:
        # Gerenciar lista de tópicos selecionados
        selected_topics = context.user_data.get('selected_topics', [])
        
        if topic in selected_topics:
            selected_topics.remove(topic)
        else:
            selected_topics.append(topic)
        
        context.user_data['selected_topics'] = selected_topics
        
        # Mapeamento de tópicos com emojis
        topic_display = {
            'tecnologia': '💻 Tecnologia',
            'ciencia': '🔬 Ciência',
            'arte': '🎨 Arte',
            'literatura': '📚 Literatura',
            'musica': '🎵 Música',
            'esportes': '⚽ Esportes',
            'viagens': '✈️ Viagens',
            'culinaria': '🍳 Culinária',
            'saude': '🏥 Saúde',
            'filosofia': '🤔 Filosofia'
        }
        
        # Criar keyboard atualizada com marcações
        keyboard = []
        for topic_key, topic_name in topic_display.items():
            if topic_key in selected_topics:
                button_text = f"✅ {topic_name}"
            else:
                button_text = f"⚪ {topic_name}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"toggle_topic_{topic_key}")])
        
        keyboard.append([InlineKeyboardButton("✅ Finalizar", callback_data="finish_personalization")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Mostrar tópicos selecionados
        if selected_topics:
            selected_text = ", ".join([topic_display.get(t, t) for t in selected_topics])
        else:
            selected_text = "Nenhum ainda"
        
        await query.edit_message_text(
            "**Passo 8/8: Tópicos de Interesse**\n\n"
            "📋 Selecione os tópicos que mais te interessam:\n"
            "(Clique nos tópicos para selecioná-los)\n\n"
            f"🔹 **Selecionados:** {selected_text}\n\n"
            "Quando terminar, clique em ✅ Finalizar",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro ao processar tópico: {e}")
        await query.edit_message_text("❌ Erro ao processar tópico. Tente novamente.")

async def finish_personalization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Finalizar o processo de personalização completa"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from src.user_profile_db import UserProfileDB as UserService
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        user_service = UserService()
        
        # Salvar tópicos selecionados
        selected_topics = context.user_data.get('selected_topics', [])
        if selected_topics:
            topics_str = ",".join(selected_topics)
            user_service.update_profile(user_id, preferred_topics=topics_str)
        
        # Obter dados do usuário para resumo
        user_data = user_service.get_profile(user_id)
        user_age = context.user_data.get('user_age', 0)
        
        # Limpar dados temporários
        context.user_data.clear()
        
        # Criar resumo da personalização
        summary = f"""🎉 **PERSONALIZAÇÃO CONCLUÍDA!**

👤 **Suas Informações:**
• Nome: {user_data.get('user_name', 'Não informado')}
• Gênero: {user_data.get('user_gender', 'Não informado')}
• Idade: {user_age} anos

🤖 **Configurações do Bot:**
• Nome: {user_data.get('bot_name', 'Eron')}
• Gênero: {user_data.get('bot_gender', 'Masculino')}
• Personalidade: {user_data.get('bot_personality', 'Amigável')}
• Linguagem: {user_data.get('bot_language', 'Informal')}

📋 **Tópicos de Interesse:**
{', '.join(selected_topics) if selected_topics else 'Nenhum selecionado'}

✨ **Agora estou totalmente personalizado para você!**"""
        
        keyboard = [
            [InlineKeyboardButton("💬 Começar a Conversar", callback_data="start_chat")],
            [InlineKeyboardButton("📋 Menu Principal", callback_data="menu_principal")]
        ]
        
        # Se for maior de 18, mencionar configurações adultas disponíveis no menu
        if user_age >= 18:
            summary += "\n\n🔞 **Nota:** Configurações adultas disponíveis no menu /personalizar"
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            summary,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro ao finalizar personalização: {e}")
        await query.edit_message_text(
            "✅ **Personalização concluída!**\n\n"
            "💬 Agora você pode conversar comigo normalmente.\n"
            "Use /menu para acessar outras opções."
        )

async def handle_name_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processar seleção de nome sugerido"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    selected_name = query.data.replace("select_name_", "")
    
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from src.user_profile_db import UserProfileDB as UserService
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        user_service = UserService()
        user_service.update_profile(user_id, bot_name=selected_name)
        
        # Próximo passo: personalidade do bot
        context.user_data['personalization_step'] = 'bot_personality'
        
        # Verificar se é maior de idade para mostrar opções adultas
        user_age = context.user_data.get('user_age', 0)
        
        keyboard = [
            [InlineKeyboardButton("😊 Amigável", callback_data="set_personality_amigavel")],
            [InlineKeyboardButton("💼 Profissional", callback_data="set_personality_profissional")],
            [InlineKeyboardButton("🎉 Divertido", callback_data="set_personality_divertido")],
            [InlineKeyboardButton("🎭 Formal", callback_data="set_personality_formal")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ Nome salvo: **{selected_name}**\n\n"
            "**Passo 6/8: Personalidade do Bot**\n\n"
            "🎭 Que personalidade você prefere para mim?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro ao salvar nome selecionado: {e}")
        await query.edit_message_text("❌ Erro ao salvar nome. Tente novamente.")

async def handle_custom_name_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Solicitar nome personalizado"""
    query = update.callback_query
    
    # Definir que o usuário vai digitar um nome personalizado
    context.user_data['personalization_step'] = 'bot_name_custom'
    
    await query.edit_message_text(
        "✏️ **Nome Personalizado**\n\n"
        "🤖 Digite o nome que você gostaria de dar ao seu assistente:\n\n"
        "💡 *Pode ser qualquer nome que você preferir!*"
    )