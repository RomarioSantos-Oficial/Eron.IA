"""
Integração do Sistema Adulto Avançado com Message Handlers
"""
import logging
from core.adult_personality_system import AdultPersonalitySystem
from core.check import check_age

logger = logging.getLogger(__name__)
adult_system = AdultPersonalitySystem()

def get_adult_personality_context(user_id: str) -> dict:
    """
    Obter contexto de personalidade adulta para integração com mensagens
    """
    try:
        # Verificar se modo adulto está ativo
        adult_status = check_age(user_id)
        if not adult_status.get('adult_mode_active'):
            return {'adult_mode': False}
        
        # Buscar perfil avançado
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
        
    except Exception as e:
        logger.error(f"Erro ao buscar contexto adulto: {e}")
        return {'adult_mode': False, 'error': str(e)}

def update_adult_session_feedback(user_id: str, message: str, response: str, rating: int = None):
    """
    Registrar feedback da sessão adulta
    """
    try:
        adult_system.update_session_feedback(user_id, {
            'user_message': message,
            'bot_response': response,
            'rating': rating,
            'timestamp': 'now'
        })
    except Exception as e:
        logger.error(f"Erro ao registrar feedback de sessão: {e}")

def format_adult_response_with_personality(user_id: str, base_response: str) -> str:
    """
    Formatar resposta com base na personalidade ativa
    """
    try:
        context = get_adult_personality_context(user_id)
        
        if not context.get('advanced_system'):
            return base_response
            
        personality_type = context.get('personality_type')
        current_mood = context.get('current_mood')
        
        # Adicionar indicadores visuais baseados na personalidade
        personality_emojis = {
            'sedutora': '💫',
            'dominante': '🔥', 
            'travessa': '😈',
            'carinhosa': '😊',
            'criativa': '🎨',
            'equilibrada': '🌟'
        }
        
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
        
        personality_emoji = personality_emojis.get(personality_type, '🎭')
        mood_emoji = mood_emojis.get(current_mood, '💭')
        
        # Formatação sutil da resposta
        formatted_response = f"{personality_emoji}{mood_emoji} {base_response}"
        
        return formatted_response
        
    except Exception as e:
        logger.error(f"Erro ao formatar resposta com personalidade: {e}")
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
        
        personalities = adult_system.get_personality_types()
        personality_info = personalities.get(personality_type, {})
        emoji = personality_info.get('emoji', '🎭')
        name = personality_info.get('name', personality_type.title())
        
        return f"🎯 Sistema Avançado | {emoji} {name} | Humor: {current_mood}"
        
    except Exception as e:
        logger.error(f"Erro ao gerar resumo de status: {e}")
        return "❓ Status indisponível"

# Funções de conveniência para integração fácil
def is_advanced_adult_active(user_id: str) -> bool:
    """Verificar se sistema avançado está ativo"""
    context = get_adult_personality_context(user_id)
    return context.get('advanced_system', False)

def get_personality_instructions_for_llm(user_id: str) -> str:
    """Obter instruções de personalidade para o LLM"""
    context = get_adult_personality_context(user_id)
    return context.get('personality_instructions', '')

def log_adult_interaction(user_id: str, interaction_type: str, details: dict = None):
    """Log de interações do sistema adulto"""
    try:
        if details is None:
            details = {}
            
        logger.info(f"Adult System Interaction - User: {user_id}, Type: {interaction_type}, Details: {details}")
        
        # Se tiver perfil avançado, registrar na base de dados
        if is_advanced_adult_active(user_id):
            adult_system.update_session_feedback(user_id, {
                'interaction_type': interaction_type,
                'details': str(details),
                'timestamp': 'now'
            })
            
    except Exception as e:
        logger.error(f"Erro ao registrar interação adulta: {e}")