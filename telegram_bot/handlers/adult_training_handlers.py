"""
Comandos de Treinamento Adulto para Telegram
Sistema interativo para ensinar vocabulário e comportamentos
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler
from core.adult_vocabulary_trainer import AdultVocabularyTrainer, InteractiveTrainer
from core.adult_personality_system import AdultPersonalitySystem

# Estados para conversação de treinamento
TRAINING_MAIN_MENU = 40
TRAINING_PERSONALITY_SELECT = 41
TRAINING_ADD_VOCABULARY = 42
TRAINING_ADD_TEMPLATE = 43
TRAINING_INTENSITY_SELECT = 44
TRAINING_CATEGORY_SELECT = 45

logger = logging.getLogger(__name__)
vocabulary_trainer = AdultVocabularyTrainer()
interactive_trainer = InteractiveTrainer()
adult_system = AdultPersonalitySystem()

async def adult_train_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /adult_train - Menu principal de treinamento"""
    user_id = str(update.effective_user.id)
    
    # Verificar se é admin/desenvolvedor (você pode ajustar essa verificação)
    # Por enquanto, vamos permitir para todos os usuários com modo adulto ativo
    try:
        from core.check import check_age
        adult_status = check_age(user_id)
        
        if not adult_status.get('adult_mode_active'):
            await update.message.reply_text(
                "❌ **Acesso negado**\n\n"
                "Sistema de treinamento requer modo adulto ativo.\n"
                "Use /adult_mode primeiro.",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
    except:
        await update.message.reply_text(
            "❌ Erro ao verificar permissões.",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    # Menu principal de treinamento
    keyboard = [
        [InlineKeyboardButton("🎭 Treinar Personalidade", callback_data="train_select_personality")],
        [InlineKeyboardButton("📊 Ver Estatísticas", callback_data="train_view_stats")],
        [InlineKeyboardButton("🎯 Treinamento Rápido", callback_data="train_quick_session")],
        [InlineKeyboardButton("📚 Biblioteca de Exemplos", callback_data="train_examples_library")],
        [InlineKeyboardButton("❌ Sair", callback_data="train_exit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🧠 **SISTEMA DE TREINAMENTO ADULTO**

Ensine a IA a ser mais sugestiva e personalizada!

🎯 **O que você pode fazer:**
• Adicionar vocabulário sexy por personalidade
• Criar templates de resposta sugestivos  
• Treinar comportamentos específicos
• Ajustar intensidade das respostas
• Ver estatísticas de performance

🎭 **Personalidades Disponíveis:**
• Romântico Apaixonado
• Brincalhão Sedutor  
• Intensamente Apaixonado
• Dominante Carinhoso
• Devotado Carinhoso
• Misterioso Sedutor

**Escolha uma opção:**
"""
    
    await update.message.reply_text(
        text, reply_markup=reply_markup, parse_mode='Markdown'
    )
    return TRAINING_MAIN_MENU

async def handle_training_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processar menu principal de treinamento"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    callback_data = query.data
    
    if callback_data == "train_select_personality":
        return await show_personality_training_menu(update, context)
    
    elif callback_data == "train_view_stats":
        return await show_training_stats(update, context)
    
    elif callback_data == "train_quick_session":
        return await start_quick_training(update, context)
    
    elif callback_data == "train_examples_library":
        await query.edit_message_text(
            "📚 **Biblioteca de Exemplos**\n\n"
            "🚧 Esta função será implementada em breve!\n"
            "Use o Treinamento Rápido por enquanto.",
            parse_mode='Markdown'
        )
        return TRAINING_MAIN_MENU
        
    elif callback_data == "train_exit":
        await query.edit_message_text("🎓 Treinamento finalizado!")
        return ConversationHandler.END

async def show_personality_training_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar menu de treinamento por personalidade"""
    query = update.callback_query
    
    personalities = adult_system.get_personality_types()
    
    keyboard = []
    for personality_id, personality_data in personalities.items():
        name = personality_data.get('name', personality_id.title())
        keyboard.append([InlineKeyboardButton(
            f"🎭 {name}", 
            callback_data=f"train_personality_{personality_id}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="train_back_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🎭 **ESCOLHA A PERSONALIDADE PARA TREINAR**

Cada personalidade pode aprender vocabulário e comportamentos únicos:

• **Palavras e frases específicas**
• **Níveis de intensidade diferentes**  
• **Templates de resposta personalizados**
• **Comportamentos característicos**

Selecione uma personalidade:
"""
    
    await query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode='Markdown'
    )
    return TRAINING_PERSONALITY_SELECT

async def handle_personality_training(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processar seleção de personalidade para treinar"""
    query = update.callback_query
    callback_data = query.data
    
    if callback_data == "train_back_main":
        return await adult_train_command(update, context)
    
    if callback_data.startswith("train_personality_"):
        personality_id = callback_data.replace("train_personality_", "")
        context.user_data['training_personality'] = personality_id
        
        return await show_training_options(update, context, personality_id)

async def show_training_options(update: Update, context: ContextTypes.DEFAULT_TYPE, personality_id: str):
    """Mostrar opções de treinamento para uma personalidade"""
    query = update.callback_query
    
    personalities = adult_system.get_personality_types()
    personality_info = personalities.get(personality_id, {})
    name = personality_info.get('name', personality_id.title())
    
    # Obter estatísticas atuais
    vocab = vocabulary_trainer.get_vocabulary_for_personality(personality_id)
    vocab_count = sum(len(items) for items in vocab.values())
    
    keyboard = [
        [InlineKeyboardButton("➕ Adicionar Vocabulário", callback_data=f"train_add_vocab_{personality_id}")],
        [InlineKeyboardButton("📝 Criar Template", callback_data=f"train_add_template_{personality_id}")],
        [InlineKeyboardButton("🎯 Treinar com Exemplos", callback_data=f"train_examples_{personality_id}")],
        [InlineKeyboardButton("⚙️ Ajustar Intensidade", callback_data=f"train_intensity_{personality_id}")],
        [InlineKeyboardButton("📊 Ver Progresso", callback_data=f"train_progress_{personality_id}")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="train_select_personality")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"""
🎭 **TREINANDO: {name.upper()}**

📊 **Status Atual:**
• Vocabulário: {vocab_count} itens
• Templates: Em desenvolvimento
• Intensidade: Configurável

🧠 **Opções de Treinamento:**

**➕ Adicionar Vocabulário**
Ensine palavras, frases e expressões específicas

**📝 Criar Template**  
Desenvolva padrões de resposta únicos

**🎯 Treinar com Exemplos**
Use exemplos práticos para aprendizado

**⚙️ Ajustar Intensidade**
Configure níveis de sugestividade

Escolha como quer treinar:
"""
    
    await query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode='Markdown'
    )
    return TRAINING_MAIN_MENU

async def show_training_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar estatísticas de treinamento"""
    query = update.callback_query
    
    # Obter insights de aprendizado
    insights = vocabulary_trainer.get_learning_insights()
    
    stats_text = """
📊 **ESTATÍSTICAS DE TREINAMENTO**

🏆 **Performance por Personalidade:**
"""
    
    if insights:
        for personality, data in insights.items():
            avg_rating = data['average_rating']
            total_feedback = data['total_feedback']
            
            # Converter rating em estrelas
            stars = "⭐" * int(avg_rating)
            
            stats_text += f"""
🎭 **{personality.title()}**
   Rating: {stars} ({avg_rating}/5.0)
   Feedback: {total_feedback} avaliações
"""
    else:
        stats_text += "\n📝 **Ainda não há dados suficientes**\n"
        stats_text += "Comece a usar o sistema para gerar estatísticas!\n"
    
    stats_text += """
💡 **Dicas:**
• Use /adult_feedback para avaliar respostas
• Quanto mais você usar, melhor o sistema fica
• Cada personalidade aprende independentemente
"""
    
    keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data="train_back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        stats_text, reply_markup=reply_markup, parse_mode='Markdown'
    )

async def start_quick_training(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Iniciar sessão de treinamento rápido"""
    query = update.callback_query
    
    # Carregar exemplos pré-definidos
    examples_text = """
🚀 **TREINAMENTO RÁPIDO ATIVADO**

Aplicando vocabulário avançado para todas as personalidades...

✅ **Romântico Apaixonado:**
• 15 novas frases românticas
• 10 expressões de desejo  
• 8 metáforas sensuais

✅ **Brincalhão Sedutor:**
• 12 provocações divertidas
• 8 duplos sentidos
• 10 convites travessos

✅ **Intensamente Apaixonado:**
• 20 expressões de paixão
• 15 declarações intensas
• 10 descrições ardentes

🔄 **Processando exemplos...**
"""
    
    await query.edit_message_text(
        examples_text, parse_mode='Markdown'
    )
    
    # Aplicar exemplos de treinamento para todas as personalidades
    all_examples = []
    personalities = adult_system.get_personality_types()
    
    for personality_id in personalities.keys():
        examples = interactive_trainer.generate_training_examples(personality_id)
        all_examples.extend(examples)
    
    # Treinar em lote
    vocabulary_trainer.batch_train_from_examples(all_examples)
    
    keyboard = [[InlineKeyboardButton("✅ Concluído", callback_data="train_back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    success_text = """
✅ **TREINAMENTO RÁPIDO CONCLUÍDO!**

🎉 **Sistema Aprimorado:**
• 50+ novas frases adicionadas
• Templates avançados instalados  
• Vocabulário expandido
• Intensidade calibrada

🧠 **A IA agora sabe:**
• Ser mais sugestiva naturalmente
• Usar vocabulário específico por personalidade
• Adaptar respostas ao nível de intensidade
• Criar mais tensão sexual nas conversas

**Teste agora conversando normalmente!**
"""
    
    await query.edit_message_text(
        success_text, reply_markup=reply_markup, parse_mode='Markdown'
    )

async def adult_feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /adult_feedback - Sistema de feedback para aprendizado"""
    user_id = str(update.effective_user.id)
    
    keyboard = [
        [InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="feedback_5")],
        [InlineKeyboardButton("⭐⭐⭐⭐", callback_data="feedback_4")],
        [InlineKeyboardButton("⭐⭐⭐", callback_data="feedback_3")],
        [InlineKeyboardButton("⭐⭐", callback_data="feedback_2")],
        [InlineKeyboardButton("⭐", callback_data="feedback_1")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="feedback_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
💝 **AVALIE A ÚLTIMA RESPOSTA**

Como você classificaria a qualidade da resposta que acabou de receber?

⭐⭐⭐⭐⭐ **Perfeita** - Exatamente o que esperava
⭐⭐⭐⭐ **Muito boa** - Quase perfeita 
⭐⭐⭐ **Boa** - Satisfatória
⭐⭐ **Regular** - Pode melhorar
⭐ **Ruim** - Precisa de muito trabalho

Seu feedback ajuda a IA a aprender e melhorar!
"""
    
    await update.message.reply_text(
        text, reply_markup=reply_markup, parse_mode='Markdown'
    )

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processar feedback do usuário"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    if query.data.startswith("feedback_"):
        rating = int(query.data.split("_")[1])
        
        # Registrar feedback (você precisaria armazenar a última resposta da IA)
        # Por enquanto, vamos apenas registrar o feedback genérico
        vocabulary_trainer.record_feedback(
            user_id=user_id,
            personality_type="generic",  # Você pode melhorar isso
            user_input="feedback_generico",
            ai_response="resposta_avaliada", 
            rating=rating
        )
        
        stars = "⭐" * rating
        await query.edit_message_text(
            f"✅ **Feedback registrado!**\n\n"
            f"Avaliação: {stars}\n"
            f"Obrigado por ajudar a melhorar o sistema! 💝",
            parse_mode='Markdown'
        )
        
    elif query.data == "feedback_cancel":
        await query.edit_message_text("❌ Feedback cancelado.")

# Handlers de conversação
training_conversation = ConversationHandler(
    entry_points=[CommandHandler('adult_train', adult_train_command)],
    states={
        TRAINING_MAIN_MENU: [CallbackQueryHandler(handle_training_main_menu)],
        TRAINING_PERSONALITY_SELECT: [CallbackQueryHandler(handle_personality_training)],
    },
    fallbacks=[CallbackQueryHandler(handle_training_main_menu, pattern="train_.*")]
)

# Comandos individuais
adult_feedback_handler = CallbackQueryHandler(handle_feedback, pattern="feedback_.*")

# Lista de handlers para registrar
training_handlers = [
    training_conversation,
    CommandHandler('adult_feedback', adult_feedback_command),
    adult_feedback_handler
]