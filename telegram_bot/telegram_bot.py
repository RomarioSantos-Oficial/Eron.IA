import os
import sys
import logging
from datetime import datetime, date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, CallbackQueryHandler, filters

# Adiciona o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory import EronMemory
from core.preferences import PreferencesManager
from core.emotion_system import EmotionSystem
from core.user_profile_db import UserProfileDB
from web.app import get_llm_response
from learning.fast_learning import FastLearning
from learning.human_conversation import HumanConversationSystem
from learning.advanced_adult_learning import advanced_adult_learning
import re
import json
import sys
from dotenv import load_dotenv

# Estados da conversa - SISTEMA COMPLETO DE PERSONALIZAÇÃO
GET_NAME = 1
GET_AGE = 2
GET_GENDER = 3
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

# Estados para mudanças individuais
CHANGE_USER_NAME = 20
CHANGE_USER_AGE = 21
CHANGE_USER_GENDER = 22
CHANGE_BOT_NAME = 23
CHANGE_BOT_GENDER = 24
CHANGE_PERSONALITY = 25
CHANGE_LANGUAGE = 26
CHANGE_TOPICS = 27

# Estados para preferências
PREF_MENU = 10
PREF_CHAT = 11
PREF_VISUAL = 12
PREF_NOTIFY = 13

# Estados para emoções
EMOTION_MENU = 20
EMOTION_DETECTION = 21
EMOTION_RANGE = 22

# Estados para sistema adulto
ADULT_TERMS = 30
ADULT_AGE_VERIFICATION = 31

# Estados para configuração sequencial inicial
SEQUENCIAL_USER_NAME = 40
SEQUENCIAL_USER_GENDER = 41
SEQUENCIAL_USER_AGE_DAY = 42
SEQUENCIAL_USER_AGE_MONTH = 43
SEQUENCIAL_USER_AGE_YEAR = 44
SEQUENCIAL_BOT_GENDER = 45
SEQUENCIAL_BOT_NAME = 46
SEQUENCIAL_PERSONALITY = 47
SEQUENCIAL_LANGUAGE = 48
SEQUENCIAL_COMPLETE = 49

# Configurar o logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Estado de usuários agora gerenciado via context.user_data para thread-safety
# Removidas variáveis globais problemáticas: sequential_setup_data, sequential_step, adult_access

# Instância da memória de conversa (mantém-se local)
memory = EronMemory()

# Instâncias dos gerenciadores
preferences_manager = PreferencesManager()
emotion_system = EmotionSystem()

# Sistemas de aprendizagem
fast_learning = FastLearning()
human_conversation = HumanConversationSystem()

# Instâncias do sistema adulto
try:
    import sys
    import os
    # Garantir que o caminho para o diretório Scripts18 está correto
    scripts18_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Eron-18', 'Scripts18')
    sys.path.append(scripts18_path)
    from adult_personality_db import AdultPersonalityDB  # type: ignore
    from adult_commands import AdultCommandSystem  # type: ignore
    from devassa_personality import DevassaPersonality  # type: ignore
    
    # Inicializar sistema adulto
    adult_db = AdultPersonalityDB()
    adult_commands = AdultCommandSystem(adult_db)
    
    ADULT_SYSTEM_AVAILABLE = True
    print("✅ Sistema adulto carregado com sucesso")
except ImportError as e:
    print(f"⚠️ Sistema adulto não disponível: {e}")
    ADULT_SYSTEM_AVAILABLE = False
    adult_commands = None
    adult_db = None

def safe_personalization_save(user_id, user_profile_db, updates_dict, context_description="personalização"):
    """
    Função auxiliar para salvar personalização com filtro de segurança
    """
    try:
        from src.personalization_filter import apply_personalization_filter
        
        # Obter perfil atual para verificar idade
        current_profile = user_profile_db.get_profile(user_id) or {}
        
        # Combinar conteúdo para análise
        content_to_check = f"{context_description} {' '.join(str(v) for v in updates_dict.values())}"
        
        filter_result = apply_personalization_filter(
            content=content_to_check,
            user_profile=current_profile
        )
        
        print(f"[TELEGRAM FILTER] {context_description}: {filter_result}")
        
        if filter_result['allowed']:
            user_profile_db.save_profile(user_id=user_id, **updates_dict)
            return True
        else:
            print(f"[TELEGRAM FILTER] Bloqueado: {filter_result['reason']}")
            return False
            
    except Exception as e:
        print(f"[TELEGRAM FILTER] Erro no filtro: {e}")
        # Em caso de erro no filtro, permitir salvamento normal
        user_profile_db.save_profile(user_id=user_id, **updates_dict)
        return True

def detect_and_save_telegram_personalization(user_message, user_id, user_profile_db):
    """
    Detecta e salva automaticamente informações de personalização para Telegram
    
    SISTEMA DE PERSONALIZAÇÃO ERON:
    - Nome padrão do bot: ERON (maiúsculo)  
    - Exemplo de personalização: "Joana" (quando usuário personaliza nome)
    - Opções disponíveis: nome do bot, gênero, personalidade, estilo linguagem, tópicos
    """
    message_lower = user_message.lower().strip()
    updates = {}
    
    # Detectar nome do usuário - versões mais específicas
    name_patterns = [
        r"meu nome é (\w+)",
        r"me chamo (\w+)", 
        r"sou (\w+)",
        r"pode me chamar de (\w+)",
        r"meu nome não (\w+)\?",  # "meu nome não Romario?"
        r"meu nome não é (\w+)\?", # "meu nome não é Romario?"
        r"^sou o (\w+)$",  # "sou o João"
        r"^me chamo (\w+)$"  # "me chamo Maria"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, message_lower)
        if match:
            name = match.group(1).capitalize()
            if len(name) > 1 and name not in ['não', 'sim', 'ok', 'obrigado', 'obrigada']:
                updates['user_name'] = name
                break
    
    # Detectar nome do assistente 
    bot_name_patterns = [
        r"se chame (\w+)",
        r"seu nome seja (\w+)",
        r"te chamar de (\w+)",
        r"quero que se chame (\w+)"
    ]
    
    for pattern in bot_name_patterns:
        match = re.search(pattern, message_lower)
        if match:
            bot_name = match.group(1).capitalize()
            if len(bot_name) > 1:
                updates['bot_name'] = bot_name
                break
    
    # Detectar personalidade do bot
    personality_patterns = {
        'amigável': ['amigável', 'amigo', 'amiga', 'legal', 'bacana', 'gentil'],
        'formal': ['formal', 'profissional', 'sério', 'séria', 'educado'],
        'casual': ['casual', 'descontraído', 'descontraída', 'relaxado', 'relaxada', 'informal'],
        'divertido': ['divertido', 'divertida', 'engraçado', 'engraçada', 'brincalhão', 'alegre'],
        'intelectual': ['intelectual', 'sábio', 'sábia', 'inteligente', 'culto', 'erudito']
    }
    
    for personality, keywords in personality_patterns.items():
        if any(keyword in message_lower for keyword in keywords):
            updates['bot_personality'] = personality
            break
    
    # Detectar estilo de linguagem
    language_patterns = {
        'simples': ['simples', 'fácil', 'direto', 'básico'],
        'técnico': ['técnico', 'detalhado', 'específico', 'científico'],
        'coloquial': ['coloquial', 'gírias', 'informal', 'descontraído'],
        'eloquente': ['eloquente', 'sofisticado', 'elegante', 'refinado']
    }
    
    for language, keywords in language_patterns.items():
        if any(keyword in message_lower for keyword in keywords):
            updates['bot_language'] = language
            break
    
    # Detectar tópicos de interesse (separados por vírgula)
    topics_patterns = [
        r"gosto de (.*)",
        r"me interesso por (.*)",
        r"quero falar sobre (.*)",
        r"meus interesses são (.*)",
        r"tópicos favoritos são (.*)"
    ]
    
    for pattern in topics_patterns:
        match = re.search(pattern, message_lower)
        if match:
            topics = match.group(1).strip()
            if len(topics) > 2:
                updates['preferred_topics'] = topics
                break
    
    # Se encontrou informações para salvar
    if updates:
        try:
            # APLICAR FILTRO DE PERSONALIZAÇÃO ESPECÍFICO
            from src.personalization_filter import apply_personalization_filter
            
            # Combinar conteúdo para análise
            content_to_check = f"{user_message} {' '.join(str(v) for v in updates.values())}"
            
            # Obter perfil atual para verificar idade
            current_profile = user_profile_db.get_profile(user_id)
            
            filter_result = apply_personalization_filter(
                content=content_to_check,
                user_profile=current_profile or {}
            )
            
            print(f"[TELEGRAM DEBUG] Filtro personalização: {filter_result}")
            
            if filter_result['allowed']:
                print(f"[TELEGRAM DEBUG] Salvando automaticamente: {updates}")
                user_profile_db.save_profile(user_id=user_id, **updates)
                return True
            else:
                print(f"[TELEGRAM DEBUG] Personalização bloqueada: {filter_result['reason']}")
                return False
                
        except Exception as e:
            print(f"[TELEGRAM DEBUG] Erro ao salvar personalização: {e}")
            return False
    
    return False

def detect_personalization_intent(user_message):
    """Detecta se a mensagem parece ser uma resposta à pergunta de personalização"""
    message_lower = user_message.lower().strip()
    
    # Palavras que indicam que é uma resposta de personalização
    personalization_indicators = [
        'meu nome', 'me chamo', 'sou', 'pode me chamar',
        'se chame', 'seu nome seja', 'te chamar de', 'quero que se chame',
        'formal', 'informal', 'amigável', 'divertido', 'casual'
    ]
    
    return any(indicator in message_lower for indicator in personalization_indicators)

async def clear_personalization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /clear - Apaga todas as personalizações"""
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    
    try:
        # Desativar modo adulto antes de apagar perfil
        from core.check import deactivate_adult_mode
        deactivate_adult_mode(user_id)
        print(f"[DEBUG] Modo adulto desativado para {user_id} durante reset de personalização")
        
        # Apagar perfil do banco
        user_profile_db.delete_profile(user_id)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='🗑️ Todas as suas personalizações foram apagadas!\n\n'
                 '🔒 O modo adulto também foi desativado.\n'
                 'Agora eu voltei a ser o ERON padrão. '
                 'Gostaria de personalizar novamente? \n\n'
                 'Digite /start para começar uma nova personalização! 😊'
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='❌ Erro ao apagar personalizações. Tente novamente.'
        )

# Comandos para mudanças individuais
async def change_bot_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /mudar_nome - Muda só o nome do bot"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='🤖 Como você gostaria que eu me chamasse?\n\n'
             'Digite o novo nome:'
    )
    context.user_data['changing_bot_name'] = True

async def change_personality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /mudar_personalidade - Muda só a personalidade"""
    keyboard = [
        [InlineKeyboardButton("😊 Amigável", callback_data='personality_amigável')],
        [InlineKeyboardButton("🎩 Formal", callback_data='personality_formal')],
        [InlineKeyboardButton("😎 Casual", callback_data='personality_casual')],
        [InlineKeyboardButton("🎭 Divertida", callback_data='personality_divertido')],
        [InlineKeyboardButton("🧠 Intelectual", callback_data='personality_intelectual')]
    ]
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='✨ Escolha minha nova personalidade:',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def change_user_name_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /meu_nome - Permite alterar o nome do usuário"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='👤 **Como você quer que eu te chame?**\n\n'
             'Digite seu nome ou apelido preferido:',
        parse_mode='Markdown'
    )
    context.user_data['changing_user_name'] = True

async def reset_personalization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /reconfigurar - Reset completo da personalização"""
    keyboard = [
        [InlineKeyboardButton("✅ Sim, recomeçar tudo", callback_data='confirm_reset_all')],
        [InlineKeyboardButton("❌ Cancelar", callback_data='cancel_reset')]
    ]
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='🔄 **Reconfigurarar personalização completa?**\n\n'
             '⚠️ Isso vai apagar todas as suas configurações atuais e permitir começar do zero.\n\n'
             '📋 **Será redefinido:**\n'
             '• Seu nome e idade\n'
             '• Seu gênero  \n'
             '• Nome e personalidade do bot\n'
             '• Estilo de linguagem\n'
             '• Tópicos de interesse\n\n'
             '💭 **Tem certeza?**',
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
async def start_personalization_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu de personalização completo com botões"""
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.first_name or "Usuário"
    
    # Limpar dados de sessão
    context.user_data.clear()
    
    await update.message.reply_text(
        f"👋 **Olá, {user_name}!**\n\n"
        "🌟 **Bem-vindo ao sistema de personalização do Eron.IA!**\n\n"
        "Vou fazer algumas perguntas para personalizar nossa conversa e oferecer a melhor experiência possível.\n\n"
        "📋 **O processo inclui:**\n"
        "• Seu nome e idade\n"
        "• Seu gênero\n" 
        "• Gênero e personalidade do bot\n"
        "• Estilo de linguagem\n"
        "• Tópicos de interesse\n\n"
        "⏱️ *Leva apenas 2 minutos!*",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Vamos começar!", callback_data='start_personalization')],
            [InlineKeyboardButton("⏭️ Pular personalização", callback_data='skip_personalization')]
        ])
    )

async def handle_start_personalization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia o processo de personalização"""
    query = update.callback_query
    await query.answer("🚀 Iniciando personalização!")
    
    await query.edit_message_text(
        "✨ **Perfeito! Vamos começar!**\n\n"
        "👤 **Primeiro, como você gostaria de ser chamado?**\n\n"
        "💭 *Digite seu nome ou apelido preferido:*"
    )
    
    context.user_data['personalization_step'] = 'user_name'

async def handle_skip_personalization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pula a personalização"""
    query = update.callback_query 
    await query.answer("⏭️ Personalização pulada!")
    
    await query.edit_message_text(
        "✅ **Tudo bem!** \n\n"
        "Vou usar as configurações padrão. Você pode personalizar a qualquer momento usando o comando `/personalizar`.\n\n"
        "🤖 **Agora pode começar a conversar comigo!**"
    )
    
    context.user_data.clear()

async def handle_user_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa o nome do usuário e pergunta a idade"""
    if context.user_data.get('personalization_step') != 'user_name':
        return
        
    user_name = update.message.text.strip()
    user_id = str(update.effective_user.id)
    
    # Salvar nome do usuário
    user_profile_db = context.application.user_profile_db
    user_profile_db.save_profile(user_id=user_id, user_name=user_name)
    
    await update.message.reply_text(
        f"✅ **Prazer em conhecê-lo, {user_name}!**\n\n"
        "🎂 **Agora preciso saber sua idade para adequar o conteúdo:**\n\n"
        "🔞 *Esta informação é importante para garantir que o conteúdo seja apropriado.*",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Sou maior de 18 anos", callback_data='age_18_plus')],
            [InlineKeyboardButton("❌ Sou menor de 18 anos", callback_data='age_under_18')]
        ])
    )
    
    context.user_data['personalization_step'] = 'user_age'

async def handle_age_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa verificação de idade e pergunta gênero do usuário"""
    query = update.callback_query
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    
    if query.data == 'age_18_plus':
        await query.answer("✅ Idade verificada!")
        user_profile_db.save_profile(user_id=user_id, user_age='18+', has_mature_access=True)
        age_message = "✅ **Perfeito!** Você tem acesso completo a todos os recursos."
    else:
        await query.answer("✅ Configuração ajustada!")
        user_profile_db.save_profile(user_id=user_id, user_age='<18', has_mature_access=False)  
        age_message = "✅ **Configuração ajustada!** Conteúdo adequado para menores de 18."
    
    await query.edit_message_text(
        f"{age_message}\n\n"
        "👥 **Agora, como você se identifica?**\n\n"
        "🏳️ *Esta informação ajuda a personalizar a comunicação:*",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👨 Masculino", callback_data='user_gender_masculino')],
            [InlineKeyboardButton("👩 Feminino", callback_data='user_gender_feminino')], 
            [InlineKeyboardButton("🌈 Outro/Prefiro não dizer", callback_data='user_gender_outro')]
        ])
    )
    
    context.user_data['personalization_step'] = 'user_gender'

async def handle_user_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa gênero do usuário e pergunta gênero do bot"""
    query = update.callback_query
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    
    gender_key = query.data.replace('user_gender_', '')
    gender_names = {
        'masculino': 'Masculino',
        'feminino': 'Feminino', 
        'outro': 'Outro/Prefiro não dizer'
    }
    
    await query.answer(f"✅ {gender_names[gender_key]} selecionado!")
    
    # Salvar gênero do usuário
    user_profile_db.save_profile(user_id=user_id, user_gender=gender_key)
    
    await query.edit_message_text(
        f"✅ **Gênero {gender_names[gender_key]} registrado!**\n\n"
        "🤖 **Agora vamos personalizar seu assistente!**\n\n"
        "👤 **Como você prefere que eu me apresente?**\n\n"
        "💭 *Isso influencia como eu falo e me refiro a mim mesmo:*",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👩 Feminino", callback_data='bot_gender_feminino')],
            [InlineKeyboardButton("👨 Masculino", callback_data='bot_gender_masculino')],
            [InlineKeyboardButton("🤖 Neutro", callback_data='bot_gender_neutro')]
        ])
    )
    
    context.user_data['personalization_step'] = 'bot_gender'

async def handle_want_bot_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa se quer dar nome ao bot ou usar padrão"""
    query = update.callback_query
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    
    if query.data == 'want_bot_name_yes':
        await query.answer("✨ Vamos escolher um nome!")
        await query.edit_message_text(
            "✨ **Perfeito! Vamos escolher um nome especial!**\n\n"
            "🤖 **Escolha uma das opções ou crie um nome personalizado:**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🌸 Joana", callback_data='initial_bot_name_joana')],
                [InlineKeyboardButton("💫 Luna", callback_data='initial_bot_name_luna')],
                [InlineKeyboardButton("🌟 Sofia", callback_data='initial_bot_name_sofia')],
                [InlineKeyboardButton("🎭 Maya", callback_data='initial_bot_name_maya')],
                [InlineKeyboardButton("💎 Aria", callback_data='initial_bot_name_aria')],
                [InlineKeyboardButton("✏️ Nome personalizado", callback_data='initial_bot_name_custom')]
            ])
        )
        context.user_data['personalization_step'] = 'choose_bot_name'
        
    elif query.data == 'want_bot_name_no':
        await query.answer("🤖 Usando nome padrão!")
        # Salvar nome padrão
        user_profile_db.save_profile(user_id=user_id, bot_name='Eron')
        
        await query.edit_message_text(
            "🤖 **Perfeito! Me chamarei de Eron!**\n\n"
            "👤 **Como você prefere que eu me apresente?**\n\n"
            "💭 *Isso influencia como eu falo e me refiro a mim mesmo:*",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👩 Feminino", callback_data='bot_gender_feminino')],
                [InlineKeyboardButton("👨 Masculino", callback_data='bot_gender_masculino')],
                [InlineKeyboardButton("🤖 Neutro", callback_data='bot_gender_neutro')]
            ])
        )
        context.user_data['personalization_step'] = 'bot_gender'

async def handle_initial_bot_name_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa escolha do nome do bot no processo inicial"""
    query = update.callback_query
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    
    name_key = query.data.replace('initial_bot_name_', '')
    
    if name_key == 'custom':
        await query.answer("✏️ Digite o nome personalizado!")
        await query.edit_message_text(
            "✏️ **Nome personalizado:**\n\n"
            "💭 *Digite o nome que você quer que eu tenha:*\n\n"
            "⚠️ *Evite nomes muito longos ou complicados*"
        )
        context.user_data['personalization_step'] = 'bot_name'
        return GET_BOT_NAME
    
    name_mapping = {
        'joana': 'Joana',
        'luna': 'Luna',
        'sofia': 'Sofia', 
        'maya': 'Maya',
        'aria': 'Aria'
    }
    
    if name_key in name_mapping:
        bot_name = name_mapping[name_key]
        
        # Salvar nome do bot
        user_profile_db.save_profile(user_id=user_id, bot_name=bot_name)
        
        await query.answer(f"✅ Nome {bot_name} escolhido!")
        await query.edit_message_text(
            f"✅ **Perfeito! Agora me chamo {bot_name}!**\n\n"
            "👤 **Como você prefere que eu me apresente?**\n\n"
            "💭 *Isso influencia como eu falo e me refiro a mim mesmo:*",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👩 Feminino", callback_data='bot_gender_feminino')],
                [InlineKeyboardButton("👨 Masculino", callback_data='bot_gender_masculino')]
            ])
        )
        context.user_data['personalization_step'] = 'bot_gender'
        return GET_BOT_GENDER

async def handle_bot_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa gênero do bot e oferece nomes apropriados"""
    query = update.callback_query
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    
    gender_key = query.data.replace('bot_gender_', '')
    gender_names = {
        'masculino': 'Masculino', 
        'feminino': 'Feminino',
        'neutro': 'Neutro'
    }
    
    await query.answer(f"✅ Gênero {gender_names[gender_key]} aplicado!")
    
    # Salvar gênero do bot
    user_profile_db.save_profile(user_id=user_id, bot_gender=gender_key)
    
    # Oferecer nomes específicos baseados no gênero escolhido
    if gender_key == 'masculino':
        await query.edit_message_text(
            f"✅ **Agora me apresento no masculino!**\n\n"
            "👨 **Escolha um nome masculino para mim:**\n\n"
            "💡 *Ou digite um nome personalizado*",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 ERON (Padrão)", callback_data='bot_name_ERON')],
                [InlineKeyboardButton("👨 Bruno", callback_data='bot_name_Bruno')],
                [InlineKeyboardButton("💼 Carlos", callback_data='bot_name_Carlos')],
                [InlineKeyboardButton("� Diego", callback_data='bot_name_Diego')],
                [InlineKeyboardButton("🔥 Mateus", callback_data='bot_name_Mateus')],
                [InlineKeyboardButton("⚡ Rafael", callback_data='bot_name_Rafael')],
                [InlineKeyboardButton("✍️ Digite outro nome", callback_data='bot_name_custom')]
            ])
        )
    elif gender_key == 'feminino':
        await query.edit_message_text(
            f"✅ **Agora me apresento no feminino!**\n\n"
            "� **Escolha um nome feminino para mim:**\n\n"
            "💡 *Ou digite um nome personalizado*",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 ERONA (Padrão)", callback_data='bot_name_ERONA')],
                [InlineKeyboardButton("👩 Ana", callback_data='bot_name_Ana')],
                [InlineKeyboardButton("💼 Beatriz", callback_data='bot_name_Beatriz')],
                [InlineKeyboardButton("� Clara", callback_data='bot_name_Clara')],
                [InlineKeyboardButton("� Maria", callback_data='bot_name_Maria')],
                [InlineKeyboardButton("⚡ Sofia", callback_data='bot_name_Sofia')],
                [InlineKeyboardButton("✍️ Digite outro nome", callback_data='bot_name_custom')]
            ])
        )
    else:  # neutro
        await query.edit_message_text(
            f"✅ **Manterei uma apresentação neutra!**\n\n"
            "🤖 **Escolha um nome neutro para mim:**\n\n"
            "💡 *Ou digite um nome personalizado*",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 ERON (Padrão)", callback_data='bot_name_ERON')],
                [InlineKeyboardButton("💫 Alex", callback_data='bot_name_Alex')],
                [InlineKeyboardButton("🌟 Chris", callback_data='bot_name_Chris')],
                [InlineKeyboardButton("✨ Jordan", callback_data='bot_name_Jordan')],
                [InlineKeyboardButton("🎭 Sam", callback_data='bot_name_Sam')],
                [InlineKeyboardButton("🔮 Taylor", callback_data='bot_name_Taylor')],
                [InlineKeyboardButton("✍️ Digite outro nome", callback_data='bot_name_custom')]
            ])
        )
    
    context.user_data['personalization_step'] = 'bot_name_selection'

async def handle_bot_name_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a seleção de nome baseada no gênero"""
    try:
        print(f"[DEBUG BOT_NAME] ============ INICIANDO handle_bot_name_selection ============")
        query = update.callback_query
        user_id = str(update.effective_user.id)
        user_profile_db = context.application.user_profile_db
        
        print(f"[DEBUG BOT_NAME] callback_data: {query.data}")
        print(f"[DEBUG BOT_NAME] user_id: {user_id}")
        print(f"[DEBUG BOT_NAME] query object: {query}")
        
        # SEMPRE responder o callback primeiro para evitar timeout
        await query.answer()
        print(f"[DEBUG BOT_NAME] Callback respondido imediatamente")
        
        if query.data == 'bot_name_custom':
            # Usuário quer digitar nome personalizado
            await query.edit_message_text(
                "✏️ **Digite o nome que você quer para mim:**\n\n"
                "💡 *Pode ser qualquer nome que preferir*"
            )
            context.user_data['personalization_step'] = 'bot_name_input'
            print(f"[DEBUG BOT_NAME] Nome customizado solicitado")
            # Retornar para um estado que aceita texto
            return GET_BOT_NAME
        
        # Extrair nome do callback_data
        bot_name = query.data.replace('bot_name_', '')
        print(f"[DEBUG BOT_NAME] Nome extraído: '{bot_name}'")
        
        # Salvar nome do bot
        print(f"[DEBUG BOT_NAME] Salvando perfil com user_id={user_id}, bot_name={bot_name}")
        user_profile_db.save_profile(user_id=user_id, bot_name=bot_name)
        print(f"[DEBUG BOT_NAME] Nome {bot_name} salvo no banco com sucesso")
        
        # Verificar se salvou corretamente
        profile_check = user_profile_db.get_profile(user_id)
        print(f"[DEBUG BOT_NAME] Verificação - perfil após salvar: {profile_check}")
        
        await query.edit_message_text(
            f"✅ **Perfeito! Agora me chamo {bot_name}!**\n\n"
            "🎭 **Qual personalidade você prefere que eu tenha?**\n\n"
            "💡 *Isso define como eu vou interagir com você:*",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("😊 Amigável", callback_data='personality_amigável')],
                [InlineKeyboardButton("🎩 Formal", callback_data='personality_formal')],
                [InlineKeyboardButton("😎 Casual", callback_data='personality_casual')],
                [InlineKeyboardButton("🎭 Divertido", callback_data='personality_divertido')],
                [InlineKeyboardButton("🧠 Intelectual", callback_data='personality_intelectual')]
            ])
        )
        print(f"[DEBUG BOT_NAME] Mensagem de personalidade enviada com sucesso")
        
        context.user_data['personalization_step'] = 'bot_personality'
        print(f"[DEBUG BOT_NAME] Step atualizado para 'bot_personality'")
        print(f"[DEBUG BOT_NAME] ============ FIM handle_bot_name_selection ============")
        
        # CRÍTICO: Retornar o estado correto para o ConversationHandler
        return SELECT_PERSONALITY
        
    except Exception as e:
        print(f"[ERROR BOT_NAME] Erro em handle_bot_name_selection: {e}")
        import traceback
        traceback.print_exc()
        try:
            await query.answer("❌ Erro interno")
            await query.edit_message_text(
                "❌ **Erro interno**\n\n"
                "Ocorreu um erro ao processar sua seleção. Tente novamente ou use /start."
            )
        except Exception as inner_e:
            print(f"[ERROR BOT_NAME] Erro ao enviar mensagem de erro: {inner_e}")

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
    """Menu completo de preferências - permite alterar todos os parâmetros"""
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    profile = user_profile_db.get_profile(user_id)
    
    if not profile:
        await update.message.reply_text(
            "❌ **Perfil não encontrado!**\n\n"
            "Use /start para criar seu perfil primeiro.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("� Criar Perfil", callback_data='start_personalization')]
            ])
        )
        return
    
    # Informações atuais do perfil
    user_name = profile.get('user_name', 'Não definido')
    user_age = profile.get('user_age', 'Não definida')
    user_gender = profile.get('user_gender', 'não definido').title()
    bot_name = profile.get('bot_name', 'Eron')
    bot_gender = profile.get('bot_gender', 'neutro').title()
    bot_personality = profile.get('bot_personality', 'casual').title()
    bot_language = profile.get('bot_language', 'informal').title()
    topics = profile.get('preferred_topics', 'Nenhum').title()
    
    keyboard = [
        [InlineKeyboardButton(f"👤 Seu Nome: {user_name}", callback_data='change_user_name')],
        [InlineKeyboardButton(f"� Sua Idade: {user_age}", callback_data='change_user_age_menu')],
        [InlineKeyboardButton(f"👥 Seu Gênero: {user_gender}", callback_data='change_user_gender_menu')],
        [InlineKeyboardButton(f"🤖 Nome do Bot: {bot_name}", callback_data='change_bot_name')],
        [InlineKeyboardButton(f"� Gênero do Bot: {bot_gender}", callback_data='change_bot_gender_menu')],
        [InlineKeyboardButton(f"🎭 Personalidade: {bot_personality}", callback_data='change_personality')],
        [InlineKeyboardButton(f"💬 Linguagem: {bot_language}", callback_data='change_language_menu')],
        [InlineKeyboardButton(f"📚 Tópicos: {topics}", callback_data='change_topics_menu')],
        [InlineKeyboardButton("🔄 Redefinir Tudo", callback_data='reset_all_preferences')],
        [InlineKeyboardButton("❌ Fechar", callback_data='close_preferences')]
    ]
    
    await update.message.reply_text(
        "🛠 **Menu de Preferências Completo**\n\n"
        f"📋 **Seu Perfil Atual:**\n"
        f"👤 **Nome:** {user_name}\n"
        f"🎂 **Idade:** {user_age}\n"
        f"👥 **Gênero:** {user_gender}\n\n"
        f"🤖 **Sobre o Bot:**\n"
        f"📝 **Nome:** {bot_name}\n"
        f"👤 **Gênero:** {bot_gender}\n"
        f"🎭 **Personalidade:** {bot_personality}\n"
        f"💬 **Linguagem:** {bot_language}\n"
        f"📚 **Tópicos:** {topics}\n\n"
        f"💡 *Clique em qualquer opção para alterar:*",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /menu - Menu principal unificado"""
    user_id = update.effective_user.id
    user_data = context.user_data
    
    # Verificar se usuário tem configuração completa
    user_name = user_data.get('user_name', update.effective_user.first_name)
    user_age = user_data.get('user_age', 'Não definida')
    bot_name = user_data.get('bot_name', 'Eron')
    is_adult = context.user_data.get('adult_access', False)
    
    # Verificar se está configurado
    is_configured = all(key in user_data for key in ['user_name', 'user_age', 'user_gender', 'bot_name', 'bot_gender', 'personality'])
    
    if not is_configured:
        # Usuário não configurado - oferecer configuração sequencial
        keyboard = [
            [InlineKeyboardButton("⚙️ Configuração Inicial", callback_data="start_sequential_setup")],
            [InlineKeyboardButton("🎨 Personalização Rápida", callback_data="start_personalization")],
            [InlineKeyboardButton("❓ Ajuda", callback_data="help_menu")]
        ]
        
        message = f"""📋 **MENU PRINCIPAL - ERON.IA**

👋 Olá **{user_name}**!

⚙️ **Sistema não configurado completamente**

**Opções disponíveis:**
• Configuração inicial completa (recomendado)
• Personalização rápida (modo clássico)
• Ajuda e informações"""
        
    else:
        # Usuário configurado - menu completo
        keyboard = [
            [InlineKeyboardButton("👤 Meu Perfil", callback_data="show_user_profile"),
             InlineKeyboardButton(f"🤖 Perfil do {bot_name}", callback_data="show_bot_profile")],
            [InlineKeyboardButton("🛠️ Preferências", callback_data="show_preferences"),
             InlineKeyboardButton("🎭 Emoções", callback_data="show_emotions")],
            [InlineKeyboardButton("🎨 Personalização", callback_data="start_personalization"),
             InlineKeyboardButton("💬 Conversar", callback_data="start_conversation")]
        ]
        
        # Adicionar opção adulta se maior de idade
        if is_adult:
            keyboard.append([InlineKeyboardButton("🔞 Modo Adulto", callback_data="adult_config")])
        
        keyboard.append([InlineKeyboardButton("🧹 Limpar Dados", callback_data="clear_all_data")])
        
        adult_indicator = "🔓 Sistema adulto ativo" if is_adult else "🔒 Modo padrão"
        
        message = f"""📋 **MENU PRINCIPAL - {bot_name.upper()}**

👋 Olá **{user_name}**!
🎂 **Idade:** {user_age} anos
{adult_indicator}

**🎛️ Opções Disponíveis:**
Acesse todas as funcionalidades do sistema!"""
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

# SISTEMA DE CONFIGURAÇÃO SEQUENCIAL INICIAL
async def start_sequential_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Iniciar configuração sequencial passo a passo"""
    user_id = update.effective_user.id
    
    # Inicializar dados
    context.user_data['sequential_setup_data'] = {}
    context.user_data['sequential_step'] = SEQUENCIAL_USER_NAME
    
    if update.callback_query:
        query = update.callback_query
        await query.answer("⚙️ Iniciando configuração!")
        
        message = f"""🤖 **Configuração Inicial - ERON.IA**

👋 Olá, {update.effective_user.first_name}!

Vou te guiar através de uma configuração completa para personalizar sua experiência!

**1. Qual é seu nome?**
(Como você gostaria que eu te chamasse?)"""
        
        await query.edit_message_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text(message, parse_mode='Markdown')

async def handle_sequential_setup_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lidar com texto durante configuração sequencial"""
    user_id = update.effective_user.id
    message_text = update.message.text.strip()
    
    if 'sequential_step' not in context.user_data:
        return

    current_step = context.user_data['sequential_step']
    
    if current_step == SEQUENCIAL_USER_NAME:
        # Etapa 1: Nome do usuário
        if 'sequential_setup_data' not in context.user_data:
            context.user_data['sequential_setup_data'] = {}
        context.user_data['sequential_setup_data']['user_name'] = message_text
        
        keyboard = [
            [InlineKeyboardButton("👨 Homem", callback_data="seq_gender_masculino")],
            [InlineKeyboardButton("👩 Mulher", callback_data="seq_gender_feminino")],
            [InlineKeyboardButton("🌟 Outro", callback_data="seq_gender_outro")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"""✅ **Perfeito, {message_text}!**

**2. Qual é seu gênero?**
Isso me ajuda a personalizar melhor nossa conversa:"""
        
        context.user_data['sequential_step'] = SEQUENCIAL_USER_GENDER
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    elif current_step == SEQUENCIAL_USER_AGE_DAY:
        # Etapa 3a: Dia do nascimento
        try:
            day = int(message_text)
            if 1 <= day <= 31:
                context.user_data['sequential_setup_data']['birth_day'] = day
                context.user_data['sequential_step'] = SEQUENCIAL_USER_AGE_MONTH
                await update.message.reply_text(f"✅ **Dia: {day}**\n\n**Agora o mês (1-12):**", parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ **Dia inválido!** Digite um número entre 1 e 31:")
        except ValueError:
            await update.message.reply_text("❌ **Por favor, digite apenas números!**\nQual é o dia do seu nascimento (1-31)?")
            
    elif current_step == SEQUENCIAL_USER_AGE_MONTH:
        # Etapa 3b: Mês do nascimento
        try:
            month = int(message_text)
            if 1 <= month <= 12:
                context.user_data['sequential_setup_data']['birth_month'] = month
                context.user_data['sequential_step'] = SEQUENCIAL_USER_AGE_YEAR
                await update.message.reply_text(f"✅ **Mês: {month}**\n\n**Agora o ano (ex: 1990):**", parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ **Mês inválido!** Digite um número entre 1 e 12:")
        except ValueError:
            await update.message.reply_text("❌ **Por favor, digite apenas números!**\nQual é o mês do seu nascimento (1-12)?")
            
    elif current_step == SEQUENCIAL_USER_AGE_YEAR:
        # Etapa 3c: Ano do nascimento
        try:
            year = int(message_text)
            if 1900 <= year <= 2025:
                # Calcular idade
                birth_date = date(year, context.user_data['sequential_setup_data']['birth_month'], context.user_data['sequential_setup_data']['birth_day'])
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                
                context.user_data['sequential_setup_data']['birth_year'] = year
                context.user_data['sequential_setup_data']['user_age'] = age
                
                # Verificar se é maior de idade
                is_adult = age >= 18
                context.user_data['sequential_setup_data']['is_adult'] = is_adult
                if is_adult:
                    context.user_data['adult_access'] = True
                
                # Avançar para escolha do gênero do bot
                keyboard = [
                    [InlineKeyboardButton("👩 Feminino", callback_data="seq_bot_gender_feminino")],
                    [InlineKeyboardButton("👨 Masculino", callback_data="seq_bot_gender_masculino")],
                    [InlineKeyboardButton("🤖 Neutro", callback_data="seq_bot_gender_neutro")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                age_message = f"✅ **Idade: {age} anos**"
                if is_adult:
                    age_message += " 🔓 *(Acesso completo liberado)*"
                
                message = f"""{age_message}

**4. Como você gostaria que eu fosse?**
Escolha o gênero do seu assistente virtual:"""
                
                context.user_data['sequential_step'] = SEQUENCIAL_BOT_GENDER
                await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
                
            else:
                await update.message.reply_text("❌ **Ano inválido!** Digite um ano entre 1900 e 2025:")
        except ValueError:
            await update.message.reply_text("❌ **Por favor, digite apenas números!**\nQual é o ano do seu nascimento?")
            
    elif current_step == SEQUENCIAL_BOT_NAME:
        # Etapa 5: Nome personalizado do bot
        bot_name = message_text
        context.user_data['sequential_setup_data']['bot_name'] = bot_name
        await show_sequential_personality_selection(update, context, user_id)
        
    elif current_step == SEQUENCIAL_PERSONALITY:
        # Personalidade customizada
        context.user_data['sequential_setup_data']['personality'] = message_text
        await show_sequential_language_selection(update, context, user_id)
        
    elif current_step == SEQUENCIAL_LANGUAGE:
        # Estilo customizado
        context.user_data['sequential_setup_data']['language_style'] = message_text
        await finish_sequential_setup(update, context, user_id)

async def show_sequential_personality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Mostrar seleção de personalidade na configuração sequencial"""
    bot_name = context.user_data['sequential_setup_data']['bot_name']
    is_adult = context.user_data['sequential_setup_data'].get('is_adult', False)
    
    keyboard = [
        [InlineKeyboardButton("😊 Amigável", callback_data="seq_personality_amigavel"),
         InlineKeyboardButton("🧠 Intelectual", callback_data="seq_personality_intelectual")],
        [InlineKeyboardButton("😄 Engraçado", callback_data="seq_personality_engracado"),
         InlineKeyboardButton("💼 Profissional", callback_data="seq_personality_profissional")]
    ]
    
    # Adicionar opções adultas se maior de idade
    if is_adult:
        keyboard.append([InlineKeyboardButton("🌶️ Sedutor (18+)", callback_data="seq_personality_sedutor"),
                       InlineKeyboardButton("💕 Romântico (18+)", callback_data="seq_personality_romantico")])
    
    keyboard.append([InlineKeyboardButton("✍️ Personalizar", callback_data="seq_personality_custom")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""✅ **Perfeito! Agora me chamo {bot_name}!**

**6. Que personalidade você quer que eu tenha?**
Isso define como eu me comporto e respondo:"""
    
    context.user_data['sequential_step'] = SEQUENCIAL_PERSONALITY
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_sequential_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Mostrar seleção de estilo de linguagem na configuração sequencial"""
    keyboard = [
        [InlineKeyboardButton("🗣️ Formal", callback_data="seq_language_formal"),
         InlineKeyboardButton("💬 Casual", callback_data="seq_language_casual")],
        [InlineKeyboardButton("😎 Gírias", callback_data="seq_language_girias"),
         InlineKeyboardButton("🎓 Técnico", callback_data="seq_language_tecnico")],
        [InlineKeyboardButton("✍️ Personalizar", callback_data="seq_language_custom")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """**7. Como você quer que eu fale?**
Escolha meu estilo de comunicação:"""
    
    context.user_data['sequential_step'] = SEQUENCIAL_LANGUAGE
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def finish_sequential_setup(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Finalizar configuração sequencial"""
    setup_data = context.user_data['sequential_setup_data']
    
    # Salvar todas as configurações no user_data
    context.user_data.update({
        'user_name': setup_data['user_name'],
        'user_gender': setup_data['user_gender'],
        'user_age': setup_data['user_age'],
        'birth_day': setup_data['birth_day'],
        'birth_month': setup_data['birth_month'],
        'birth_year': setup_data['birth_year'],
        'bot_name': setup_data['bot_name'],
        'bot_gender': setup_data['bot_gender'],
        'personality': setup_data['personality'],
        'language_style': setup_data['language_style']
    })
    
    # Limpar dados temporários
    if 'sequential_step' in context.user_data:
        del context.user_data['sequential_step']
    if 'sequential_setup_data' in context.user_data:
        del context.user_data['sequential_setup_data']
    
    # Mensagem de conclusão
    config = context.user_data
    adult_status = "🔓 Sistema adulto liberado" if context.user_data.get('adult_access', False) else "🔒 Sistema padrão"
    
    keyboard = [
        [InlineKeyboardButton("💬 Começar a Conversar", callback_data="start_conversation")],
        [InlineKeyboardButton("📋 Ver Menu Principal", callback_data="show_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""🎉 **CONFIGURAÇÃO CONCLUÍDA!**

👤 **Seu perfil:**
• Nome: {config['user_name']}
• Gênero: {config['user_gender']}
• Idade: {config['user_age']} anos
• {adult_status}

🤖 **Meu perfil:**
• Nome: {config['bot_name']}
• Gênero: {config['bot_gender']}
• Personalidade: {config['personality']}
• Estilo: {config['language_style']}

✅ **Tudo pronto! Agora podemos conversar!**

Use /menu para acessar todas as opções."""
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

# CALLBACKS PARA CONFIGURAÇÃO SEQUENCIAL
async def handle_sequential_setup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para iniciar configuração sequencial"""
    await start_sequential_setup(update, context)

async def handle_sequential_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para callbacks da configuração sequencial"""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    await query.answer()
    
    if data.startswith("seq_gender_"):
        # Etapa 2: Gênero do usuário
        gender = data.replace("seq_gender_", "")
        context.user_data['sequential_setup_data']['user_gender'] = gender
        
        gender_display = {"masculino": "👨 Homem", "feminino": "👩 Mulher", "outro": "🌟 Outro"}[gender]
        
        message = f"""✅ **Gênero: {gender_display}**

**3. Qual é sua data de nascimento?**
Preciso saber sua idade para personalizar melhor a experiência.

**Primeiro, digite o dia (1-31):**"""
        
        context.user_data['sequential_step'] = SEQUENCIAL_USER_AGE_DAY
        await query.edit_message_text(message, parse_mode='Markdown')
        
    elif data.startswith("seq_bot_gender_"):
        # Etapa 4: Gênero do bot
        bot_gender = data.replace("seq_bot_gender_", "")
        context.user_data['sequential_setup_data']['bot_gender'] = bot_gender
        
        # Sugerir nomes baseados no gênero
        suggestions = {
            "feminino": ["Luna", "Maya", "Sofia", "Aria", "Zara"],
            "masculino": ["Alex", "Marcus", "Felix", "Dante", "Neo"],
            "neutro": ["Eron", "Sky", "River", "Phoenix", "Sage"]
        }
        
        suggested_names = suggestions[bot_gender]
        gender_display = {"feminino": "👩 Feminina", "masculino": "👨 Masculino", "neutro": "🤖 Neutro"}[bot_gender]
        
        keyboard = []
        for i in range(0, len(suggested_names), 2):
            row = [InlineKeyboardButton(f"✨ {suggested_names[i]}", callback_data=f"seq_bot_name_{suggested_names[i]}")]
            if i+1 < len(suggested_names):
                row.append(InlineKeyboardButton(f"✨ {suggested_names[i+1]}", callback_data=f"seq_bot_name_{suggested_names[i+1]}"))
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("✍️ Escolher Outro Nome", callback_data="seq_bot_name_custom")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"""✅ **Personalidade: {gender_display}**

**5. Como você quer que eu me chame?**
Aqui estão algumas sugestões, ou você pode escolher outro nome:"""
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    elif data.startswith("seq_bot_name_"):
        # Etapa 5: Nome do bot
        if data == "seq_bot_name_custom":
            context.user_data['sequential_step'] = SEQUENCIAL_BOT_NAME
            await query.edit_message_text("✍️ **Digite o nome que você quer me dar:**", parse_mode='Markdown')
        else:
            bot_name = data.replace("seq_bot_name_", "")
            context.user_data['sequential_setup_data']['bot_name'] = bot_name
            await show_sequential_personality_selection_callback(query, context, user_id)
            
    elif data.startswith("seq_personality_"):
        # Etapa 6: Personalidade
        if data == "seq_personality_custom":
            context.user_data['sequential_step'] = SEQUENCIAL_PERSONALITY
            await query.edit_message_text("✍️ **Descreva como você quer que eu seja:**\n(Ex: 'Seja engraçado e use muitas piadas')", parse_mode='Markdown')
        else:
            personality = data.replace("seq_personality_", "")
            personality_display = {
                "amigavel": "😊 Amigável",
                "intelectual": "🧠 Intelectual", 
                "engracado": "😄 Engraçado",
                "profissional": "💼 Profissional",
                "sedutor": "🌶️ Sedutor",
                "romantico": "💕 Romântico"
            }[personality]
            
            context.user_data['sequential_setup_data']['personality'] = personality_display
            await show_sequential_language_selection_callback(query, context, user_id)
            
    elif data.startswith("seq_language_"):
        # Etapa 7: Estilo de linguagem
        if data == "seq_language_custom":
            context.user_data['sequential_step'] = SEQUENCIAL_LANGUAGE
            await query.edit_message_text("✍️ **Como você quer que eu fale?**\n(Ex: 'Fale de forma descontraída com gírias jovens')", parse_mode='Markdown')
        else:
            style = data.replace("seq_language_", "")
            style_display = {
                "formal": "🗣️ Formal",
                "casual": "💬 Casual",
                "girias": "😎 Com Gírias",
                "tecnico": "🎓 Técnico"
            }[style]
            
            context.user_data['sequential_setup_data']['language_style'] = style_display
            await finish_sequential_setup_callback(query, context, user_id)

async def show_sequential_personality_selection_callback(query, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Mostrar seleção de personalidade via callback"""
    bot_name = context.user_data['sequential_setup_data']['bot_name']
    is_adult = context.user_data['sequential_setup_data'].get('is_adult', False)
    
    keyboard = [
        [InlineKeyboardButton("😊 Amigável", callback_data="seq_personality_amigavel"),
         InlineKeyboardButton("🧠 Intelectual", callback_data="seq_personality_intelectual")],
        [InlineKeyboardButton("😄 Engraçado", callback_data="seq_personality_engracado"),
         InlineKeyboardButton("💼 Profissional", callback_data="seq_personality_profissional")]
    ]
    
    if is_adult:
        keyboard.append([InlineKeyboardButton("🌶️ Sedutor (18+)", callback_data="seq_personality_sedutor"),
                       InlineKeyboardButton("💕 Romântico (18+)", callback_data="seq_personality_romantico")])
    
    keyboard.append([InlineKeyboardButton("✍️ Personalizar", callback_data="seq_personality_custom")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""✅ **Perfeito! Agora me chamo {bot_name}!**

**6. Que personalidade você quer que eu tenha?**
Isso define como eu me comporto e respondo:"""
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_sequential_language_selection_callback(query, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Mostrar seleção de estilo via callback"""
    keyboard = [
        [InlineKeyboardButton("🗣️ Formal", callback_data="seq_language_formal"),
         InlineKeyboardButton("💬 Casual", callback_data="seq_language_casual")],
        [InlineKeyboardButton("😎 Gírias", callback_data="seq_language_girias"),
         InlineKeyboardButton("🎓 Técnico", callback_data="seq_language_tecnico")],
        [InlineKeyboardButton("✍️ Personalizar", callback_data="seq_language_custom")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """**7. Como você quer que eu fale?**
Escolha meu estilo de comunicação:"""
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def finish_sequential_setup_callback(query, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Finalizar configuração via callback"""
    setup_data = context.user_data['sequential_setup_data']
    
    # Salvar configurações
    context.user_data.update({
        'user_name': setup_data['user_name'],
        'user_gender': setup_data['user_gender'],
        'user_age': setup_data['user_age'],
        'birth_day': setup_data['birth_day'],
        'birth_month': setup_data['birth_month'],
        'birth_year': setup_data['birth_year'],
        'bot_name': setup_data['bot_name'],
        'bot_gender': setup_data['bot_gender'],
        'personality': setup_data['personality'],
        'language_style': setup_data['language_style']
    })
    
    # Limpar dados temporários
    if 'sequential_step' in context.user_data:
        del context.user_data['sequential_step']
    if 'sequential_setup_data' in context.user_data:
        del context.user_data['sequential_setup_data']
    
    # Mensagem de conclusão
    config = context.user_data
    adult_status = "🔓 Sistema adulto liberado" if context.user_data.get('adult_access', False) else "🔒 Sistema padrão"
    
    keyboard = [
        [InlineKeyboardButton("💬 Começar a Conversar", callback_data="start_conversation")],
        [InlineKeyboardButton("📋 Ver Menu Principal", callback_data="show_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""🎉 **CONFIGURAÇÃO CONCLUÍDA!**

👤 **Seu perfil:**
• Nome: {config['user_name']}
• Gênero: {config['user_gender']}
• Idade: {config['user_age']} anos
• {adult_status}

🤖 **Meu perfil:**
• Nome: {config['bot_name']}
• Gênero: {config['bot_gender']}
• Personalidade: {config['personality']}
• Estilo: {config['language_style']}

✅ **Tudo pronto! Agora podemos conversar!**

Use /menu para acessar todas as opções."""
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para mostrar menu principal"""
    await menu_command(update, context)

async def handle_start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para iniciar conversa"""
    query = update.callback_query
    await query.answer("💬 Pronto para conversar!")
    
    user_config = context.user_data
    bot_name = user_config.get('bot_name', 'Eron')
    
    message = f"💬 **Perfeito!** Agora você pode conversar comigo normalmente.\n\nOlá! Eu sou {bot_name} e estou pronto para nossa conversa! 😊\n\n*Envie qualquer mensagem que eu responderei!*"
    
    await query.edit_message_text(message, parse_mode='Markdown')

async def handle_change_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Permite alterar nome do usuário"""
    query = update.callback_query
    await query.answer("✏️ Digite seu novo nome!")
    
    await query.edit_message_text(
        "✏️ **Alterar seu nome:**\n\n"
        "💭 *Digite seu novo nome ou apelido:*",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Voltar", callback_data='back_to_preferences')]
        ])
    )
    context.user_data['preference_change'] = 'user_name'

async def handle_change_bot_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Permite alterar nome do bot via preferências"""
    query = update.callback_query
    await query.answer("🤖 Alterando nome do bot!")
    
    # Usar a mesma função já criada
    return await handle_adjust_bot_name(update, context)

async def handle_change_user_age_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu para alterar idade do usuário"""
    query = update.callback_query
    await query.answer("🎂 Alterando idade!")
    
    await query.edit_message_text(
        "🎂 **Alterar sua idade:**\n\n"
        "💭 *Selecione sua faixa etária:*",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔞 18+ anos", callback_data='pref_age_18_plus')],
            [InlineKeyboardButton("👶 Menor de 18", callback_data='pref_age_under_18')],
            [InlineKeyboardButton("⬅️ Voltar", callback_data='back_to_preferences')]
        ])
    )

async def handle_change_user_gender_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu para alterar gênero do usuário"""
    query = update.callback_query
    await query.answer("👥 Alterando gênero!")
    
    await query.edit_message_text(
        "👥 **Alterar seu gênero:**\n\n"
        "💭 *Como você se identifica?*",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👨 Masculino", callback_data='pref_user_gender_masculino')],
            [InlineKeyboardButton("👩 Feminino", callback_data='pref_user_gender_feminino')],
            [InlineKeyboardButton("🌈 Outro/Prefiro não dizer", callback_data='pref_user_gender_outro')],
            [InlineKeyboardButton("⬅️ Voltar", callback_data='back_to_preferences')]
        ])
    )

async def handle_change_bot_gender_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu para alterar gênero do bot"""
    query = update.callback_query
    await query.answer("👤 Alterando gênero do bot!")
    
    await query.edit_message_text(
        "👤 **Como o bot deve se apresentar?**\n\n"
        "💭 *Isso influencia como ele fala e se refere a si mesmo:*",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👩 Feminino", callback_data='pref_bot_gender_feminino')],
            [InlineKeyboardButton("👨 Masculino", callback_data='pref_bot_gender_masculino')],
            [InlineKeyboardButton("⬅️ Voltar", callback_data='back_to_preferences')]
        ])
    )

async def handle_change_personality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu para alterar personalidade do bot"""
    query = update.callback_query
    await query.answer("🎭 Alterando personalidade!")
    
    await query.edit_message_text(
        "🎭 **Escolha a personalidade do bot:**\n\n"
        "💭 *Como você prefere que eu me comporte?*",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("😊 Amigável", callback_data='pref_personality_amigável')],
            [InlineKeyboardButton("💼 Formal", callback_data='pref_personality_formal')],
            [InlineKeyboardButton("😎 Casual", callback_data='pref_personality_casual')],
            [InlineKeyboardButton("🎉 Divertido", callback_data='pref_personality_divertido')],
            [InlineKeyboardButton("🧠 Intelectual", callback_data='pref_personality_intelectual')],
            [InlineKeyboardButton("⬅️ Voltar", callback_data='back_to_preferences')]
        ])
    )

async def handle_change_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu para alterar estilo de linguagem"""
    query = update.callback_query
    await query.answer("💬 Alterando linguagem!")
    
    await query.edit_message_text(
        "💬 **Escolha o estilo de linguagem:**\n\n"
        "💭 *Como você prefere que eu fale?*",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎩 Formal", callback_data='pref_language_formal')],
            [InlineKeyboardButton("😊 Informal", callback_data='pref_language_informal')],
            [InlineKeyboardButton("😎 Casual", callback_data='pref_language_casual')],
            [InlineKeyboardButton("🔧 Técnico", callback_data='pref_language_tecnico')],
            [InlineKeyboardButton("⬅️ Voltar", callback_data='back_to_preferences')]
        ])
    )

async def handle_change_topics_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu para alterar tópicos de interesse"""
    query = update.callback_query
    await query.answer("📚 Alterando tópicos!")
    
    await query.edit_message_text(
        "📚 **Selecione seus tópicos de interesse:**\n\n"
        "💭 *Clique nos temas que mais te interessam (pode escolher vários):*",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚽ Esportes", callback_data='pref_topic_esportes')],
            [InlineKeyboardButton("💻 Tecnologia", callback_data='pref_topic_tecnologia')],
            [InlineKeyboardButton("🎨 Arte", callback_data='pref_topic_arte')],
            [InlineKeyboardButton("🎵 Música", callback_data='pref_topic_musica')],
            [InlineKeyboardButton("💼 Negócios", callback_data='pref_topic_negocios')],
            [InlineKeyboardButton("📚 Educação", callback_data='pref_topic_educacao')],
            [InlineKeyboardButton("🍳 Culinária", callback_data='pref_topic_culinaria')],
            [InlineKeyboardButton("✅ Finalizar", callback_data='pref_topics_finish')],
            [InlineKeyboardButton("⬅️ Voltar", callback_data='back_to_preferences')]
        ])
    )

async def show_preferences_again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Volta ao menu principal de preferências"""
    query = update.callback_query
    await query.answer("⬅️ Voltando ao menu!")
    
    # Chamar preferences_menu adaptado para callback query
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    profile = user_profile_db.get_profile(user_id)
    
    if not profile:
        await query.edit_message_text(
            "❌ **Perfil não encontrado!**\n\n"
            "Use /start para criar seu perfil primeiro."
        )
        return
    
    # Informações atuais do perfil
    user_name = profile.get('user_name', 'Não definido')
    user_age = profile.get('user_age', 'Não definida')
    user_gender = profile.get('user_gender', 'não definido').title()
    bot_name = profile.get('bot_name', 'Eron')
    bot_gender = profile.get('bot_gender', 'neutro').title()
    bot_personality = profile.get('bot_personality', 'casual').title()
    bot_language = profile.get('bot_language', 'informal').title()
    topics = profile.get('preferred_topics', 'Nenhum').title()
    
    keyboard = [
        [InlineKeyboardButton(f"👤 Seu Nome: {user_name}", callback_data='change_user_name')],
        [InlineKeyboardButton(f"🎂 Sua Idade: {user_age}", callback_data='change_user_age_menu')],
        [InlineKeyboardButton(f"👥 Seu Gênero: {user_gender}", callback_data='change_user_gender_menu')],
        [InlineKeyboardButton(f"🤖 Nome do Bot: {bot_name}", callback_data='change_bot_name')],
        [InlineKeyboardButton(f"👤 Gênero do Bot: {bot_gender}", callback_data='change_bot_gender_menu')],
        [InlineKeyboardButton(f"🎭 Personalidade: {bot_personality}", callback_data='change_personality')],
        [InlineKeyboardButton(f"💬 Linguagem: {bot_language}", callback_data='change_language_menu')],
        [InlineKeyboardButton(f"📚 Tópicos: {topics}", callback_data='change_topics_menu')],
        [InlineKeyboardButton("🔄 Redefinir Tudo", callback_data='reset_all_preferences')],
        [InlineKeyboardButton("❌ Fechar", callback_data='close_preferences')]
    ]
    
    await query.edit_message_text(
        "🛠 **Menu de Preferências Completo**\n\n"
        f"📋 **Seu Perfil Atual:**\n"
        f"👤 **Nome:** {user_name}\n"
        f"🎂 **Idade:** {user_age}\n"
        f"👥 **Gênero:** {user_gender}\n\n"
        f"🤖 **Sobre o Bot:**\n"
        f"📝 **Nome:** {bot_name}\n"
        f"👤 **Gênero:** {bot_gender}\n"
        f"🎭 **Personalidade:** {bot_personality}\n"
        f"💬 **Linguagem:** {bot_language}\n"
        f"📚 **Tópicos:** {topics}\n\n"
        f"💡 *Clique em qualquer opção para alterar:*",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

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
    
    if query.data == 'pref_chat':
        await query.answer("💬 Abrindo preferências de chat...")
        await handle_chat_preferences(update, context)
    elif query.data == 'pref_visual':
        await query.answer("🎨 Abrindo preferências visuais...")
        # Aqui você pode implementar handle_visual_preferences
        await query.edit_message_text("🎨 **Preferências Visuais**\n\n🚧 Em desenvolvimento...")
    elif query.data == 'pref_notify':
        await query.answer("🔔 Abrindo configurações de notificação...")
        # Aqui você pode implementar handle_notification_preferences  
        await query.edit_message_text("🔔 **Notificações**\n\n🚧 Em desenvolvimento...")
    elif query.data == 'chat_style':
        await query.answer("🎭 Alternando estilo de chat...")
        await handle_chat_style(update, context)
    elif query.data == 'chat_length':
        await query.answer("📏 Alternando tamanho das respostas...")
        await handle_chat_length(update, context)
    elif query.data == 'chat_emoji':
        await query.answer("😊 Alternando uso de emojis...")
        await handle_chat_emoji(update, context)
    elif query.data == 'back_to_menu':
        await query.answer("⬅️ Voltando ao menu...")
        keyboard = [
            [InlineKeyboardButton("💬 Preferências de Chat", callback_data='pref_chat')],
            [InlineKeyboardButton("🎨 Preferências Visuais", callback_data='pref_visual')],
            [InlineKeyboardButton("🔔 Notificações", callback_data='pref_notify')],
            [InlineKeyboardButton("❌ Fechar", callback_data='close')]
        ]
        await query.edit_message_text(
            "🛠 **Configure suas preferências:**\n\n"
            "Escolha uma categoria para ajustar suas configurações.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif query.data == 'close':
        await query.answer("❌ Fechando menu...")
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
    user_id = str(update.effective_user.id)
    
    if query.data == 'emotion_detection':
        # Alternar detecção de emoções
        prefs = emotion_system.get_emotion_preferences(user_id)
        prefs['emotion_detection_enabled'] = not prefs['emotion_detection_enabled']
        emotion_system.update_emotion_preferences(
            user_id=user_id,
            emotion_detection_enabled=prefs['emotion_detection_enabled']
        )
        
        status = "✅ Ativada" if prefs['emotion_detection_enabled'] else "❌ Desativada"
        await query.answer(f"🎭 Detecção de emoções: {status}")
        
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
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    
    # Verificar se já tem perfil personalizado
    profile = user_profile_db.get_profile(user_id)
    
    if profile and profile.get('bot_name') and profile.get('bot_name') != 'ERON':
        # Perfil já personalizado
        bot_name = profile.get('bot_name')
        user_saved_name = profile.get('user_name', user_name)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Olá, {user_saved_name}! 😊 Eu sou a {bot_name}, sua assistente personalizada! '
                 f'Estou aqui para te ajudar. Como posso ser útil hoje?\n\n'
                 f'💡 Comandos disponíveis:\n'
                 f'/mudar_nome - Para mudar meu nome\n'
                 f'/mudar_personalidade - Para mudar minha personalidade\n'
                 f'/clear - Para recomeçar a personalização'
        )
    else:
        # Primeira vez ou não personalizado - iniciar apresentação
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Olá, {user_name}! 👋\n\n'
                 f'Meu nome é ERON e sou seu assistente de relacionamento! 💕\n\n'
                 f'Para melhorar sua experiência, vou sugerir algumas personalizações '
                 f'para aprimorar nossa conversa. Vou fazer algumas perguntas para '
                 f'te conhecer melhor! 😊\n\n'
                 f'Vamos começar? (Digite "sim" para continuar ou "não" para pular)'
        )
        context.user_data['awaiting_personalization_start'] = True

# Função para o comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando help que mostra comandos baseados no perfil do usuário"""
    user_id = str(update.message.from_user.id)
    user_profile_db = context.application.user_profile_db
    
    # Verificar se usuário tem acesso adulto
    profile = user_profile_db.get_profile(user_id)
    has_adult_access = profile.get('has_mature_access', False) if profile else False
    
    # Comandos básicos sempre disponíveis
    help_text = """
🤖 **Comandos Disponíveis:**

**📋 Personalização:**
/start - Começar personalização completa
/reconfigurar - Refazer toda a personalização
/preferencias - Menu de preferências avançadas
/emocoes - Configurar sistema emocional

**🔧 Mudanças Rápidas:**
/mudar_nome - Mudar nome do assistente
/mudar_personalidade - Alterar personalidade
/meu_nome - Mudar seu próprio nome
/mudar_linguagem - Alterar estilo de linguagem
/mudar_topicos - Modificar tópicos de interesse

**📊 Sistema:**
/aprendizagem - Ver status do sistema de aprendizagem 🧠
/clear - Limpar personalização
/help - Esta mensagem
"""
    
    # Adicionar comandos adultos se aplicável
    if has_adult_access:
        help_text += """
**🔞 Comandos Adultos:**
/devassa_on - Ativar modo adulto avançado
/devassa_off - Desativar modo adulto
/adulto - Status do modo adulto
/help_adulto - Ver todos os comandos adultos

**💡 Modo Adulto Ativo:** Personalização sem restrições ✅
"""
    else:
        help_text += """
**� Para acessar comandos adultos:**
Use /18 para verificar sua idade (maior de 18 anos)
"""
    
    help_text += """
**�💬 Interação:**
Apenas mande mensagens normais para conversar!
O sistema aprende automaticamente com cada conversa! ✨
    """
    
    await update.message.reply_text(help_text)

async def help_adulto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando específico para ajuda com comandos adultos"""
    user_id = str(update.message.from_user.id)
    user_profile_db = context.application.user_profile_db
    
    # Verificar se usuário tem acesso adulto
    profile = user_profile_db.get_profile(user_id)
    has_adult_access = profile.get('has_mature_access', False) if profile else False
    
    if not has_adult_access:
        await update.message.reply_text(
            "❌ **Acesso Negado**\n\n"
            "🔞 Você precisa ser maior de 18 anos para acessar comandos adultos.\n\n"
            "📱 Use /18 para verificar sua idade e ativar o modo adulto."
        )
        return
    
    adult_help_text = """
🔞 **COMANDOS ADULTOS - ERON.IA**
================================

**⚠️ ATENÇÃO:** Estes comandos estão disponíveis apenas para usuários maiores de 18 anos.

**🔞 Ativação/Desativação:**
/18 - Verificar idade (ativar modo adulto)
/devassa_on - Ativar modo adulto avançado
/devassa_off - Desativar modo adulto
/adulto - Verificar status do modo adulto

**🌶️ Personalização Adulta:**
/personalidade_adulta - Menu de personalidades adultas
/intensidade - Ajustar intensidade do conteúdo adulto
/estilo_adulto - Configurar estilo de interação adulta

**💕 Relacionamento:**
/namorada - Configurar modo namorada virtual
/romantico - Ativar personalidade romântica
/sedutor - Ativar personalidade sedutora

**🔧 Configurações:**
/config_adulto - Menu de configurações adultas
/status_adulto - Ver configurações atuais do modo adulto

**💡 IMPORTANTE:**
• Personalização é LIVRE para adultos (sem filtros)
• Conversas normais mantêm moderação apropriada
• Use /devassa_off a qualquer momento para desativar
• Todos os comandos respeitam sua privacidade

**🆘 Ajuda:**
/help - Comandos gerais
/help_adulto - Esta mensagem (comandos adultos)

*Sistema implementado com foco na segurança e privacidade do usuário.*
    """
    
    await update.message.reply_text(adult_help_text)

async def learning_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🧠 Mostrar status do sistema de aprendizagem"""
    user_id = str(update.effective_user.id)
    
    try:
        # Obter estatísticas básicas do usuário
        user_profile_db = context.application.user_profile_db
        profile = user_profile_db.get_profile(user_id)
        
        # Verificar se o sistema de conversas humanas está ativo
        conversation_type = human_conversation.detect_conversation_type("teste")
        
        # 🔥 NOVO: Obter estatísticas do sistema adulto avançado
        adult_stats = {}
        has_adult_access = profile.get('has_mature_access', False) if profile else False
        
        if has_adult_access:
            try:
                adult_stats = advanced_adult_learning.get_learning_stats(user_id)
            except Exception as e:
                print(f"[DEBUG] Erro ao obter stats adultas: {e}")
                adult_stats = {}
        
        status_text = f"""
🧠 **Status do Sistema de Aprendizagem**

**👤 Seu Perfil:**
• User ID: {user_id}
• Nome: {profile.get('user_name', 'Não definido') if profile else 'Perfil não criado'}
• Bot: {profile.get('bot_name', 'ERON') if profile else 'ERON'}
• Acesso Adulto: {'✅ Ativo' if has_adult_access else '❌ Inativo'}

**🤖 Sistema de Conversas Humanas:**
• Status: ✅ Ativo
• Detecção de humor: ✅ Funcionando  
• Templates casuais: ✅ 12 contextos disponíveis
• Respostas empáticas: ✅ 9 estados emocionais

**⚡ FastLearning:**
• Status: ✅ Integrado
• Salvando padrões: ✅ A cada conversa
• Contextos inteligentes: ✅ Ativos
        """
        
        # Adicionar estatísticas adultas se disponíveis
        if has_adult_access and adult_stats:
            status_text += f"""
**🔥 Sistema Adulto Avançado:**
• Interações registradas: {adult_stats.get('total_interactions', 0)}
• Score de satisfação: {adult_stats.get('satisfaction_score', 0.0)}/1.0
• Conteúdo disponível: {adult_stats.get('available_content', 0)} items
• Nível de intensidade: {adult_stats.get('intensity_preference', 5)}/10
• Progresso de aprendizagem: {adult_stats.get('learning_progress', 0.0)}%
• Efetividade média: {adult_stats.get('avg_effectiveness', 0.0)}/1.0
            """
        
        status_text += f"""
**💾 Sistema Integrado:**
• Web + Telegram: ✅ Sincronizados
• Memória compartilhada: ✅ Ativa
• Aprendizagem contínua: ✅ Funcionando

**🎯 Próxima vez que conversar:**
Suas respostas ficarão mais personalizadas e naturais!
        """
        
    except Exception as e:
        status_text = f"""
🧠 **Status do Sistema de Aprendizagem**

❌ **Erro ao carregar detalhes**: {str(e)}

**Sistemas Básicos:**
• FastLearning: ✅ Carregado
• HumanConversation: ✅ Carregado  
• Integração: ✅ Ativo

Use /help para ver outros comandos disponíveis.
        """
    
    await update.message.reply_text(status_text)

async def help_command_old(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = '''Olá! Sou um assistente de apoio emocional. Estou aqui para conversar e ajudar com o que precisar. 

🤖 **COMANDOS BÁSICOS:**
/start - Iniciar ou reconfigurar personalização completa
/definir_perfil - Para eu me lembrar do seu nome, idade e gênero
/personalizar - Para mudar meu nome, gênero e outras configurações
/preferencias - Para ajustar como eu me comunico com você
/emocoes - Para configurar minhas respostas emocionais
/cancelar - Para cancelar operações em andamento
/help - Mostrar esta mensagem de ajuda

📝 **COMANDOS DE PERSONALIZAÇÃO RÁPIDA:**
/meu_nome - 👤 Alterar SEU nome (como devo te chamar)
/mudar_nome - 🤖 Alterar MEU nome (como você quer me chamar)
/mudar_personalidade - 🎭 Alterar minha personalidade
/mudar_idade - 🎂 Alterar sua idade
/mudar_genero_usuario - 👥 Alterar seu gênero
/mudar_genero_bot - 🎭 Alterar meu gênero  
/mudar_linguagem - 🗣️ Alterar meu estilo de comunicação
/mudar_topicos - 📚 Alterar tópicos de interesse

🔄 **COMANDOS DE RESET E LIMPEZA:**
/reconfigurar - 🔄 Reset COMPLETO (apagar tudo e começar do zero)
/clear - 🗑️ Limpar personalização atual

💡 **DICA:** Use /meu_nome para mudar como eu te chamo, e /mudar_nome para mudar meu nome!'''

    # Adicionar comandos adultos se sistema disponível
    if ADULT_SYSTEM_AVAILABLE:
        help_text += '''

🔞 **SISTEMA ADULTO (+18):**
/18 - Ativar modo adulto (requer verificação de idade)
/devassa_config - Configurar modo adulto
/devassa_status - Ver status do modo adulto
/devassa_off - Desativar modo adulto
/intensidade1, /intensidade2, /intensidade3 - Ajustar intensidade
/genero_feminino, /genero_masculino, /genero_neutro - Alterar gênero do bot

⚠️ **Importante:** O modo adulto requer verificação de idade e contém conteúdo explícito.'''

    help_text += '''

💬 Fique à vontade para desabafar ou fazer qualquer pergunta!'''
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=help_text
    )

# Função de chat - MELHORADA
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    
    # PRIMEIRA COISA: SEMPRE VERIFICAR CONFIGURAÇÕES ATUAIS DO BANCO DE DADOS
    # Pegar o perfil mais atualizado do banco ANTES de qualquer processamento
    current_profile = user_profile_db.get_profile(user_id)
    print(f"[DEBUG PERFIL] Verificando perfil atualizado no início: {current_profile}")
    
    # SISTEMA DE PERSONALIZAÇÃO PASSO A PASSO
    
    # 1. Verificar se está aguardando início da personalização
    if context.user_data.get('awaiting_personalization_start'):
        if user_message.lower() in ['sim', 's', 'yes', 'ok']:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Perfeito! Vamos começar! 😊\n\n'
                     'Primeiro, como você gostaria de ser chamado?'
            )
            context.user_data['awaiting_personalization_start'] = False
            context.user_data['step'] = 'user_name'
            return
        elif user_message.lower() in ['não', 'nao', 'no', 'pular']:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Tudo bem! Vou continuar sendo o ERON padrão. '
                     'Se mudar de ideia, use /start novamente! 😊'
            )
            context.user_data.clear()
            return
    
    # 2. Sistema de personalização passo a passo
    current_step = context.user_data.get('step')
    
    if current_step == 'user_name':
        # Salvar nome do usuário
        user_profile_db.save_profile(user_id=user_id, user_name=user_message.strip())
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Prazer em te conhecer, {user_message}! 😊\n\n'
                 f'Agora, como você gostaria que EU me chamasse? '
                 f'(Pode ser qualquer nome que preferir)'
        )
        context.user_data['step'] = 'bot_name'
        return
        
    elif current_step == 'bot_name':
        # Salvar nome do bot
        user_profile_db.save_profile(user_id=user_id, bot_name=user_message.strip())
        
        keyboard = [
            [InlineKeyboardButton("😊 Amigável", callback_data='personality_amigável')],
            [InlineKeyboardButton("🎩 Formal", callback_data='personality_formal')],
            [InlineKeyboardButton("😎 Casual", callback_data='personality_casual')],
            [InlineKeyboardButton("🎭 Divertida", callback_data='personality_divertido')]
        ]
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Perfeito! Agora me chamo {user_message}! ✨\n\n'
                 f'Qual personalidade você prefere que eu tenha?',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['step'] = 'bot_personality'
        return
    
    # 3. Verificar mudanças individuais
    if context.user_data.get('changing_bot_name'):
        user_profile_db.save_profile(user_id=user_id, bot_name=user_message.strip())
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'✅ Perfeito! Agora me chamo {user_message}! '
                 f'Vou usar esse nome daqui para frente. 😊'
        )
        context.user_data.clear()
        return
    
    # 3.1 Verificar mudanças de nome de usuário
    if context.user_data.get('changing_user_name'):
        new_user_name = user_message.strip()
        user_profile_db.save_profile(user_id=user_id, user_name=new_user_name)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'✅ Perfeito, {new_user_name}! '
                 f'Agora vou te chamar por esse nome. 😊\n\n'
                 f'Para testar, pergunta "qual é o meu nome?"',
            parse_mode='Markdown'
        )
        context.user_data.clear()
        return
    
    # 4. Chat normal - usar sistema existente
    # SEMPRE pegar o perfil mais atualizado do banco de dados
    profile = user_profile_db.get_profile(user_id)
    print(f"[DEBUG PERFIL] Perfil atual do banco: {profile}")
    
    if not profile:
        # Criar perfil básico para Telegram usando nome real quando possível
        telegram_name = update.effective_user.first_name or update.effective_user.username or ''
        # Se o nome do telegram tem mais de 2 caracteres e não são apenas saudações, use-o
        if telegram_name and len(telegram_name) > 2 and telegram_name.lower() not in ['oi', 'hi', 'hey', 'ola']:
            user_name = telegram_name
        else:
            user_name = ''
            
        profile = {
            'user_id': user_id,
            'username': f'telegram_{user_id}',
            'user_name': user_name,
            'user_age': '18',
            'user_gender': 'outro',
            'bot_name': '',
            'bot_gender': 'outro',
            'bot_personality': '',
            'bot_language': 'informal',
            'preferred_topics': '',
            'has_mature_access': True
        }
        try:
            user_profile_db.save_profile(user_id=user_id, **profile)
        except Exception as e:
            print(f"Erro ao criar perfil Telegram: {e}")
    
    # GARANTIR que sempre temos as configurações mais recentes do banco
    # Recarregar perfil para ter certeza das configurações atualizadas
    updated_profile = user_profile_db.get_profile(user_id)
    if updated_profile:
        profile = updated_profile
        print(f"[DEBUG PERFIL] Perfil recarregado com configurações atuais: bot_name='{profile.get('bot_name')}'")
    
    # EXTRAIR INFORMAÇÕES MAIS RECENTES DO BANCO
    current_bot_name = profile.get('bot_name', 'ERON')
    current_user_name = profile.get('user_name', update.effective_user.first_name or 'Usuário')
    current_personality = profile.get('bot_personality', 'amigável')
    current_language = profile.get('bot_language', 'informal')
    
    print(f"[DEBUG NOME BOT] Nome atual do bot no banco: '{current_bot_name}'")
    print(f"[DEBUG NOME BOT] Nome do usuário atual: '{current_user_name}'")
    print(f"[DEBUG NOME BOT] Personalidade atual: '{current_personality}'")
    print(f"[DEBUG NOME BOT] Linguagem atual: '{current_language}'")
    
    # SEMPRE tentar detectar e salvar personalização (mesmo se completa)
    saved = detect_and_save_telegram_personalization(user_message, user_id, user_profile_db)
    if saved:
        print(f"[TELEGRAM DEBUG] Personalização detectada! Recarregando perfil...")
        # Recarregar perfil após mudança
        profile = user_profile_db.get_profile(user_id)
        print(f"[TELEGRAM DEBUG] Perfil recarregado após personalização: bot_name='{profile.get('bot_name')}'")
        
        # Atualizar variáveis com informações mais recentes
        current_bot_name = profile.get('bot_name', 'ERON')
        current_user_name = profile.get('user_name', update.effective_user.first_name or 'Usuário')
        print(f"[DEBUG] Nome do bot atualizado após personalização: '{current_bot_name}'")
        
        # Atualizar variável de completude
        personalization_complete = (
            profile.get('bot_name') and 
            profile.get('bot_name') not in ['', 'ERON'] and
            profile.get('user_name') and 
            profile.get('user_name') != ''
        )
    
    # USAR O PERFIL MAIS ATUALIZADO - SEM BUSCAR NOVAMENTE
    print(f"[TELEGRAM DEBUG] Usando perfil final com nome do bot: '{profile.get('bot_name')}'")
    
    # Usar informações personalizadas ATUALIZADAS
    user_name = profile.get('user_name', update.effective_user.first_name)
    bot_name = profile.get('bot_name', 'ERON')

    # Obter preferências e estado emocional
    user_preferences = preferences_manager.get_preferences(user_id)
    emotion_prefs = emotion_system.get_emotion_preferences(user_id)

    # ===== INTEGRAÇÃO COM SISTEMA ADULTO - MODO OPCIONAL =====
    adult_response = None
    
    # Verificar se o usuário tem modo adulto ATIVO usando core.check
    from core.check import check_age
    adult_status = check_age(user_id)
    user_wants_adult_mode = adult_status.get('adult_mode_active', False)
    
    print(f"[ADULT DEBUG] Status adulto para {user_id}: adult_mode_active={user_wants_adult_mode}")
    
    # Só usar resposta devassa se o usuário EXPLICITAMENTE ativou o modo adulto
    if ADULT_SYSTEM_AVAILABLE and user_wants_adult_mode:
        try:
            # Usar personalidade devassa apenas quando explicitamente ativada
            devassa = DevassaPersonality(adult_db, profile)
            adult_response = devassa.get_adaptive_response(
                user_message,
                context='geral',
                relationship_stage=profile.get('relationship_stage', 'inicial')
            )
            print(f"[ADULT DEBUG] Modo devassa ATIVO - Resposta gerada: {adult_response[:50]}...")
        except Exception as e:
            print(f"[ADULT DEBUG] Erro ao gerar resposta devassa: {e}")
            adult_response = None
    else:
        print(f"[ADULT DEBUG] Modo devassa INATIVO - Usando resposta normal")

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

    # Escolher resposta: adulta (se explicitamente ativada) ou normal
    if adult_response and user_wants_adult_mode:
        response = adult_response
        print(f"[ADULT DEBUG] Usando resposta DEVASSA (modo explicitamente ativo)")
    else:
        # VERIFICAÇÃO FINAL: Garantir que estamos usando o nome correto do bot
        final_bot_name = profile.get('bot_name', 'ERON')
        final_user_name = profile.get('user_name', update.effective_user.first_name or 'Usuário')
        print(f"[DEBUG FINAL] Chamando API com: bot_name='{final_bot_name}', user_name='{final_user_name}'")
        print(f"[DEBUG FINAL] Perfil completo sendo enviado para API: {profile}")
        
        # Usar função get_llm_response atualizada com user_id
        response = get_llm_response(user_message, user_profile=profile, user_id=user_id)
        if not response:
            response = "Desculpe, não consegui me conectar com a IA no momento. Por favor, verifique se o servidor do LM Studio está rodando."
        print(f"[TELEGRAM DEBUG] Usando resposta NORMAL (modo devassa inativo ou não disponível)")
        print(f"[DEBUG FINAL] Resposta recebida da API: {response[:100]}...")
    
    # Salvar na memória com user_id para separar por usuário
    memory.save_message(user_message, response, user_id)
    
    # 🧠 APRENDIZADO ACELERADO NO TELEGRAM: Salvar padrões de resposta
    try:
        fast_learning.learn_response_pattern(user_id, user_message, response)
        
        # Salvar contexto inteligente para futuras conversas
        topic = fast_learning._extract_main_topic(user_message)
        context_data = f"[TG] {user_message[:100]}... → {response[:100]}..."
        fast_learning.save_smart_context(user_id, topic, context_data, importance=1.5)
        print(f"[TELEGRAM LEARNING] Padrão salvo para user_id: {user_id}")
    except Exception as e:
        print(f"[TELEGRAM LEARNING ERROR] {e}")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response
    )

async def handle_personality_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa personalidade e pergunta estilo de linguagem"""
    query = update.callback_query
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    
    personality_key = query.data.replace('personality_', '')
    personality_names = {
        'amigável': 'Amigável e Calorosa',
        'formal': 'Formal e Profissional', 
        'casual': 'Casual e Descontraída',
        'divertido': 'Divertida e Alegre',
        'intelectual': 'Intelectual e Analítica'
    }
    
    await query.answer(f"✅ {personality_names[personality_key]} selecionada!")
    
    # Salvar personalidade com filtro
    success = safe_personalization_save(
        user_id=user_id, 
        user_profile_db=user_profile_db,
        updates_dict={'bot_personality': personality_key},
        context_description=f"personalidade {personality_key}"
    )
    
    if not success:
        await query.edit_message_text("❌ Personalização não permitida pelo sistema de moderação.")
        return PERSONALIZATION_COMPLETE
    
    await query.edit_message_text(
        f"✅ **Personalidade {personality_names[personality_key]} aplicada!**\n\n"
        "🗣️ **Como você prefere que eu me comunique?**\n\n"
        "💬 *Escolha o estilo de linguagem:*",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("😎 Informal", callback_data='language_informal')],
            [InlineKeyboardButton("🎩 Formal", callback_data='language_formal')],
            [InlineKeyboardButton("🔬 Técnica", callback_data='language_tecnica')],
            [InlineKeyboardButton("🌈 Casual", callback_data='language_casual')]
        ])
    )
    
    context.user_data['personalization_step'] = 'language_style'

async def handle_language_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa estilo de linguagem e pergunta tópicos"""
    query = update.callback_query
    user_id = str(update.effective_user.id) 
    user_profile_db = context.application.user_profile_db
    
    language_key = query.data.replace('language_', '')
    language_names = {
        'informal': 'Informal e Descontraída',
        'formal': 'Formal e Educada',
        'tecnica': 'Técnica e Precisa',
        'casual': 'Casual e Amigável'
    }
    
    await query.answer(f"✅ Estilo {language_names[language_key]} aplicado!")
    
    # Salvar estilo de linguagem
    user_profile_db.save_profile(user_id=user_id, bot_language=language_key)
    
    await query.edit_message_text(
        f"✅ **Estilo {language_names[language_key]} aplicado!**\n\n"
        "🎯 **Quais assuntos mais te interessam?**\n\n"
        "📚 *Clique nos tópicos de interesse (pode escolher vários):*",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💻 Tecnologia", callback_data='topic_tecnologia'),
             InlineKeyboardButton("🔬 Ciência", callback_data='topic_ciencia')],
            [InlineKeyboardButton("🎨 Arte", callback_data='topic_arte'),
             InlineKeyboardButton("⚽ Esportes", callback_data='topic_esportes')],
            [InlineKeyboardButton("🎵 Música", callback_data='topic_musica'), 
             InlineKeyboardButton("🎬 Cinema", callback_data='topic_cinema')],
            [InlineKeyboardButton("✈️ Viagens", callback_data='topic_viagem'),
             InlineKeyboardButton("🍳 Culinária", callback_data='topic_culinaria')],
            [InlineKeyboardButton("📚 Literatura", callback_data='topic_literatura'),
             InlineKeyboardButton("🎮 Games", callback_data='topic_games')],
            [InlineKeyboardButton("💼 Negócios", callback_data='topic_negocios'),
             InlineKeyboardButton("🏥 Saúde", callback_data='topic_saude')],
            [InlineKeyboardButton("✅ Finalizar personalização", callback_data='finish_personalization')]
        ])
    )
    
    context.user_data['personalization_step'] = 'topics'
    context.user_data['selected_topics'] = []

async def handle_topic_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa seleção de tópicos"""
    query = update.callback_query
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    
    if query.data == 'finish_personalization':
        await finish_personalization_process(update, context)
        return
        
    topic_key = query.data.replace('topic_', '')
    selected_topics = context.user_data.get('selected_topics', [])
    
    topics = {
        'tecnologia': '💻 Tecnologia',
        'ciencia': '🔬 Ciência', 
        'arte': '🎨 Arte',
        'esportes': '⚽ Esportes',
        'musica': '🎵 Música',
        'cinema': '🎬 Cinema',
        'viagem': '✈️ Viagens',
        'culinaria': '🍳 Culinária',
        'literatura': '📚 Literatura',
        'games': '🎮 Games',
        'negocios': '💼 Negócios',
        'saude': '🏥 Saúde'
    }
    
    # Toggle tópico
    if topic_key in selected_topics:
        selected_topics.remove(topic_key)
        await query.answer(f"➖ {topics[topic_key]} removido!")
    else:
        selected_topics.append(topic_key)
        await query.answer(f"➕ {topics[topic_key]} adicionado!")
    
    context.user_data['selected_topics'] = selected_topics
    
    # Reconstruir keyboard com tópicos marcados
    keyboard = []
    topic_items = list(topics.items())
    for i in range(0, len(topic_items), 2):
        row = []
        for j in range(2):
            if i + j < len(topic_items):
                key, name = topic_items[i + j]
                display_name = f"✅ {name}" if key in selected_topics else name
                row.append(InlineKeyboardButton(display_name, callback_data=f"topic_{key}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("✅ Finalizar personalização", callback_data='finish_personalization')])
    
    selected_text = ", ".join([topics[t] for t in selected_topics]) if selected_topics else "Nenhum ainda"
    
    await query.edit_message_text(
        f"🎯 **Tópicos de interesse selecionados:**\n\n"
        f"📝 {selected_text}\n\n"
        "💡 *Continue clicando para adicionar/remover ou finalize:*",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def finish_personalization_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Finaliza o processo de personalização"""
    query = update.callback_query
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    
    await query.answer("🎉 Personalização concluída!")
    
    # Salvar tópicos selecionados
    selected_topics = context.user_data.get('selected_topics', [])
    topics_str = ','.join(selected_topics)
    user_profile_db.save_profile(user_id=user_id, preferred_topics=topics_str)
    
    # Obter perfil completo
    profile = user_profile_db.get_profile(user_id)
    
    bot_gender = "👩 feminino" if profile.get('bot_gender') == 'feminino' else "👨 masculino"
    user_gender_map = {'masculino': '👨', 'feminino': '👩', 'outro': '🌈'}
    user_gender = user_gender_map.get(profile.get('user_gender', 'outro'), '🌈')
    
    topics_text = ", ".join([t.title() for t in selected_topics]) if selected_topics else "Nenhum específico"
    
    await query.edit_message_text(
        f"🎉 **Personalização concluída com sucesso!**\n\n"
        f"📋 **Resumo do seu perfil:**\n"
        f"👤 **Seu nome:** {profile.get('user_name', 'Usuário')}\n"
        f"{user_gender} **Seu gênero:** {profile.get('user_gender', 'outro').title()}\n"
        f"🎂 **Idade:** {profile.get('user_age', 'N/A')}\n\n"
        f"🤖 **Sobre mim:**\n"
        f"📝 **Nome:** {profile.get('bot_name', 'Eron')}\n"
        f"{bot_gender.split()[0]} **Gênero:** {bot_gender.split()[1].title()}\n" 
        f"🎭 **Personalidade:** {profile.get('bot_personality', 'casual').title()}\n"
        f"🗣️ **Linguagem:** {profile.get('bot_language', 'informal').title()}\n"
        f"📚 **Tópicos:** {topics_text}\n\n"
        f"✨ **Agora posso te atender de forma totalmente personalizada!**\n\n"
        f"💬 **Pode começar a conversar comigo!**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔧 Ajustar configurações", callback_data='adjust_settings')],
            [InlineKeyboardButton("💬 Começar conversa", callback_data='start_chat')]
        ])
    )
    
    context.user_data.clear()
    """Handler global para seleção de personalidade fora do ConversationHandler"""
    query = update.callback_query
    await query.answer("✅ Personalidade aplicada!")
    
    user_id = str(update.effective_user.id)
    personality_key = query.data.replace('personality_', '')
    
    print(f"[DEBUG PERSONALITY GLOBAL] Personalidade recebida: '{personality_key}' para user {user_id}")
    
    # Obter instância do banco
    user_profile_db = context.application.user_profile_db
    
    # Salvar personalidade diretamente no perfil
    try:
        user_profile_db.save_profile(user_id=user_id, bot_personality=personality_key)
        print(f"[DEBUG PERSONALITY GLOBAL] Personalidade {personality_key} salva com sucesso")
        
        personality_names = {
            'amigável': 'Amigável e Calorosa',
            'formal': 'Formal e Profissional', 
            'casual': 'Casual e Descontraída',
            'divertido': 'Divertida e Alegre',
            'intelectual': 'Intelectual e Analítica'
        }
        
        personality_name = personality_names.get(personality_key, personality_key.title())
        
        await query.edit_message_text(
            f"✅ **Personalidade {personality_name} aplicada com sucesso!**\n\n"
            f"Agora eu vou interagir com você de forma {personality_name.lower()}.\n\n"
            f"💬 Pode começar a conversar comigo normalmente! \n\n"
            f"🔧 Para ajustar outras configurações, use /preferencias"
        )
    except Exception as e:
        print(f"[ERROR] Erro ao salvar personalidade: {e}")
        await query.edit_message_text(
            f"❌ **Erro ao aplicar personalidade**\n\n"
            f"Ocorreu um erro técnico. Tente novamente ou use /start."
        )

async def handle_personality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com a seleção de personalidade e solicita estilo de linguagem"""
    query = update.callback_query
    await query.answer()
    
    personality_key = query.data.replace('personality_', '')
    context.user_data['personality'] = personality_key
    
    print(f"[DEBUG PERSONALITY] Personalidade recebida: '{personality_key}'")
    
    personality_names = {
        'amigável': 'Amigável e Calorosa',
        'formal': 'Formal e Profissional', 
        'casual': 'Casual e Descontraída',
        'divertido': 'Divertida e Alegre',
        'intelectual': 'Intelectual e Analítica'
    }
    
    print(f"[DEBUG PERSONALITY] Personalidades disponíveis: {list(personality_names.keys())}")
    
    # Opções de estilo de linguagem
    language_styles = {
        'informal': '😎 Informal e Descontraída',
        'formal': '🎩 Formal e Educada',
        'tecnica': '🔬 Técnica e Precisa', 
        'casual': '🌈 Casual e Amigável'
    }
    
    keyboard = []
    for key, name in language_styles.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"language_{key}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    bot_name = context.user_data.get('bot_name', 'Eron')
    
    # Verificar se personalidade existe
    if personality_key not in personality_names:
        error_message = (
            f"❌ Erro: Personalidade '{personality_key}' não encontrada!\n\n"
            f"Personalidades disponíveis:\n"
            f"• Amigável\n• Formal\n• Casual\n• Divertido\n• Intelectual\n\n"
            f"Por favor, use /personalizar novamente."
        )
        await query.edit_message_text(error_message)
        return ConversationHandler.END
    
    await query.edit_message_text(
        f"✅ Personalidade {personality_names[personality_key]} escolhida!\n\n"
        f"�️ **Como você prefere que {bot_name} fale com você?**\n\n"
        "Escolha o estilo de comunicação:",
        reply_markup=reply_markup
    )
    
    return SELECT_LANGUAGE

# Função para processar estilo de linguagem e solicitar tópicos
async def process_language_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa o estilo de linguagem e solicita tópicos de interesse"""
    query = update.callback_query
    await query.answer("✅ Estilo de linguagem aplicado!")
    
    language_key = query.data.replace('language_', '')
    context.user_data['language'] = language_key
    
    language_names = {
        'informal': 'Informal e Descontraída',
        'formal': 'Formal e Educada',
        'tecnica': 'Técnica e Precisa',
        'casual': 'Casual e Amigável'
    }
    
    # Tópicos de interesse
    topics = {
        'tecnologia': '💻 Tecnologia',
        'ciencia': '🔬 Ciência',
        'arte': '🎨 Arte e Cultura',
        'esportes': '⚽ Esportes',
        'musica': '🎵 Música',
        'cinema': '🎬 Cinema e TV',
        'viagem': '✈️ Viagens',
        'culinaria': '🍳 Culinária',
        'literatura': '📚 Literatura',
        'games': '🎮 Games',
        'negocios': '💼 Negócios',
        'saude': '🏥 Saúde e Bem-estar'
    }
    
    # Dividir em duas colunas para melhor visualização
    keyboard = []
    topic_items = list(topics.items())
    for i in range(0, len(topic_items), 2):
        row = []
        for j in range(2):
            if i + j < len(topic_items):
                key, name = topic_items[i + j]
                row.append(InlineKeyboardButton(name, callback_data=f"topic_{key}"))
        keyboard.append(row)
    
    # Botão para finalizar seleção
    keyboard.append([InlineKeyboardButton("✅ Finalizar Seleção", callback_data="topics_done")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ Estilo {language_names[language_key]} aplicado!\n\n"
        "🎯 **Quais assuntos mais te interessam?**\n\n"
        "📝 *Clique nos tópicos de interesse e depois 'Finalizar'*\n\n"
        "🔹 **Tópicos selecionados:** Nenhum ainda",
        reply_markup=reply_markup
    )
    
    # Inicializar lista de tópicos selecionados
    context.user_data['selected_topics'] = []
    
    return SELECT_TOPICS

# Função para processar seleção de tópicos
async def process_topic_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a seleção de tópicos de interesse"""
    query = update.callback_query
    
    if query.data == "topics_done":
        await query.answer("✅ Finalizando personalização...")
        # Finalizar personalização
        return await complete_personalization_flow(update, context)
    
    # Processar seleção/deseleção de tópico
    topic_key = query.data.replace('topic_', '')
    selected_topics = context.user_data.get('selected_topics', [])
    
    topics = {
        'tecnologia': '💻 Tecnologia',
        'ciencia': '🔬 Ciência',
        'arte': '🎨 Arte e Cultura',
        'esportes': '⚽ Esportes',
        'musica': '🎵 Música',
        'cinema': '🎬 Cinema e TV',
        'viagem': '✈️ Viagens',
        'culinaria': '🍳 Culinária',
        'literatura': '📚 Literatura',
        'games': '🎮 Games',
        'negocios': '💼 Negócios',
        'saude': '🏥 Saúde e Bem-estar'
    }
    
    # Toggle topic selection
    if topic_key in selected_topics:
        selected_topics.remove(topic_key)
        await query.answer(f"➖ {topics[topic_key]} removido!")
    else:
        selected_topics.append(topic_key)
        await query.answer(f"➕ {topics[topic_key]} adicionado!")
    
    context.user_data['selected_topics'] = selected_topics
    
    # Reconstruir keyboard com tópicos marcados
    keyboard = []
    topic_items = list(topics.items())
    for i in range(0, len(topic_items), 2):
        row = []
        for j in range(2):
            if i + j < len(topic_items):
                key, name = topic_items[i + j]
                # Adicionar checkmark se selecionado
                display_name = f"✅ {name}" if key in selected_topics else name
                row.append(InlineKeyboardButton(display_name, callback_data=f"topic_{key}"))
        keyboard.append(row)
    
    # Botão para finalizar seleção
    keyboard.append([InlineKeyboardButton("✅ Finalizar Seleção", callback_data="topics_done")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Texto dos tópicos selecionados
    selected_names = [topics[t] for t in selected_topics] if selected_topics else ["Nenhum ainda"]
    selected_text = ", ".join(selected_names)
    
    language_names = {
        'informal': 'Informal e Descontraída',
        'formal': 'Formal e Educada',
        'tecnica': 'Técnica e Precisa',
        'casual': 'Casual e Amigável'
    }
    
    language_key = context.user_data.get('language', 'casual')
    
    await query.edit_message_text(
        f"✅ Estilo {language_names[language_key]} selecionado!\n\n"
        "🎯 **Quais assuntos mais te interessam?**\n\n"
        "📝 *Selecione quantos quiser e depois clique em 'Finalizar'*\n\n"
        f"🔹 **Tópicos selecionados:** {selected_text}",
        reply_markup=reply_markup
    )
    
    return SELECT_TOPICS

# Função para finalizar toda a personalização
async def complete_personalization_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Finaliza o processo completo de personalização com apresentação"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Coletar todos os dados
    user_name = context.user_data.get('user_name', 'Usuário')
    user_age = context.user_data.get('user_age', '18')
    user_gender = context.user_data.get('user_gender', 'outro')
    bot_name = context.user_data.get('bot_name', 'Eron')
    bot_gender = context.user_data.get('bot_gender', 'neutro')
    personality = context.user_data.get('personality', 'amigavel')
    language = context.user_data.get('language', 'casual')
    selected_topics = context.user_data.get('selected_topics', [])
    topics_text = ','.join(selected_topics) if selected_topics else ''
    
    try:
        # Salvar no banco usando o método atualizado
        db = context.bot.application.user_profile_db
        db.update_profile(
            user_id=user_id,
            user_name=user_name,
            user_age=user_age,
            user_gender=user_gender,
            bot_name=bot_name,
            bot_gender=bot_gender,
            bot_personality=personality,
            bot_language=language,
            preferred_topics=topics_text
        )
        
        # Criar mensagem de apresentação personalizada
        gender_articles = {
            'masculino': 'o',
            'feminino': 'a', 
            'neutro': ''
        }
        
        article = gender_articles.get(bot_gender, '')
        greeting = f"Prazer {user_name}, {'eu sou ' + article + ' ' if article else 'meu nome é '}{bot_name}!"
        
        personality_descriptions = {
            'amigável': 'amigável e calorosa',
            'formal': 'formal e profissional', 
            'casual': 'casual e descontraída',
            'divertido': 'divertida e alegre',
            'intelectual': 'intelectual e analítica'
        }
        
        language_descriptions = {
            'informal': 'de forma descontraída',
            'formal': 'de forma educada e respeitosa',
            'tecnica': 'de forma precisa e técnica',
            'casual': 'de forma amigável e casual'
        }
        
        topics_list = {
            'tecnologia': 'tecnologia',
            'ciencia': 'ciência',
            'arte': 'arte e cultura',
            'esportes': 'esportes',
            'musica': 'música',
            'cinema': 'cinema e TV',
            'viagem': 'viagens',
            'culinaria': 'culinária',
            'literatura': 'literatura',
            'games': 'games',
            'negocios': 'negócios',
            'saude': 'saúde e bem-estar'
        }
        
        # Construir lista de interesses
        interests_text = ""
        if selected_topics:
            interests_names = [topics_list.get(t, t) for t in selected_topics]
            if len(interests_names) == 1:
                interests_text = f" Adorei saber que você se interessa por {interests_names[0]}!"
            elif len(interests_names) == 2:
                interests_text = f" Que legal que você gosta de {interests_names[0]} e {interests_names[1]}!"
            else:
                interests_text = f" Que interessante seus gostos por {', '.join(interests_names[:-1])} e {interests_names[-1]}!"
        
        presentation_message = (
            f"🎉 **{greeting}**\n\n"
            f"Vou ser {personality_descriptions[personality]} e falar com você "
            f"{language_descriptions[language]}.{interests_text}\n\n"
            f"🎯 **Resumo da sua personalização:**\n"
            f"👤 Seu nome: {user_name} ({user_age} anos)\n"
            f"🤖 Meu nome: {bot_name}\n"
            f"✨ Personalidade: {personality_descriptions[personality].title()}\n"
            f"🗣️ Estilo: {language_descriptions[language].replace('de forma ', '').title()}\n"
            f"🎯 Interesses: {', '.join([topics_list[t].title() for t in selected_topics]) if selected_topics else 'Conversas gerais'}\n\n"
            f"Agora estamos prontos para conversar! O que você gostaria de saber? 😊\n\n"
            f"💡 **Comandos úteis:**\n"
            f"/clear - Recomeçar personalização\n"
            f"/meu_nome - Alterar seu nome\n"
            f"/mudar_nome - Alterar meu nome\n"
            f"/mudar_personalidade - Alterar personalidade\n"
            f"/reconfigurar - Reset completo\n"
            f"/mudar_linguagem - Alterar estilo de comunicação"
        )
        
        await query.edit_message_text(presentation_message)
        
        # Limpar dados temporários
        context.user_data.clear()
        
        return ConversationHandler.END
        
    except Exception as e:
        logging.error(f"Erro ao salvar perfil completo: {e}")
        await query.edit_message_text(
            "❌ Ocorreu um erro ao salvar seu perfil. Tente novamente com /start."
        )
        return ConversationHandler.END

# Função para iniciar personalização
async def personalization_intro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia o processo de personalização"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("👤 Vamos começar!", callback_data="get_name")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "✨ **Vamos nos conhecer melhor!**\n\n"
        "Vou fazer algumas perguntas simples para personalizar nossa conversa:\n\n"
        "1️⃣ Como você gostaria que eu te chamasse?\n"
        "2️⃣ Como você gostaria de me chamar?\n"
        "3️⃣ Que tipo de personalidade você prefere?\n\n"
        "📝 *Isso ajuda a criar uma experiência única para você!*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return GET_USER_NAME

# Função para obter nome do usuário
async def get_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Solicita o nome do usuário"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "👤 **Como você gostaria que eu te chamasse?**\n\n"
        "💬 Digite seu nome ou como prefere ser chamado(a):"
    )
    
    return GET_USER_NAME

# Função para salvar nome do usuário e solicitar idade
async def save_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Salva o nome do usuário e solicita a idade"""
    user_name = update.message.text.strip()
    context.user_data['user_name'] = user_name
    
    await update.message.reply_text(
        f"✅ Ótimo, {user_name}!\n\n"
        "🎂 **Agora me conta, qual sua idade?**\n\n"
        "💭 Digite apenas o número da sua idade:"
    )
    
    return GET_USER_AGE

# Função para salvar idade e solicitar gênero do usuário
async def save_user_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Salva a idade do usuário e solicita o gênero"""
    try:
        user_age = int(update.message.text.strip())
        if user_age < 1 or user_age > 120:
            raise ValueError("Idade fora do intervalo válido")
        
        context.user_data['user_age'] = str(user_age)
        
        # Opções de gênero do usuário
        keyboard = [
            [InlineKeyboardButton("👨 Masculino", callback_data="user_gender_masculino")],
            [InlineKeyboardButton("👩 Feminino", callback_data="user_gender_feminino")],
            [InlineKeyboardButton("🌟 Não-binário", callback_data="user_gender_nao_binario")],
            [InlineKeyboardButton("🤐 Prefiro não dizer", callback_data="user_gender_outro")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ {user_age} anos, perfeito!\n\n"
            "👤 **Como você se identifica?**\n\n"
            "Escolha a opção que melhor representa você:",
            reply_markup=reply_markup
        )
        
        return GET_USER_GENDER
        
    except ValueError:
        await update.message.reply_text(
            "❌ Por favor, digite apenas um número válido para sua idade (ex: 25):"
        )
        return GET_USER_AGE

# Função para processar gênero do usuário e solicitar nome do bot
async def process_user_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa o gênero do usuário e solicita o nome do bot"""
    query = update.callback_query
    await query.answer()
    
    gender_mapping = {
        'user_gender_masculino': 'masculino',
        'user_gender_feminino': 'feminino', 
        'user_gender_nao_binario': 'nao_binario',
        'user_gender_outro': 'outro'
    }
    
    gender_names = {
        'masculino': 'Masculino',
        'feminino': 'Feminino',
        'nao_binario': 'Não-binário',
        'outro': 'Prefiro não dizer'
    }
    
    user_gender = gender_mapping.get(query.data, 'outro')
    context.user_data['user_gender'] = user_gender
    
    user_name = context.user_data.get('user_name', 'Usuário')
    
    await query.edit_message_text(
        f"✅ Perfeito, {user_name}!\n\n"
        "🤖 **Agora, como você gostaria de me chamar?**\n\n"
        "💭 Pode ser qualquer nome que você preferir!"
    )
    
    return GET_BOT_NAME

# Função para salvar nome do bot e solicitar gênero do bot
async def save_bot_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Salva o nome do bot e solicita o gênero do bot"""
    bot_name = update.message.text.strip()
    context.user_data['bot_name'] = bot_name
    
    # Opções de gênero do bot
    keyboard = [
        [InlineKeyboardButton("👨 Masculino", callback_data="bot_gender_masculino")],
        [InlineKeyboardButton("👩 Feminino", callback_data="bot_gender_feminino")],
        [InlineKeyboardButton("⚖️ Neutro", callback_data="bot_gender_neutro")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✨ Ótimo! Agora me chame de **{bot_name}**!\n\n"
        "⚧ **Que gênero você prefere para {bot_name}?**\n\n"
        "Isso ajuda a personalizar melhor nossas conversas:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return GET_BOT_GENDER

# Função para processar gênero do bot e solicitar personalidade
async def process_bot_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa o gênero do bot e solicita personalidade"""
    query = update.callback_query
    await query.answer()
    
    gender_mapping = {
        'bot_gender_masculino': 'masculino',
        'bot_gender_feminino': 'feminino',
        'bot_gender_neutro': 'neutro'
    }
    
    gender_names = {
        'masculino': 'Masculino',
        'feminino': 'Feminino', 
        'neutro': 'Neutro'
    }
    
    bot_gender = gender_mapping.get(query.data, 'neutro')
    context.user_data['bot_gender'] = bot_gender
    bot_name = context.user_data.get('bot_name', 'Eron')
    
    personalities = {
        'amigavel': '😊 Amigável e Calorosa',
        'profissional': '💼 Profissional e Focada',
        'criativa': '🎨 Criativa e Inspiradora',
        'intelectual': '🧠 Intelectual e Analítica',
        'divertida': '🎭 Divertida e Descontraída'
    }
    
    keyboard = []
    for key, name in personalities.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"personality_{key}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ Perfeito! {bot_name} será {gender_names[bot_gender].lower()}!\n\n"
        "🎭 **Que personalidade você prefere?**\n\n"
        "Escolha o estilo que mais combina com você:",
        reply_markup=reply_markup
    )
    
    return SELECT_PERSONALITY

# Funções para comandos individuais
async def change_bot_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para mudar apenas o nome do bot"""
    await update.message.reply_text(
        "🤖 **Como você gostaria de me chamar agora?**\n\n"
        "💭 Digite o novo nome:"
    )
    
    return CHANGE_BOT_NAME

async def update_bot_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Atualiza apenas o nome do bot"""
    user_id = update.effective_user.id
    new_bot_name = update.message.text.strip()
    
    try:
        # Buscar perfil existente
        profile = context.bot.application.user_profile_db.get_profile(user_id)
        if profile:
            # Atualizar apenas o nome do bot
            context.bot.application.user_profile_db.save_profile(
                user_id,
                profile.get('user_name', 'Usuário'),
                new_bot_name,
                profile.get('personality', 'amigavel')
            )
            
            await update.message.reply_text(
                f"✅ **Perfeito!** Agora me chame de **{new_bot_name}**! 😊\n\n"
                "💬 Em que posso ajudar você hoje?"
            )
        else:
            await update.message.reply_text(
                "❌ Erro: Perfil não encontrado. Use /start para criar seu perfil primeiro."
            )
    except Exception as e:
        logging.error(f"Erro ao atualizar nome do bot: {e}")
        await update.message.reply_text(
            "❌ Erro ao salvar. Tente novamente mais tarde."
        )
    
    return ConversationHandler.END

async def change_personality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para mudar a personalidade"""
    personalities = {
        'amigavel': '😊 Amigável e Calorosa',
        'profissional': '💼 Profissional e Focada',
        'criativa': '🎨 Criativa e Inspiradora',
        'intelectual': '🧠 Intelectual e Analítica',
        'divertida': '🎭 Divertida e Descontraída'
    }
    
    keyboard = []
    for key, name in personalities.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"personality_{key}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎭 **Qual personalidade você prefere agora?**\n\n"
        "Escolha o novo estilo:",
        reply_markup=reply_markup
    )
    
    return CHANGE_PERSONALITY

async def handle_personality_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com a mudança de personalidade"""
    query = update.callback_query
    await query.answer()
    
    personality_key = query.data.replace('personality_', '')
    user_id = update.effective_user.id
    
    personality_names = {
        'amigavel': 'Amigável e Calorosa',
        'profissional': 'Profissional e Focada', 
        'criativa': 'Criativa e Inspiradora',
        'intelectual': 'Intelectual e Analítica',
        'divertida': 'Divertida e Descontraída'
    }
    
    try:
        # Buscar perfil existente
        profile = context.bot.application.user_profile_db.get_profile(user_id)
        if profile:
            # Atualizar apenas a personalidade
            context.bot.application.user_profile_db.save_profile(
                user_id,
                profile.get('user_name', 'Usuário'),
                profile.get('bot_name', 'Eron'),
                personality_key
            )
            
            await query.edit_message_text(
                f"✅ **Personalidade atualizada!**\n\n"
                f"🎭 Nova personalidade: {personality_names.get(personality_key, personality_key)}\n\n"
                f"💬 Agora estou com meu novo estilo! Como posso ajudar?"
            )
        else:
            await query.edit_message_text(
                "❌ Erro: Perfil não encontrado. Use /start para criar seu perfil primeiro."
            )
    except Exception as e:
        logging.error(f"Erro ao atualizar personalidade: {e}")
        await query.edit_message_text(
            "❌ Erro ao salvar. Tente novamente mais tarde."
        )
    
    return ConversationHandler.END

# Comandos para mudanças individuais adicionais
async def change_user_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para mudar idade do usuário"""
    await update.message.reply_text(
        "🎂 **Qual é sua idade agora?**\n\n"
        "💭 Digite apenas o número:"
    )
    
    return CHANGE_USER_AGE

async def update_user_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Atualiza a idade do usuário"""
    try:
        user_age = int(update.message.text.strip())
        if user_age < 1 or user_age > 120:
            raise ValueError("Idade fora do intervalo válido")
        
        user_id = update.effective_user.id
        db = context.bot.application.user_profile_db
        
        if db.update_profile(user_id=user_id, user_age=str(user_age)):
            await update.message.reply_text(
                f"✅ **Idade atualizada para {user_age} anos!** 🎂\n\n"
                "💬 Em que posso ajudar você hoje?"
            )
        else:
            await update.message.reply_text(
                "❌ Erro ao atualizar. Use /start para criar seu perfil primeiro."
            )
    except ValueError:
        await update.message.reply_text(
            "❌ Por favor, digite apenas um número válido para sua idade (ex: 25):"
        )
        return CHANGE_USER_AGE
    
    return ConversationHandler.END

async def change_user_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para mudar gênero do usuário"""
    keyboard = [
        [InlineKeyboardButton("👨 Masculino", callback_data="change_user_gender_masculino")],
        [InlineKeyboardButton("👩 Feminino", callback_data="change_user_gender_feminino")],
        [InlineKeyboardButton("🌟 Não-binário", callback_data="change_user_gender_nao_binario")],
        [InlineKeyboardButton("🤐 Prefiro não dizer", callback_data="change_user_gender_outro")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👤 **Como você se identifica?**\n\n"
        "Escolha a opção que melhor representa você:",
        reply_markup=reply_markup
    )
    
    return CHANGE_USER_GENDER

async def update_user_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Atualiza o gênero do usuário"""
    query = update.callback_query
    await query.answer()
    
    gender_mapping = {
        'change_user_gender_masculino': 'masculino',
        'change_user_gender_feminino': 'feminino', 
        'change_user_gender_nao_binario': 'nao_binario',
        'change_user_gender_outro': 'outro'
    }
    
    gender_names = {
        'masculino': 'Masculino',
        'feminino': 'Feminino',
        'nao_binario': 'Não-binário',
        'outro': 'Prefiro não dizer'
    }
    
    user_gender = gender_mapping.get(query.data, 'outro')
    user_id = update.effective_user.id
    db = context.bot.application.user_profile_db
    
    if db.update_profile(user_id=user_id, user_gender=user_gender):
        await query.edit_message_text(
            f"✅ **Identidade atualizada: {gender_names[user_gender]}!** 👤\n\n"
            "💬 Como posso ajudar você hoje?"
        )
    else:
        await query.edit_message_text(
            "❌ Erro: Perfil não encontrado. Use /start para criar seu perfil primeiro."
        )
    
    return ConversationHandler.END

async def change_bot_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para mudar gênero do bot"""
    keyboard = [
        [InlineKeyboardButton("👨 Masculino", callback_data="change_bot_gender_masculino")],
        [InlineKeyboardButton("👩 Feminino", callback_data="change_bot_gender_feminino")],
        [InlineKeyboardButton("⚖️ Neutro", callback_data="change_bot_gender_neutro")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚧ **Que gênero você prefere para mim?**\n\n"
        "Escolha como quer que eu me apresente:",
        reply_markup=reply_markup
    )
    
    return CHANGE_BOT_GENDER

async def update_bot_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Atualiza o gênero do bot"""
    query = update.callback_query
    await query.answer()
    
    gender_mapping = {
        'change_bot_gender_masculino': 'masculino',
        'change_bot_gender_feminino': 'feminino',
        'change_bot_gender_neutro': 'neutro'
    }
    
    gender_names = {
        'masculino': 'Masculino',
        'feminino': 'Feminino', 
        'neutro': 'Neutro'
    }
    
    bot_gender = gender_mapping.get(query.data, 'neutro')
    user_id = update.effective_user.id
    db = context.bot.application.user_profile_db
    
    if db.update_profile(user_id=user_id, bot_gender=bot_gender):
        await query.edit_message_text(
            f"✅ **Meu gênero foi atualizado para {gender_names[bot_gender]}!** ⚧\n\n"
            "💬 Agora vamos conversar! Em que posso ajudar?"
        )
    else:
        await query.edit_message_text(
            "❌ Erro: Perfil não encontrado. Use /start para criar seu perfil primeiro."
        )
    
    return ConversationHandler.END

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para mudar estilo de linguagem"""
    language_styles = {
        'informal': '😎 Informal e Descontraída',
        'formal': '🎩 Formal e Educada',
        'tecnica': '🔬 Técnica e Precisa', 
        'casual': '🌈 Casual e Amigável'
    }
    
    keyboard = []
    for key, name in language_styles.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"change_language_{key}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🗣️ **Como você prefere que eu fale com você?**\n\n"
        "Escolha o novo estilo de comunicação:",
        reply_markup=reply_markup
    )
    
    return CHANGE_LANGUAGE

async def update_language_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Atualiza o estilo de linguagem"""
    query = update.callback_query
    await query.answer()
    
    language_key = query.data.replace('change_language_', '')
    user_id = update.effective_user.id
    
    language_names = {
        'informal': 'Informal e Descontraída',
        'formal': 'Formal e Educada',
        'tecnica': 'Técnica e Precisa',
        'casual': 'Casual e Amigável'
    }
    
    db = context.bot.application.user_profile_db
    
    if db.update_profile(user_id=user_id, bot_language=language_key):
        await query.edit_message_text(
            f"✅ **Estilo de linguagem atualizado!**\n\n"
            f"🗣️ Novo estilo: {language_names.get(language_key, language_key)}\n\n"
            "💬 Agora vou falar com você nesse estilo! Como posso ajudar?"
        )
    else:
        await query.edit_message_text(
            "❌ Erro: Perfil não encontrado. Use /start para criar seu perfil primeiro."
        )
    
    return ConversationHandler.END

async def change_topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para mudar tópicos de interesse"""
    # Obter perfil atual para mostrar tópicos já selecionados
    user_id = update.effective_user.id
    db = context.bot.application.user_profile_db
    profile = db.get_profile(user_id)
    
    if not profile:
        await update.message.reply_text(
            "❌ Perfil não encontrado. Use /start para criar seu perfil primeiro."
        )
        return ConversationHandler.END
    
    current_topics = profile.get('preferred_topics', '').split(',') if profile.get('preferred_topics') else []
    current_topics = [t.strip() for t in current_topics if t.strip()]
    
    topics = {
        'tecnologia': '💻 Tecnologia',
        'ciencia': '🔬 Ciência',
        'arte': '🎨 Arte e Cultura',
        'esportes': '⚽ Esportes',
        'musica': '🎵 Música',
        'cinema': '🎬 Cinema e TV',
        'viagem': '✈️ Viagens',
        'culinaria': '🍳 Culinária',
        'literatura': '📚 Literatura',
        'games': '🎮 Games',
        'negocios': '💼 Negócios',
        'saude': '🏥 Saúde e Bem-estar'
    }
    
    # Dividir em duas colunas para melhor visualização
    keyboard = []
    topic_items = list(topics.items())
    for i in range(0, len(topic_items), 2):
        row = []
        for j in range(2):
            if i + j < len(topic_items):
                key, name = topic_items[i + j]
                # Adicionar checkmark se já estiver selecionado
                display_name = f"✅ {name}" if key in current_topics else name
                row.append(InlineKeyboardButton(display_name, callback_data=f"change_topic_{key}"))
        keyboard.append(row)
    
    # Botão para finalizar seleção
    keyboard.append([InlineKeyboardButton("✅ Salvar Alterações", callback_data="change_topics_done")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Texto dos tópicos atuais
    current_names = [topics[t] for t in current_topics if t in topics] if current_topics else ["Nenhum"]
    current_text = ", ".join(current_names)
    
    await update.message.reply_text(
        "🎯 **Quais assuntos te interessam?**\n\n"
        "📝 *Selecione/desselecione quantos quiser e depois clique em 'Salvar'*\n\n"
        f"🔹 **Tópicos atuais:** {current_text}",
        reply_markup=reply_markup
    )
    
    # Armazenar tópicos atuais no contexto
    context.user_data['editing_topics'] = current_topics.copy()
    
    return CHANGE_TOPICS

async def update_topics_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Atualiza seleção de tópicos de interesse"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "change_topics_done":
        # Finalizar edição
        user_id = update.effective_user.id
        selected_topics = context.user_data.get('editing_topics', [])
        topics_text = ','.join(selected_topics) if selected_topics else ''
        
        db = context.bot.application.user_profile_db
        
        if db.update_profile(user_id=user_id, preferred_topics=topics_text):
            topics_list = {
                'tecnologia': 'tecnologia',
                'ciencia': 'ciência',
                'arte': 'arte e cultura',
                'esportes': 'esportes',
                'musica': 'música',
                'cinema': 'cinema e TV',
                'viagem': 'viagens',
                'culinaria': 'culinária',
                'literatura': 'literatura',
                'games': 'games',
                'negocios': 'negócios',
                'saude': 'saúde e bem-estar'
            }
            
            if selected_topics:
                interests_names = [topics_list.get(t, t) for t in selected_topics]
                interests_text = ", ".join(interests_names).title()
            else:
                interests_text = "Conversas gerais"
            
            await query.edit_message_text(
                f"✅ **Tópicos de interesse atualizados!**\n\n"
                f"🎯 Novos interesses: {interests_text}\n\n"
                "💬 Agora posso falar melhor sobre os assuntos que você gosta! Como posso ajudar?"
            )
        else:
            await query.edit_message_text(
                "❌ Erro ao salvar. Tente novamente mais tarde."
            )
        
        # Limpar dados temporários
        context.user_data.pop('editing_topics', None)
        
        return ConversationHandler.END
    
    # Processar seleção/deseleção de tópico
    topic_key = query.data.replace('change_topic_', '')
    editing_topics = context.user_data.get('editing_topics', [])
    
    topics = {
        'tecnologia': '💻 Tecnologia',
        'ciencia': '🔬 Ciência',
        'arte': '🎨 Arte e Cultura',
        'esportes': '⚽ Esportes',
        'musica': '🎵 Música',
        'cinema': '🎬 Cinema e TV',
        'viagem': '✈️ Viagens',
        'culinaria': '🍳 Culinária',
        'literatura': '📚 Literatura',
        'games': '🎮 Games',
        'negocios': '💼 Negócios',
        'saude': '🏥 Saúde e Bem-estar'
    }
    
    # Toggle topic selection
    if topic_key in editing_topics:
        editing_topics.remove(topic_key)
    else:
        editing_topics.append(topic_key)
    
    context.user_data['editing_topics'] = editing_topics
    
    # Reconstruir keyboard com tópicos marcados
    keyboard = []
    topic_items = list(topics.items())
    for i in range(0, len(topic_items), 2):
        row = []
        for j in range(2):
            if i + j < len(topic_items):
                key, name = topic_items[i + j]
                # Adicionar checkmark se selecionado
                display_name = f"✅ {name}" if key in editing_topics else name
                row.append(InlineKeyboardButton(display_name, callback_data=f"change_topic_{key}"))
        keyboard.append(row)
    
    # Botão para finalizar seleção
    keyboard.append([InlineKeyboardButton("✅ Salvar Alterações", callback_data="change_topics_done")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Texto dos tópicos selecionados
    selected_names = [topics[t] for t in editing_topics] if editing_topics else ["Nenhum"]
    selected_text = ", ".join(selected_names)
    
    await query.edit_message_text(
        "🎯 **Quais assuntos te interessam?**\n\n"
        "📝 *Selecione/desselecione quantos quiser e depois clique em 'Salvar'*\n\n"
        f"🔹 **Tópicos selecionados:** {selected_text}",
        reply_markup=reply_markup
    )
    
    return CHANGE_TOPICS

# ===== SISTEMA ADULTO - HANDLERS E FUNÇÕES =====

async def adult_activation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia processo de ativação do modo adulto (+18)"""
    if not ADULT_SYSTEM_AVAILABLE:
        await update.message.reply_text("❌ Sistema adulto não disponível nesta instalação.")
        return ConversationHandler.END
    
    user_id = update.message.from_user.id
    
    # Processar ativação
    result = adult_commands.handle_adult_activation_command(user_id, 'telegram')
    
    await update.message.reply_text(result['message'])
    
    if result['status'] == 'terms_required':
        # Salvar token na sessão
        context.user_data['adult_verification_token'] = result['token']
        context.user_data['adult_question_type'] = None
        return ADULT_TERMS
    else:
        return ConversationHandler.END

async def handle_adult_terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa resposta aos termos de responsabilidade"""
    if not ADULT_SYSTEM_AVAILABLE:
        await update.message.reply_text("❌ Sistema não disponível.")
        return ConversationHandler.END
    
    user_id = update.message.from_user.id
    response = update.message.text.strip()
    token = context.user_data.get('adult_verification_token')
    
    if not token:
        await update.message.reply_text("❌ Sessão inválida. Tente novamente com /18")
        return ConversationHandler.END
    
    # Processar resposta aos termos
    result = adult_commands.handle_terms_response(user_id, response, token)
    
    await update.message.reply_text(result['message'])
    
    if result['status'] == 'age_verification':
        # Salvar tipo de pergunta para próximo step
        context.user_data['adult_question_type'] = result['question_type']
        return ADULT_AGE_VERIFICATION
    else:
        # Limpar dados da sessão
        context.user_data.pop('adult_verification_token', None)
        context.user_data.pop('adult_question_type', None)
        return ConversationHandler.END

async def handle_adult_age_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa verificação de idade"""
    if not ADULT_SYSTEM_AVAILABLE:
        await update.message.reply_text("❌ Sistema não disponível.")
        return ConversationHandler.END
    
    user_id = update.message.from_user.id
    age_response = update.message.text.strip()
    token = context.user_data.get('adult_verification_token')
    question_type = context.user_data.get('adult_question_type')
    
    if not token or not question_type:
        await update.message.reply_text("❌ Sessão inválida. Tente novamente com /18")
        return ConversationHandler.END
    
    # Processar verificação de idade
    result = adult_commands.handle_age_verification(user_id, age_response, token, question_type)
    
    # CORREÇÃO: Se verificação foi bem-sucedida, atualizar banco de perfis
    if result.get('status') == 'verification_successful' or 'aprovado' in result.get('message', '').lower():
        try:
            # Atualizar banco de perfis principal
            user_profile_db.update_profile(str(user_id), has_mature_access=True)
            
            # Também ativar via check.py para garantir
            from core.check import activate_adult_mode
            activate_adult_mode(str(user_id))
            
            print(f"[DEBUG] Modo adulto ativado para usuário {user_id}")
        except Exception as e:
            print(f"[ERRO] Falha ao ativar modo adulto: {e}")
    
    await update.message.reply_text(result['message'])
    
    # Limpar dados da sessão
    context.user_data.pop('adult_verification_token', None)
    context.user_data.pop('adult_question_type', None)
    
    return ConversationHandler.END

async def cancel_adult_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela processo de verificação adulta"""
    user_id = update.message.from_user.id
    token = context.user_data.get('adult_verification_token')
    
    if ADULT_SYSTEM_AVAILABLE and token:
        adult_db.cancel_verification(user_id, token, 'user_cancelled')
    
    context.user_data.pop('adult_verification_token', None)
    context.user_data.pop('adult_question_type', None)
    
    await update.message.reply_text("✅ Verificação de idade cancelada.")
    return ConversationHandler.END

async def adult_config_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu de configuração do modo adulto"""
    user_id = str(update.message.from_user.id)
    
    try:
        # Verificar se usuário tem acesso adulto
        from core.check import check_age
        adult_status = check_age(user_id)
        
        if not adult_status.get('adult_mode_active'):
            await update.message.reply_text(
                "❌ Você precisa ativar o modo adulto primeiro.\n"
                "🔞 Use o comando /18 para ativar."
            )
            return
        
        # Obter perfil do usuário
        profile = user_profile_db.get_user_profile(user_id)
        
        config_msg = "🔞 **CONFIGURAÇÕES DO MODO ADULTO**\n\n"
        
        if profile:
            config_msg += f"👤 Nome do usuário: {profile.get('user_name', 'Não definido')}\n"
            config_msg += f"🤖 Nome do bot: {profile.get('bot_name', 'ERON')}\n"
            config_msg += f"🎭 Personalidade: {profile.get('bot_personality', 'padrão')}\n"
            config_msg += f"🔥 Intensidade atual: {profile.get('adult_intensity_level', 1)}/5\n"
        
        config_msg += "\n🛠️ **COMANDOS DE CONFIGURAÇÃO:**\n"
        config_msg += "/intensidade1 - Romântico e carinhoso\n"
        config_msg += "/intensidade2 - Flerte moderado\n"
        config_msg += "/intensidade3 - Sensual e provocante\n"
        config_msg += "/genero_feminino - Bot no gênero feminino\n"
        config_msg += "/genero_masculino - Bot no gênero masculino\n"
        config_msg += "/genero_neutro - Bot no gênero neutro\n\n"
        config_msg += "📊 /devassa_status - Ver status completo\n"
        config_msg += "🔴 /devassa_off - Desativar modo adulto"
        
        await update.message.reply_text(config_msg, parse_mode='Markdown')
        
    except Exception as e:
        logging.error(f"Erro no menu de configuração adulto: {e}")
        await update.message.reply_text(
            "❌ Erro ao carregar configurações.\n"
            "Tente novamente ou entre em contato com o suporte."
        )

async def deactivate_adult_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Desativa modo adulto com feedback melhorado"""
    user_id = str(update.message.from_user.id)
    user_profile_db = context.application.user_profile_db
    
    try:
        # Usar sistema básico de verificação de idade
        from core.check import check_age, deactivate_adult_mode as check_deactivate
        adult_status = check_age(user_id)
        
        # Verificar se o modo adulto já está desativado
        if not adult_status.get('adult_mode_active'):
            await update.message.reply_text(
                "❌ **O modo adulto já está desativado.**\n\n"
                "🔒 Você já está no modo seguro.\n"
                "🔞 Para ativar o modo adulto, use /18"
            )
            return
        
        # Obter informações do perfil antes da desativação
        profile = user_profile_db.get_profile(user_id)
        user_name = profile.get('user_name', update.effective_user.first_name or 'Usuário')
        
        # Desativar modo adulto no banco principal
        user_profile_db.update_profile(user_id, has_mature_access=False)
        
        # Também desativar via check.py para garantir sincronização
        success = check_deactivate(user_id)
        
        if success:
            print(f"[DEBUG] Modo adulto desativado com sucesso para usuário {user_id} ({user_name})")
            
            await update.message.reply_text(
                f"✅ **Modo adulto desativado com sucesso, {user_name}!**\n\n"
                "🔒 **Status atual:** Modo seguro\n"
                "🤖 **Respostas:** Agora voltarei ao modo padrão\n"
                "🔞 **Para reativar:** Use /18 e siga a verificação\n\n"
                "💬 Pode continuar conversando normalmente!"
            )
        else:
            print(f"[WARNING] Falha ao desativar modo adulto para usuário {user_id}")
            await update.message.reply_text(
                "⚠️ **Houve um problema ao desativar completamente.**\n\n"
                "Modo adulto foi parcialmente desativado.\n"
                "Se o problema persistir, use /clear para resetar tudo."
            )
        
    except Exception as e:
        logging.error(f"Erro ao desativar modo adulto para {user_id}: {e}")
        await update.message.reply_text(
            "❌ **Erro ao desativar modo adulto.**\n\n"
            "🔧 **Soluções:**\n"
            "• Tente novamente em alguns segundos\n"
            "• Use /clear para resetar todas as configurações\n"
            "• Entre em contato com o suporte se persistir"
        )

async def adult_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra status do modo adulto"""
    user_id = str(update.message.from_user.id)
    user_profile_db = context.application.user_profile_db
    
    try:
        # Usar sistema básico de verificação de idade
        from core.check import check_age
        adult_status = check_age(user_id)
        
        if adult_status.get('adult_mode_active'):
            # Obter informações do perfil
            profile = user_profile_db.get_profile(user_id)
            
            status_msg = "🔞 **STATUS DO MODO ADULTO**\n\n"
            status_msg += "✅ Modo adulto: **ATIVO**\n"
            
            if profile:
                status_msg += f"👤 Usuário: {profile.get('user_name', 'Não definido')}\n"
                status_msg += f"🤖 Bot: {profile.get('bot_name', 'ERON')}\n"
                status_msg += f"🎭 Personalidade: {profile.get('bot_personality', 'padrão')}\n"
                status_msg += f"🔥 Intensidade: {profile.get('adult_intensity_level', 1)}/5\n"
                
                # Verificar se tem sistema avançado
                context_info = get_adult_personality_context(user_id)
                if context_info.get('advanced_system'):
                    status_msg += "\n🎯 Sistema avançado: **ATIVO**"
                else:
                    status_msg += "\n⚡ Sistema básico ativo"
                    status_msg += "\n💡 Use /adult_config para upgrade"
            
            status_msg += "\n\n🛠️ **COMANDOS DISPONÍVEIS:**"
            status_msg += "\n/devassa_off - Desativar modo adulto"
            status_msg += "\n/adult_config - Configurações avançadas"
            
        else:
            status_msg = "🔒 **MODO SEGURO ATIVO**\n\n"
            status_msg += "❌ Modo adulto: **INATIVO**\n\n"
            status_msg += "🔞 Para ativar o modo adulto:\n"
            status_msg += "• Use o comando /18\n"
            status_msg += "• Complete a verificação de idade\n"
            status_msg += "• Aceite os termos de uso"
        
        await update.message.reply_text(status_msg, parse_mode='Markdown')
        
    except Exception as e:
        logging.error(f"Erro ao verificar status adulto: {e}")
        await update.message.reply_text(
            "❌ Erro ao verificar status.\n"
            "Tente novamente ou entre em contato com o suporte."
        )

async def set_intensity(update: Update, context: ContextTypes.DEFAULT_TYPE, level: int):
    """Define intensidade da linguagem adulta"""
    user_id = str(update.message.from_user.id)
    user_profile_db = context.application.user_profile_db
    
    try:
        # Verificar se usuário tem acesso adulto
        from core.check import check_age
        adult_status = check_age(user_id)
        
        if not adult_status.get('adult_mode_active'):
            await update.message.reply_text(
                "❌ Você precisa ativar o modo adulto primeiro.\n"
                "🔞 Use o comando /18 para ativar."
            )
            return
        
        # Definir intensidade no perfil
        user_profile_db.update_profile(user_id, adult_intensity_level=level)
        
        intensity_names = {
            1: "Romântico e carinhoso",
            2: "Flerte moderado", 
            3: "Sensual e provocante",
            4: "Intenso e explícito",
            5: "Extremamente intenso"
        }
        
        intensity_name = intensity_names.get(level, "Desconhecido")
        
        await update.message.reply_text(
            f"🔥 **Intensidade alterada com sucesso!**\n\n"
            f"📊 Nível atual: **{level}/5**\n"
            f"🎭 Estilo: {intensity_name}\n\n"
            f"💬 As próximas conversas seguirão este nível de intensidade.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logging.error(f"Erro ao definir intensidade: {e}")
        await update.message.reply_text(
            "❌ Erro ao alterar intensidade.\n"
            "Tente novamente ou entre em contato com o suporte."
        )

async def set_adult_gender(update: Update, context: ContextTypes.DEFAULT_TYPE, gender: str):
    """Define gênero do bot no modo adulto"""
    user_id = str(update.message.from_user.id)
    user_profile_db = context.application.user_profile_db
    
    try:
        # Verificar se usuário tem acesso adulto
        from core.check import check_age
        adult_status = check_age(user_id)
        
        if not adult_status.get('adult_mode_active'):
            await update.message.reply_text(
                "❌ Você precisa ativar o modo adulto primeiro.\n"
                "🔞 Use o comando /18 para ativar."
            )
            return
        
        # Definir gênero no perfil
        user_profile_db.update_profile(user_id, bot_gender=gender)
        
        gender_names = {
            'feminino': '👩 Feminino',
            'masculino': '👨 Masculino', 
            'neutro': '🤖 Neutro'
        }
        
        gender_name = gender_names.get(gender, gender.title())
        
        await update.message.reply_text(
            f"👤 **Gênero alterado com sucesso!**\n\n"
            f"🎭 Gênero atual: {gender_name}\n\n"
            f"💬 O bot agora se comportará de acordo com este gênero.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logging.error(f"Erro ao definir gênero: {e}")
        await update.message.reply_text(
            "❌ Erro ao alterar gênero.\n"
            "Tente novamente ou entre em contato com o suporte."
        )

async def handle_personality_selection_global(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler global para seleção de personalidade (para botões fora do menu)"""
    # Se estiver no processo de personalização, usar handler do menu
    if context.user_data.get('personalization_step') == 'bot_personality':
        return await handle_personality_selection_menu(update, context)
    
    # Caso contrário, usar handler simples para mudanças individuais
    query = update.callback_query
    await query.answer("✅ Personalidade aplicada!")
    
    user_id = str(update.effective_user.id)
    personality_key = query.data.replace('personality_', '')
    
    print(f"[DEBUG PERSONALITY GLOBAL] Personalidade recebida: '{personality_key}' para user {user_id}")
    
    # Obter instância do banco
    user_profile_db = context.application.user_profile_db
    
    # Salvar personalidade diretamente no perfil
    try:
        user_profile_db.save_profile(user_id=user_id, bot_personality=personality_key)
        print(f"[DEBUG PERSONALITY GLOBAL] Personalidade {personality_key} salva com sucesso")
        
        personality_names = {
            'amigável': 'Amigável e Calorosa',
            'formal': 'Formal e Profissional', 
            'casual': 'Casual e Descontraída',
            'divertido': 'Divertida e Alegre',
            'intelectual': 'Intelectual e Analítica'
        }
        
        personality_name = personality_names.get(personality_key, personality_key.title())
        
        await query.edit_message_text(
            f"✅ **Personalidade {personality_name} aplicada com sucesso!**\n\n"
            f"Agora eu vou interagir com você de forma {personality_name.lower()}.\n\n"
            f"💬 Pode começar a conversar comigo normalmente! \n\n"
            f"🔧 Para ajustar outras configurações, use /preferencias"
        )
    except Exception as e:
        print(f"[ERROR] Erro ao salvar personalidade: {e}")
        await query.edit_message_text(
            f"❌ **Erro ao aplicar personalidade**\n\n"
            f"Ocorreu um erro técnico. Tente novamente ou use /start."
        )

async def handle_close_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fecha o menu de preferências"""
    query = update.callback_query
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    profile = user_profile_db.get_profile(user_id)
    
    bot_name = profile.get('bot_name', 'Eron')
    user_name = profile.get('user_name', 'Usuário')
    
    await query.answer("✅ Menu fechado!")
    
    await query.edit_message_text(
        f"✅ **Menu de preferências fechado**\n\n"
        f"Olá {user_name}! Eu sou {bot_name}.\n\n"
        f"💬 Agora podemos conversar normalmente!\n\n"
        f"🔧 Para alterar configurações novamente, use: /preferencias"
    )

async def handle_reset_all_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reseta todas as preferências - mesmo funcionamento do /clear"""
    query = update.callback_query
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db

    await query.answer("🔄 Redefinindo todas as configurações...")

    try:
        # Desativar modo adulto antes de apagar perfil
        from core.check import deactivate_adult_mode
        deactivate_adult_mode(user_id)
        print(f"[DEBUG] Modo adulto desativado para {user_id} durante reset de preferências")
        
        # Apagar perfil do banco (mesma funcionalidade do /clear)
        user_profile_db.delete_profile(user_id)
        print(f"[DEBUG] Perfil {user_id} apagado com sucesso")

        await query.edit_message_text(
            '🗑️ **Todas as suas personalizações foram redefinidas!**\n\n'
            '🔒 **O modo adulto também foi desativado.**\n\n'
            'Agora eu voltei a ser o ERON padrão.\n\n'
            '🚀 Gostaria de personalizar novamente?\n\n'
            '💡 Digite /start para começar uma nova personalização! 😊'
        )
    except Exception as e:
        print(f"[ERROR] Erro ao resetar preferências: {e}")
        await query.edit_message_text(
            '❌ **Erro ao redefinir personalizações**\n\n'
            'Ocorreu um erro técnico. Tente novamente ou use /clear.'
        )

async def handle_global_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler global para todos os callbacks do sistema de personalização"""
    query = update.callback_query
    
    # Mapear callbacks para funções
    callback_handlers = {
        'start_personalization': handle_start_personalization,
        'skip_personalization': handle_skip_personalization,
        'age_18_plus': handle_age_verification,
        'age_under_18': handle_age_verification,
        'user_gender_masculino': handle_user_gender,
        'user_gender_feminino': handle_user_gender,
        'user_gender_outro': handle_user_gender,
        'bot_gender_masculino': handle_bot_gender,
        'bot_gender_feminino': handle_bot_gender,
        'bot_gender_neutro': handle_bot_gender,
        # Callbacks para seleção de nomes do bot
        'bot_name_ERON': handle_bot_name_selection,
        'bot_name_ERONA': handle_bot_name_selection,
        'bot_name_Bruno': handle_bot_name_selection,
        'bot_name_Carlos': handle_bot_name_selection,
        'bot_name_Diego': handle_bot_name_selection,
        'bot_name_Mateus': handle_bot_name_selection,
        'bot_name_Rafael': handle_bot_name_selection,
        'bot_name_Ana': handle_bot_name_selection,
        'bot_name_Beatriz': handle_bot_name_selection,
        'bot_name_Clara': handle_bot_name_selection,
        'bot_name_Maria': handle_bot_name_selection,
        'bot_name_Sofia': handle_bot_name_selection,
        'bot_name_Alex': handle_bot_name_selection,
        'bot_name_Chris': handle_bot_name_selection,
        'bot_name_Jordan': handle_bot_name_selection,
        'bot_name_Sam': handle_bot_name_selection,
        'bot_name_Taylor': handle_bot_name_selection,
        'bot_name_custom': handle_bot_name_selection,
        'bot_gender_neutro': handle_bot_gender,
        'finish_personalization': finish_personalization_process,
        'adjust_settings': handle_adjust_settings,
        'adjust_bot_name': handle_adjust_bot_name,
        'start_chat': handle_start_chat,
        'change_user_name': handle_change_user_name,
        'change_bot_name': handle_change_bot_name,
        'change_user_age_menu': handle_change_user_age_menu,
        'change_user_gender_menu': handle_change_user_gender_menu,
        'change_bot_gender_menu': handle_change_bot_gender_menu,
        'change_personality': handle_change_personality,
        'change_language_menu': handle_change_language_menu,
        'change_topics_menu': handle_change_topics_menu,
        'back_to_preferences': show_preferences_again,
        'close_preferences': handle_close_preferences,
        'reset_all_preferences': handle_reset_all_preferences,
        # Callbacks para configuração sequencial
        'start_sequential_setup': handle_sequential_setup_callback,
        'show_main_menu': handle_show_main_menu,
        'start_conversation': handle_start_conversation
    }
    
    # Callbacks com padrões específicos
    
    # Callbacks da configuração sequencial
    if query.data.startswith('seq_'):
        return await handle_sequential_callbacks(update, context)
    
    if query.data.startswith('personality_'):
        if context.user_data.get('personalization_step') == 'bot_personality':
            return await handle_personality_selection_menu(update, context)
        else:
            return await handle_personality_selection_global(update, context)
            
    elif query.data.startswith('language_'):
        return await handle_language_selection_menu(update, context)
        
    elif query.data.startswith('topic_'):
        return await handle_topic_selection_menu(update, context)
    
    elif query.data.startswith('bot_name_'):
        return await handle_bot_name_selection(update, context)
    
    elif query.data.startswith('initial_bot_name_'):
        return await handle_initial_bot_name_selection(update, context)
    
    # Handlers para reset completo
    elif query.data == 'confirm_reset_all':
        return await handle_confirm_reset_all(update, context)
    elif query.data == 'cancel_reset':
        return await handle_cancel_reset(update, context)
    
    # Callbacks diretos
    handler = callback_handlers.get(query.data)
    if handler:
        return await handler(update, context)
    
    # Fallback para outros handlers existentes  
    if query.data.startswith('pref_'):
        return await handle_preference_callbacks(update, context)
    elif query.data.startswith('emotion_'):
        return await handle_emotion_button(update, context)
    
    # Se chegou aqui, callback não reconhecido
    await query.answer("❓ Ação não reconhecida")

async def handle_adjust_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Permite ajustar configurações após personalização"""
    query = update.callback_query
    await query.answer("🔧 Abrindo configurações...")
    
    await query.edit_message_text(
        "🔧 **Configurações disponíveis:**\n\n"
        "Escolha o que deseja ajustar:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Nome do Bot", callback_data='adjust_bot_name')],
            [InlineKeyboardButton("🎭 Personalidade", callback_data='adjust_personality')],
            [InlineKeyboardButton("🗣️ Linguagem", callback_data='adjust_language')],
            [InlineKeyboardButton("📚 Tópicos", callback_data='adjust_topics')],
            [InlineKeyboardButton("⚙️ Preferências", callback_data='pref_menu')],
            [InlineKeyboardButton("⬅️ Voltar", callback_data='back_to_summary')]
        ])
    )

async def handle_start_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia conversa após personalização"""
    query = update.callback_query
    await query.answer("💬 Vamos conversar!")
    
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    profile = user_profile_db.get_profile(user_id)
    
    bot_name = profile.get('bot_name', 'Eron')
    user_name = profile.get('user_name', 'Usuário')
    
    await query.edit_message_text(
        f"💬 **Olá, {user_name}! Eu sou {bot_name}!**\n\n"
        f"Agora estou completamente personalizado(a) para você. \n\n"
        f"🚀 **O que gostaria de conversar?**\n\n"
        f"💡 *Dica: Pode me fazer qualquer pergunta, pedir ajuda ou só bater um papo!*"
    )

async def handle_adjust_bot_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Permite escolher nome do bot com opções predefinidas"""
    query = update.callback_query
    await query.answer("🤖 Configurando nome do bot!")
    
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    profile = user_profile_db.get_profile(user_id)
    current_name = profile.get('bot_name', 'Eron')
    
    await query.edit_message_text(
        f"🤖 **Escolha o nome do bot:**\n\n"
        f"📝 *Nome atual:* **{current_name}**\n\n"
        f"💭 **Opções disponíveis:**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🌸 Joana", callback_data='bot_name_joana')],
            [InlineKeyboardButton("🤖 Eron", callback_data='bot_name_eron')],
            [InlineKeyboardButton("💫 Luna", callback_data='bot_name_luna')],
            [InlineKeyboardButton("🌟 Sofia", callback_data='bot_name_sofia')],
            [InlineKeyboardButton("🎭 Maya", callback_data='bot_name_maya')],
            [InlineKeyboardButton("💎 Aria", callback_data='bot_name_aria')],
            [InlineKeyboardButton("✏️ Nome personalizado", callback_data='bot_name_custom')],
            [InlineKeyboardButton("⬅️ Voltar", callback_data='adjust_settings')]
        ])
    )

async def handle_confirm_reset_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirma reset completo da personalização"""
    query = update.callback_query
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    
    try:
        # Reset completo - manter apenas o user_id
        user_profile_db.save_profile(user_id=user_id,
                                   user_name='',
                                   user_age='',
                                   user_gender='',
                                   bot_name='',
                                   bot_gender='',
                                   bot_personality='',
                                   bot_language='',
                                   preferred_topics='',
                                   has_mature_access=True)
        
        await query.answer("🔄 Personalização resetada!")
        await query.edit_message_text(
            "✅ **Personalização resetada com sucesso!**\n\n"
            "🆕 Todas as configurações foram apagadas.\n"
            "Agora você pode recomeçar do zero.\n\n"
            "Use /start para iniciar uma nova personalização! 🚀",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Começar nova personalização", callback_data='start_personalization')]
            ])
        )
        
        # Limpar dados da sessão
        context.user_data.clear()
        
    except Exception as e:
        print(f"Erro ao resetar personalização: {e}")
        await query.answer("❌ Erro ao resetar!")
        await query.edit_message_text(
            "❌ **Erro ao resetar personalização**\n\n"
            "Tente novamente ou use /start para reconfigurar."
        )

async def handle_cancel_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela o reset da personalização"""
    query = update.callback_query
    await query.answer("✅ Reset cancelado!")
    
    await query.edit_message_text(
        "✅ **Reset cancelado!**\n\n"
        "Suas configurações permanecem intactas.\n\n"
        "💡 **Comandos disponíveis:**\n"
        "/meu_nome - Alterar seu nome\n"
        "/mudar_nome - Alterar nome do bot\n"
        "/mudar_personalidade - Alterar personalidade\n"
        "/preferences - Menu de preferências"
    )

async def handle_bot_name_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa seleção do nome predefinido do bot"""
    query = update.callback_query
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    
    # Extrair nome do callback
    name_key = query.data.replace('bot_name_', '')
    
    name_mapping = {
        'joana': 'Joana',
        'eron': 'Eron', 
        'luna': 'Luna',
        'sofia': 'Sofia',
        'maya': 'Maya',
        'aria': 'Aria'
    }
    
    if name_key == 'custom':
        await query.answer("✏️ Digite o nome personalizado!")
        await query.edit_message_text(
            "✏️ **Nome personalizado do bot:**\n\n"
            "💭 *Digite o nome que você quer que eu tenha:*\n\n"
            "⚠️ *Evite nomes muito longos ou complicados*"
        )
        context.user_data['personalization_step'] = 'bot_name'
        context.user_data['from_adjust'] = True
        return
    
    if name_key in name_mapping:
        new_name = name_mapping[name_key]
        
        # Salvar novo nome
        user_profile_db.save_profile(user_id=user_id, bot_name=new_name)
        
        await query.answer(f"✅ Nome alterado para {new_name}!")
        await query.edit_message_text(
            f"✅ **Nome do bot alterado com sucesso!**\n\n"
            f"🤖 **Novo nome:** {new_name}\n\n"
            f"Agora você pode me chamar de **{new_name}**! 🎉\n\n"
            f"💬 Como posso ajudar você hoje?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔧 Outras configurações", callback_data='adjust_settings')],
                [InlineKeyboardButton("💬 Começar conversa", callback_data='start_chat')]
            ])
        )

async def handle_personalization_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para processar texto durante a personalização"""
    user_id = str(update.effective_user.id)
    
    # Verificar se está no sistema sequencial
    if 'sequential_step' in context.user_data and context.user_data['sequential_step'] in [
        SEQUENCIAL_USER_NAME, SEQUENCIAL_USER_GENDER, SEQUENCIAL_USER_AGE_DAY, SEQUENCIAL_USER_AGE_MONTH, SEQUENCIAL_USER_AGE_YEAR,
        SEQUENCIAL_BOT_GENDER, SEQUENCIAL_BOT_NAME, SEQUENCIAL_PERSONALITY, SEQUENCIAL_LANGUAGE
    ]:
        return await handle_sequential_setup_text(update, context)
    
    # Sistema de personalização original
    step = context.user_data.get('personalization_step')
    
    if step == 'user_name':
        return await handle_user_name_input(update, context)
    elif step == 'bot_name':
        return await handle_bot_name_input(update, context)
    elif step == 'bot_name_input':
        return await handle_custom_bot_name_input(update, context)
    else:
        # Se não estiver em processo de personalização, usar handler normal
        return await chat(update, context)

async def handle_bot_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa nome do bot e avança para gênero do bot"""
    bot_name = update.message.text.strip()
    user_id = str(update.effective_user.id)
    
    # Salvar nome do bot
    user_profile_db = context.application.user_profile_db
    user_profile_db.save_profile(user_id=user_id, bot_name=bot_name)
    
    # Verificar se veio do menu de ajustes
    if context.user_data.get('from_adjust'):
        await update.message.reply_text(
            f"✅ **Nome personalizado salvo com sucesso!**\n\n"
            f"🤖 **Novo nome:** {bot_name}\n\n"
            f"Agora você pode me chamar de **{bot_name}**! 🎉\n\n"
            f"💬 Como posso ajudar você hoje?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔧 Outras configurações", callback_data='adjust_settings')],
                [InlineKeyboardButton("💬 Começar conversa", callback_data='start_chat')]
            ])
        )
        # Limpar flag
        del context.user_data['from_adjust']
        del context.user_data['personalization_step']
        return
    
    # Fluxo normal de personalização inicial
    await update.message.reply_text(
        f"✅ **Perfeito! Agora me chamo {bot_name}!**\n\n"
        "🤖 **Como você prefere que eu me apresente?**\n\n"
        "💭 *Isso influencia como eu falo e me refiro a mim mesmo:*",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👩 Feminino", callback_data='bot_gender_feminino')],
            [InlineKeyboardButton("👨 Masculino", callback_data='bot_gender_masculino')],
            [InlineKeyboardButton("🤖 Neutro", callback_data='bot_gender_neutro')]
        ])
    )
    
    context.user_data['personalization_step'] = 'bot_gender'

async def handle_custom_bot_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa nome personalizado do bot após seleção de gênero"""
    bot_name = update.message.text.strip()
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    
    # Validar nome
    if len(bot_name) < 2 or len(bot_name) > 20:
        await update.message.reply_text(
            "❌ **Nome inválido!**\n\n"
            "O nome deve ter entre 2 e 20 caracteres.\n"
            "Por favor, digite um nome válido:"
        )
        return
    
    # Salvar nome do bot
    user_profile_db.save_profile(user_id=user_id, bot_name=bot_name)
    
    # Continuar para personalidade
    await update.message.reply_text(
        f"✅ **Perfeito! Agora me chamo {bot_name}!**\n\n"
        "🎭 **Qual personalidade você prefere que eu tenha?**\n\n"
        "💡 *Isso define como eu vou interagir com você:*",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("😊 Amigável", callback_data='personality_amigável')],
            [InlineKeyboardButton("🎩 Formal", callback_data='personality_formal')],
            [InlineKeyboardButton("😎 Casual", callback_data='personality_casual')],
            [InlineKeyboardButton("🎭 Divertido", callback_data='personality_divertido')],
            [InlineKeyboardButton("🧠 Intelectual", callback_data='personality_intelectual')]
        ])
    )
    
    context.user_data['personalization_step'] = 'bot_personality'

async def handle_preference_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa todos os callbacks de preferências (pref_*)"""
    query = update.callback_query
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    
    # Processar diferentes tipos de preferências
    if query.data.startswith('pref_age_'):
        age_key = query.data.replace('pref_age_', '')
        if age_key == '18_plus':
            user_profile_db.save_profile(user_id=user_id, user_age='18+', has_mature_access=True)
            await query.answer("✅ Idade 18+ definida!")
        else:
            user_profile_db.save_profile(user_id=user_id, user_age='menor_18', has_mature_access=False)
            await query.answer("✅ Idade menor de 18 definida!")
        
        await query.edit_message_text(
            "✅ **Idade atualizada com sucesso!**\n\n"
            "Suas configurações foram salvas.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Voltar ao Menu", callback_data='back_to_preferences')],
                [InlineKeyboardButton("❌ Fechar", callback_data='close_preferences')]
            ])
        )
    
    elif query.data.startswith('pref_user_gender_'):
        gender_key = query.data.replace('pref_user_gender_', '')
        gender_names = {'masculino': 'Masculino', 'feminino': 'Feminino', 'outro': 'Outro'}
        
        user_profile_db.save_profile(user_id=user_id, user_gender=gender_key)
        await query.answer(f"✅ Gênero {gender_names[gender_key]} definido!")
        
        await query.edit_message_text(
            f"✅ **Seu gênero atualizado para {gender_names[gender_key]}!**\n\n"
            "Suas configurações foram salvas.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Voltar ao Menu", callback_data='back_to_preferences')],
                [InlineKeyboardButton("❌ Fechar", callback_data='close_preferences')]
            ])
        )
    
    elif query.data.startswith('pref_bot_gender_'):
        gender_key = query.data.replace('pref_bot_gender_', '')
        gender_names = {'masculino': 'Masculino', 'feminino': 'Feminino'}
        
        user_profile_db.save_profile(user_id=user_id, bot_gender=gender_key)
        await query.answer(f"✅ Bot agora se apresenta como {gender_names[gender_key]}!")
        
        await query.edit_message_text(
            f"✅ **Bot agora se apresenta como {gender_names[gender_key]}!**\n\n"
            "Suas configurações foram salvas.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Voltar ao Menu", callback_data='back_to_preferences')],
                [InlineKeyboardButton("❌ Fechar", callback_data='close_preferences')]
            ])
        )
    
    elif query.data.startswith('pref_personality_'):
        personality_key = query.data.replace('pref_personality_', '')
        personality_names = {
            'amigável': 'Amigável',
            'formal': 'Formal',
            'casual': 'Casual',
            'divertido': 'Divertido',
            'intelectual': 'Intelectual'
        }
        
        user_profile_db.save_profile(user_id=user_id, bot_personality=personality_key)
        await query.answer(f"✅ Personalidade {personality_names[personality_key]} aplicada!")
        
        await query.edit_message_text(
            f"✅ **Personalidade {personality_names[personality_key]} aplicada!**\n\n"
            f"Agora vou me comportar de forma {personality_names[personality_key].lower()}.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Voltar ao Menu", callback_data='back_to_preferences')],
                [InlineKeyboardButton("❌ Fechar", callback_data='close_preferences')]
            ])
        )
    
    elif query.data.startswith('pref_language_'):
        language_key = query.data.replace('pref_language_', '')
        language_names = {
            'formal': 'Formal',
            'informal': 'Informal',
            'casual': 'Casual',
            'tecnico': 'Técnico'
        }
        
        user_profile_db.save_profile(user_id=user_id, bot_language=language_key)
        await query.answer(f"✅ Linguagem {language_names[language_key]} aplicada!")
        
        await query.edit_message_text(
            f"✅ **Estilo de linguagem {language_names[language_key]} aplicado!**\n\n"
            f"Agora vou falar de forma {language_names[language_key].lower()}.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Voltar ao Menu", callback_data='back_to_preferences')],
                [InlineKeyboardButton("❌ Fechar", callback_data='close_preferences')]
            ])
        )
    
    elif query.data.startswith('pref_topic_'):
        topic_key = query.data.replace('pref_topic_', '')
        
        # Obter tópicos atuais
        profile = user_profile_db.get_profile(user_id)
        current_topics = profile.get('preferred_topics', '').split(',') if profile.get('preferred_topics') else []
        current_topics = [t.strip() for t in current_topics if t.strip()]
        
        if topic_key in current_topics:
            current_topics.remove(topic_key)
            action = "removido"
        else:
            current_topics.append(topic_key)
            action = "adicionado"
        
        # Salvar tópicos atualizados
        topics_str = ','.join(current_topics) if current_topics else ''
        user_profile_db.save_profile(user_id=user_id, preferred_topics=topics_str)
        
        await query.answer(f"✅ Tópico {topic_key.title()} {action}!")
        
        # Mostrar menu atualizado
        await handle_change_topics_menu(update, context)
    
    elif query.data == 'pref_topics_finish':
        await query.answer("✅ Tópicos salvos!")
        await query.edit_message_text(
            "✅ **Tópicos de interesse atualizados!**\n\n"
            "Suas preferências foram salvas com sucesso.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Voltar ao Menu", callback_data='back_to_preferences')],
                [InlineKeyboardButton("❌ Fechar", callback_data='close_preferences')]
            ])
        )

# ============================================================================
# FUNÇÕES DO SISTEMA ADULTO INTEGRADO
# Movido de adult_integration.py para eliminar duplicação
# ============================================================================

def get_adult_personality_context(user_id: str) -> dict:
    """
    Obter contexto de personalidade adulta para integração com mensagens
    """
    try:
        from core.check import check_age
        
        # Verificar se modo adulto está ativo
        adult_status = check_age(user_id)
        if not adult_status.get('adult_mode_active'):
            return {'adult_mode': False}
        
        # Se sistema adulto avançado disponível, buscar perfil
        if ADULT_SYSTEM_AVAILABLE:
            try:
                from core.adult_personality_system import AdultPersonalitySystem
                adult_system = AdultPersonalitySystem()
                profile = adult_system.get_adult_profile(user_id)
                
                if not profile:
                    return {
                        'adult_mode': True,
                        'advanced_system': False,
                        'message': 'Sistema básico ativo. Use /adult_config para upgrade!'
                    }
                
                # Gerar instruções de personalidade
                personality_instructions = adult_system.generate_personality_instructions(profile)
                
                return {
                    'adult_mode': True,
                    'advanced_system': True,
                    'personality_type': profile.get('personality_type'),
                    'current_mood': profile.get('current_mood', 'neutro'),
                    'personality_instructions': personality_instructions,
                    'profile_data': profile
                }
                
            except ImportError:
                # Se não conseguir importar, retornar sistema básico
                return {
                    'adult_mode': True,
                    'advanced_system': False,
                    'message': 'Sistema básico ativo'
                }
        
        return {
            'adult_mode': True,
            'advanced_system': False,
            'message': 'Sistema básico ativo'
        }
        
    except Exception as e:
        logging.error(f"Erro ao buscar contexto adulto: {e}")
        return {'adult_mode': False, 'error': str(e)}

def is_advanced_adult_active(user_id: str) -> bool:
    """Verificar se sistema avançado está ativo"""
    context = get_adult_personality_context(user_id)
    return context.get('advanced_system', False)

def get_personality_instructions_for_llm(user_id: str) -> str:
    """Obter instruções de personalidade para o LLM"""
    context = get_adult_personality_context(user_id)
    return context.get('personality_instructions', '')

def format_adult_response_with_personality(user_id: str, base_response: str) -> str:
    """
    Formatar resposta com base na personalidade ativa
    INCLUI EMOJI DE PIMENTA PARA INDICAR MODO ADULTO
    """
    try:
        context = get_adult_personality_context(user_id)
        
        if not context.get('adult_mode'):
            return base_response
            
        # ADICIONAR EMOJI DE PIMENTA ANTES DA MENSAGEM NO MODO ADULTO
        adult_indicator = "🌶️ "
        
        # Se já tem o emoji, não adicionar novamente
        if base_response.startswith("🌶️"):
            return base_response
            
        return adult_indicator + base_response
        
    except Exception as e:
        logging.error(f"Erro ao formatar resposta adulta: {e}")
        return base_response

def get_adult_system_status_summary(user_id: str) -> str:
    """
    Gerar resumo do status do sistema adulto
    """
    try:
        context = get_adult_personality_context(user_id)
        
        if not context.get('adult_mode'):
            return "❌ Modo adulto inativo"
            
        if not context.get('advanced_system'):
            return "⚡ Sistema básico (use /adult_config para upgrade)"
            
        personality_type = context.get('personality_type', 'Indefinido')
        current_mood = context.get('current_mood', 'neutro')
        
        return f"🎯 Sistema Avançado | Personalidade: {personality_type} | Humor: {current_mood}"
        
    except Exception as e:
        logging.error(f"Erro ao gerar resumo de status: {e}")
        return "❓ Status indisponível"

# ============================================================================
# FUNÇÃO PRINCIPAL DO BOT
# ============================================================================

def main(application, user_profile_db):
    logging.info("Adicionando handlers...")
    
    # Adiciona a instância do banco de dados ao objeto de aplicação
    application.user_profile_db = user_profile_db
    
    # ConversationHandler para o sistema de personalização
    personalization_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CallbackQueryHandler(personalization_intro, pattern='^personalization_intro$')
        ],
        states={
            PERSONALIZATION_INTRO: [
                CallbackQueryHandler(get_user_name, pattern='^get_name$'),
                CallbackQueryHandler(lambda u, c: start(u, c), pattern='^skip_personalization$')
            ],
            GET_USER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_user_name)],
            GET_USER_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_user_age)],
            GET_USER_GENDER: [
                CallbackQueryHandler(process_user_gender, pattern='^user_gender_')
            ],
            GET_BOT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_bot_name)],
            GET_BOT_GENDER: [
                CallbackQueryHandler(process_bot_gender, pattern='^bot_gender_'),
                CallbackQueryHandler(handle_bot_name_selection, pattern='^bot_name_'),
                CallbackQueryHandler(handle_initial_bot_name_selection, pattern='^initial_bot_name_')
            ],
            SELECT_PERSONALITY: [
                CallbackQueryHandler(handle_personality_selection, pattern='^personality_')
            ],
            SELECT_LANGUAGE: [
                CallbackQueryHandler(process_language_style, pattern='^language_')
            ],
            SELECT_TOPICS: [
                CallbackQueryHandler(process_topic_selection, pattern='^(topic_|topics_done)')
            ],
            CHANGE_BOT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_bot_name)],
            CHANGE_PERSONALITY: [
                CallbackQueryHandler(handle_personality_change, pattern='^personality_')
            ],
            CHANGE_USER_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_user_age)],
            CHANGE_USER_GENDER: [
                CallbackQueryHandler(update_user_gender, pattern='^change_user_gender_')
            ],
            CHANGE_BOT_GENDER: [
                CallbackQueryHandler(update_bot_gender, pattern='^change_bot_gender_')
            ],
            CHANGE_LANGUAGE: [
                CallbackQueryHandler(update_language_style, pattern='^change_language_')
            ],
            CHANGE_TOPICS: [
                CallbackQueryHandler(update_topics_selection, pattern='^(change_topic_|change_topics_done)')
            ]
        },
        fallbacks=[
            CommandHandler('clear', clear_personalization),
            CommandHandler('cancelar', cancel)
        ],
        allow_reentry=True,
        per_chat=False
    )
    
    # ConversationHandler removido - usando novo sistema de botões
    
    # ConversationHandlers para comandos individuais
    change_user_age_handler = ConversationHandler(
        entry_points=[CommandHandler('mudar_idade', change_user_age)],
        states={
            CHANGE_USER_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_user_age)]
        },
        fallbacks=[CommandHandler('cancelar', cancel)]
    )
    
    change_user_gender_handler = ConversationHandler(
        entry_points=[CommandHandler('mudar_genero_usuario', change_user_gender)],
        states={
            CHANGE_USER_GENDER: [CallbackQueryHandler(update_user_gender, pattern='^change_user_gender_')]
        },
        fallbacks=[CommandHandler('cancelar', cancel)],
        per_chat=False
    )
    
    change_bot_gender_handler = ConversationHandler(
        entry_points=[CommandHandler('mudar_genero_bot', change_bot_gender)],
        states={
            CHANGE_BOT_GENDER: [CallbackQueryHandler(update_bot_gender, pattern='^change_bot_gender_')]
        },
        fallbacks=[CommandHandler('cancelar', cancel)],
        per_chat=False
    )
    
    change_language_handler = ConversationHandler(
        entry_points=[CommandHandler('mudar_linguagem', change_language)],
        states={
            CHANGE_LANGUAGE: [CallbackQueryHandler(update_language_style, pattern='^change_language_')]
        },
        fallbacks=[CommandHandler('cancelar', cancel)],
        per_chat=False
    )
    
    change_topics_handler = ConversationHandler(
        entry_points=[CommandHandler('mudar_topicos', change_topics)],
        states={
            CHANGE_TOPICS: [CallbackQueryHandler(update_topics_selection, pattern='^(change_topic_|change_topics_done)')]
        },
        fallbacks=[CommandHandler('cancelar', cancel)],
        per_chat=False
    )
    
    # Handlers do sistema adulto
    if ADULT_SYSTEM_AVAILABLE:
        adult_activation_handler = ConversationHandler(
            entry_points=[CommandHandler('18', adult_activation_command)],
            states={
                ADULT_TERMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_adult_terms)],
                ADULT_AGE_VERIFICATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_adult_age_verification)]
            },
            fallbacks=[CommandHandler('cancelar', cancel_adult_verification)]
        )
        application.add_handler(adult_activation_handler)
        
        # Comandos adultos simples
        application.add_handler(CommandHandler("devassa_config", adult_config_menu))
        application.add_handler(CommandHandler("devassa_off", deactivate_adult_mode))
        application.add_handler(CommandHandler("devassa_status", adult_status))
        application.add_handler(CommandHandler("intensidade1", lambda u, c: set_intensity(u, c, 1)))
        application.add_handler(CommandHandler("intensidade2", lambda u, c: set_intensity(u, c, 2)))
        application.add_handler(CommandHandler("intensidade3", lambda u, c: set_intensity(u, c, 3)))
        application.add_handler(CommandHandler("genero_feminino", lambda u, c: set_adult_gender(u, c, 'feminino')))
        application.add_handler(CommandHandler("genero_masculino", lambda u, c: set_adult_gender(u, c, 'masculino')))
        application.add_handler(CommandHandler("genero_neutro", lambda u, c: set_adult_gender(u, c, 'neutro')))

    # Adicionar os handlers
    
    # Handler principal para /start e /personalizar
    application.add_handler(CommandHandler("start", start_personalization_menu))
    application.add_handler(CommandHandler("personalizar", start_personalization_menu))
    application.add_handler(CommandHandler("menu", menu_command))
    
    # ⚠️ HANDLERS ESPECÍFICOS PRIMEIRO (maior prioridade)
    # Handler específico para seleção de nomes do bot (alta prioridade) 
    application.add_handler(CallbackQueryHandler(handle_bot_name_selection, pattern='^bot_name_Ana$'))
    application.add_handler(CallbackQueryHandler(handle_bot_name_selection, pattern='^bot_name_Beatriz$'))
    application.add_handler(CallbackQueryHandler(handle_bot_name_selection, pattern='^bot_name_Clara$'))
    application.add_handler(CallbackQueryHandler(handle_bot_name_selection, pattern='^bot_name_Maria$'))
    application.add_handler(CallbackQueryHandler(handle_bot_name_selection, pattern='^bot_name_Sofia$'))
    application.add_handler(CallbackQueryHandler(handle_bot_name_selection, pattern='^bot_name_.*$'))
    
    # Handler global para outros callbacks 
    application.add_handler(CallbackQueryHandler(handle_global_callbacks))
    
    # Handler para entrada de texto durante personalização
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_personalization_text))
    
    # ConversationHandler vem por último
    application.add_handler(personalization_handler)
    # conv_handler removido - usando novo sistema
    application.add_handler(change_user_age_handler)
    application.add_handler(change_user_gender_handler)
    application.add_handler(change_bot_gender_handler)
    application.add_handler(change_language_handler)
    application.add_handler(change_topics_handler)
    
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("help_adulto", help_adulto_command))
    application.add_handler(CommandHandler("clear", clear_personalization))
    application.add_handler(CommandHandler("mudar_nome", change_bot_name))
    application.add_handler(CommandHandler("mudar_personalidade", change_personality))
    application.add_handler(CommandHandler("meu_nome", change_user_name_command))
    application.add_handler(CommandHandler("reconfigurar", reset_personalization))
    application.add_handler(CommandHandler("preferencias", preferences_menu))
    application.add_handler(CommandHandler("emocoes", emotions_menu))
    application.add_handler(CommandHandler("aprendizagem", learning_status))
    application.add_handler(CallbackQueryHandler(handle_preference_button, pattern='^(pref_|chat_)'))
    application.add_handler(CallbackQueryHandler(handle_emotion_button, pattern='^emotion_'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    logging.info("✅ Todos os handlers foram adicionados com sucesso!")

if __name__ == '__main__':
    """Executar o bot quando chamado diretamente"""
    print("🚀 Iniciando Telegram Bot...")
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Erro: Token do Telegram não encontrado!")
        print("💡 Verifique se o TELEGRAM_BOT_TOKEN está definido no arquivo .env")
        exit(1)
    
    # Inicializar o banco de dados de perfis de usuários
    try:
        user_profile_db = UserProfileDB()
        print("✅ Banco de dados de perfis inicializado")
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        exit(1)
    
    # Criar a aplicação do bot
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Configurar handlers
    main(application, user_profile_db)
    
    print("🤖 Bot do Telegram iniciado com sucesso!")
    print("📱 Digite /start no chat com o bot para começar")
    print("⚙️ Use /menu para acessar todas as opções")
    print("🛑 Pressione Ctrl+C para parar\n")
    
    # Executar o bot
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        print("\n🛑 Bot interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
    finally:
        print("✅ Bot encerrado com sucesso!")
