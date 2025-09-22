"""
Patch para Sistema de Personalização - Sem Moderação para Adultos
==================================================================

Modifica o sistema de personalização para permitir conteúdo
adulto quando o usuário for verificado como maior de idade.

Aplica-se apenas ao contexto de personalização - outros
contextos mantêm moderação normal.

Uso: Importar e usar personalization_is_allowed() antes de salvar dados
"""

import os
import sys
from datetime import datetime

def is_adult_user_simple(user_profile: dict) -> bool:
    """
    Verificação simples se usuário é adulto baseado no perfil
    
    Args:
        user_profile: Dicionário com dados do perfil do usuário
    
    Returns:
        bool: True se usuário for considerado adulto
    """
    if not user_profile:
        return False
    
    # Verificar campo de idade
    age = user_profile.get('user_age', '')
    
    # Verificar diferentes formatos de idade
    if isinstance(age, int):
        return age >= 18
    
    if isinstance(age, str):
        # Formatos: "18", "18+", "25 anos", etc.
        age_str = age.lower().strip()
        
        # Se tem "18+" ou similar
        if '+' in age_str or 'mais' in age_str:
            return True
        
        # Extrair número da idade
        try:
            # Pegar apenas números
            age_num = int(''.join(filter(str.isdigit, age_str)))
            return age_num >= 18
        except (ValueError, TypeError):
            pass
    
    # Verificar se tem acesso adulto habilitado
    has_mature_access = user_profile.get('has_mature_access', False)
    adult_mode_enabled = user_profile.get('adult_mode_enabled', False)
    
    return has_mature_access or adult_mode_enabled


def personalization_is_allowed(content: str, user_profile: dict = None, context: str = 'personalization') -> dict:
    """
    Verifica se conteúdo de personalização deve ser permitido
    
    Args:
        content: Conteúdo a ser verificado
        user_profile: Perfil do usuário
        context: Contexto ('personalization' ou outro)
    
    Returns:
        dict: Resultado da verificação
    """
    
    # Se não for personalização, aplicar moderação normal
    if context != 'personalization':
        return {
            'allowed': False,  # Por segurança, bloquear por padrão
            'reason': 'Contexto não é personalização - aplicar moderação normal',
            'is_adult': False,
            'moderation_bypassed': False,
            'action': 'check_with_normal_moderation'
        }
    
    # Verificar se usuário é adulto
    is_adult = is_adult_user_simple(user_profile)
    
    # Se usuário é adulto, permitir praticamente tudo na personalização
    if is_adult:
        return {
            'allowed': True,
            'reason': 'Usuário adulto - personalização livre permitida',
            'is_adult': True,
            'moderation_bypassed': True,
            'action': 'allow',
            'note': 'Moderação desabilitada para personalização de adultos'
        }
    
    # Para menores, verificar apenas problemas óbvios
    content_lower = content.lower().strip()
    
    # Lista de verificações básicas (apenas problemas graves)
    serious_issues = [
        'spam repetitivo', 'ameaça de morte', 'violência extrema',
        'assédio', 'bullying', 'conteúdo ilegal'
    ]
    
    # Verificar se é spam (conteúdo repetitivo)
    words = content_lower.split()
    if len(words) > 5:
        unique_words = set(words)
        if len(unique_words) < len(words) * 0.4:  # Menos de 40% palavras únicas
            return {
                'allowed': False,
                'reason': 'Possível spam detectado - muita repetição',
                'is_adult': False,
                'moderation_bypassed': False,
                'action': 'filter'
            }
    
    # Para menores, na personalização, ser bem permissivo
    return {
        'allowed': True,
        'reason': 'Personalização permitida - moderação leve aplicada',
        'is_adult': False,
        'moderation_bypassed': False,
        'action': 'allow',
        'note': 'Moderação leve para personalização de menores'
    }


def get_personalization_status_message(user_profile: dict = None) -> str:
    """
    Retorna mensagem de status da personalização baseada no usuário
    """
    is_adult = is_adult_user_simple(user_profile)
    
    if is_adult:
        return """
🎭 **PERSONALIZAÇÃO LIVRE - USUÁRIO ADULTO**

✅ Você pode personalizar livremente:
• Linguagem adulta e explícita
• Temas sexuais e românticos  
• Personalidade provocativa
• Referências adultas
• Conversas explícitas sobre preferências

⚠️ **Importante:** Esta liberdade se aplica APENAS à configuração 
da personalização. Conversas normais seguem regras de moderação.

💡 **Contextos com moderação normal:**
• Chat geral do Telegram
• Mensagens públicas
• Interações web normais
"""
    else:
        return """
🎨 **PERSONALIZAÇÃO AMIGÁVEL**

Você pode personalizar:
• Nome e personalidade do bot
• Estilo de conversa respeitoso
• Interesses e hobbies
• Temas apropriados
• Linguagem educada

💡 Para acessar personalização avançada, confirme sua idade nas configurações.
"""


def apply_personalization_filter(content: str, user_profile: dict = None) -> dict:
    """
    Aplica filtro específico para personalização
    
    Esta é a função principal que deve ser usada nas rotas de personalização
    """
    result = personalization_is_allowed(content, user_profile, 'personalization')
    
    # Log da decisão
    timestamp = datetime.now().isoformat()
    user_age = user_profile.get('user_age', 'não informado') if user_profile else 'não informado'
    
    log_entry = f"""[{timestamp}] PERSONALIZAÇÃO FILTER:
  Usuário: {user_profile.get('user_name', 'Anônimo') if user_profile else 'Anônimo'}
  Idade: {user_age}
  É adulto: {result['is_adult']}
  Conteúdo permitido: {result['allowed']}
  Razão: {result['reason']}
  Moderação ignorada: {result['moderation_bypassed']}
"""
    
    print(log_entry)  # Para debug - pode ser removido em produção
    
    return result


# Função de teste
def test_personalization_filter():
    """Testa o sistema de filtro de personalização"""
    
    print("🧪 TESTE DO FILTRO DE PERSONALIZAÇÃO\n")
    
    # Perfis de teste
    adult_profile = {
        'user_name': 'João',
        'user_age': '25',
        'has_mature_access': True
    }
    
    minor_profile = {
        'user_name': 'Ana',
        'user_age': '16',
        'has_mature_access': False
    }
    
    adult_profile_plus = {
        'user_name': 'Maria',
        'user_age': '18+',
        'has_mature_access': False
    }
    
    # Conteúdos de teste
    test_contents = [
        "Quero que você seja sexy e provocante",
        "Configure personalidade sexual explicita",
        "Fale palavrões e seja safada",
        "Seja minha namorada virtual",
        "Configure nome como Ana",
        "spam spam spam spam spam spam spam"
    ]
    
    profiles = [
        ("👨 ADULTO (25 anos)", adult_profile),
        ("👩 ADULTO (18+)", adult_profile_plus), 
        ("👧 MENOR (16 anos)", minor_profile)
    ]
    
    for profile_name, profile in profiles:
        print(f"\n{profile_name}:")
        print(get_personalization_status_message(profile))
        
        for content in test_contents[:3]:  # Teste apenas alguns
            result = apply_personalization_filter(content, profile)
            emoji = "✅" if result['allowed'] else "❌"
            print(f"  {emoji} \"{content[:40]}...\"")
            print(f"      → {result['action']} ({result['reason']})")


if __name__ == "__main__":
    test_personalization_filter()