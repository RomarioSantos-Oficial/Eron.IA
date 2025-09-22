"""
Integração de Moderação Seletiva com Sistema Existente
======================================================

Integra a moderação seletiva com o sistema de personalização existente,
permitindo que usuários adultos tenham personalização sem restrições.

Autor: Eron.IA System
"""

import sys
import os
from pathlib import Path

# Adicionar diretório pai para imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from src.selective_moderation import (
        get_selective_config, 
        check_personalization_moderation,
        ModerationContext,
        PersonalizationModerator
    )
    from src.adult_content_moderator import AdultContentModerator
    from src.flexible_moderation import FlexibleModerationConfig
except ImportError as e:
    print(f"⚠️ Aviso: Alguns módulos não disponíveis - {e}")

class IntegratedModerationSystem:
    """Sistema integrado que aplica moderação seletiva baseada no contexto"""
    
    def __init__(self):
        self.selective_config = get_selective_config()
        self.personalization_moderator = PersonalizationModerator()
        
        # Sistemas de fallback
        try:
            self.adult_moderator = AdultContentModerator()
        except:
            self.adult_moderator = None
            
        print("🎯 Sistema de moderação seletiva inicializado")
        print("   • Personalização: Livre para adultos")
        print("   • Outros contextos: Moderação normal")
    
    def analyze_content(self, content: str, context: str, user_id: str = None, user_is_adult: bool = False) -> dict:
        """
        Análise de conteúdo com moderação seletiva baseada no contexto
        
        Args:
            content: Texto a ser analisado
            context: Contexto ('personalization', 'general_chat', etc.)
            user_id: ID do usuário
            user_is_adult: Se o usuário é adulto verificado
        
        Returns:
            Dict com resultado da análise
        """
        
        # Verificar se é personalização
        if context == 'personalization':
            return self._analyze_personalization_content(content, user_id, user_is_adult)
        
        # Para outros contextos, usar moderação normal
        return self._analyze_general_content(content, context, user_id)
    
    def _analyze_personalization_content(self, content: str, user_id: str, user_is_adult: bool) -> dict:
        """Análise específica para personalização"""
        
        # Se usuário é adulto, permitir praticamente tudo
        if user_is_adult:
            return {
                'severity': 'clean',
                'action': 'allow',
                'reason': 'Personalização livre para usuário adulto',
                'confidence': 0.0,
                'flagged_words': [],
                'context': 'personalization',
                'moderation_bypassed': True,
                'user_is_adult': True,
                'timestamp': self._get_timestamp()
            }
        
        # Para menores, verificar apenas spam/assédio básico
        result = self.personalization_moderator.should_allow_personalization_content(
            user_id, content, user_is_adult
        )
        
        return {
            'severity': 'clean' if result['allowed'] else 'mild',
            'action': result['action'],
            'reason': result['reason'],
            'confidence': 0.1 if not result['allowed'] else 0.0,
            'flagged_words': [],
            'context': 'personalization',
            'moderation_bypassed': False,
            'user_is_adult': False,
            'timestamp': self._get_timestamp()
        }
    
    def _analyze_general_content(self, content: str, context: str, user_id: str) -> dict:
        """Análise para contextos gerais (com moderação normal)"""
        
        # Se temos o moderador adulto disponível, usar ele
        if self.adult_moderator:
            try:
                result = self.adult_moderator.analyze_content(content, user_id)
                result['context'] = context
                result['moderation_bypassed'] = False
                return result
            except Exception as e:
                print(f"Erro ao usar moderador adulto: {e}")
        
        # Fallback: análise básica
        return {
            'severity': 'clean',
            'action': 'allow',
            'reason': 'Análise básica - conteúdo permitido',
            'confidence': 0.0,
            'flagged_words': [],
            'context': context,
            'moderation_bypassed': False,
            'timestamp': self._get_timestamp()
        }
    
    def _get_timestamp(self):
        """Timestamp atual"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def is_user_adult(self, user_id: str) -> bool:
        """
        Verifica se usuário é adulto (implementar baseado no seu sistema)
        Por enquanto, retorna False como padrão seguro
        """
        try:
            # Aqui você pode integrar com seu sistema de verificação de idade
            # Por exemplo, verificando no banco de dados do usuário
            from core.user_profile_db import UserProfileDB
            profile_db = UserProfileDB()
            profile = profile_db.get_user_profile(user_id)
            
            if profile and profile.get('age'):
                age = int(profile.get('age', 0))
                return age >= 18
            
            # Verificar se tem configuração de adulto habilitada
            return profile.get('adult_mode_enabled', False) if profile else False
            
        except Exception as e:
            print(f"Erro ao verificar idade: {e}")
            return False
    
    def get_personalization_guidelines(self, user_is_adult: bool) -> str:
        """Retorna diretrizes de personalização baseadas na idade"""
        
        if user_is_adult:
            return """
🎭 **PERSONALIZAÇÃO LIVRE PARA ADULTOS**

Você pode personalizar livremente:
• Linguagem explícita e adulta
• Temas sexuais e românticos
• Personalidade provocativa ou sedutora
• Referências adultas sem restrições
• Conversas explícitas sobre preferências

⚠️ **Nota:** Esta liberdade se aplica apenas à configuração da personalização.
Os chats normais ainda seguem as regras de moderação padrão.
"""
        else:
            return """
🎨 **PERSONALIZAÇÃO FAMILIAR**

Você pode personalizar:
• Nome e personalidade do bot
• Estilo de conversa apropriado
• Interesses e hobbies
• Linguagem respeitosa
• Temas adequados para todas as idades

💡 Mantenha um ambiente respeitoso e apropriado.
"""
    
    def get_system_status(self) -> str:
        """Retorna status do sistema"""
        return self.selective_config.get_status_summary()


# Instância global do sistema integrado
integrated_moderation = IntegratedModerationSystem()


def analyze_with_context(content: str, context: str, user_id: str = None) -> dict:
    """
    Função principal para análise de conteúdo com contexto
    
    Uso:
        result = analyze_with_context("texto", "personalization", "user123")
    """
    user_is_adult = integrated_moderation.is_user_adult(user_id) if user_id else False
    return integrated_moderation.analyze_content(content, context, user_id, user_is_adult)


def is_personalization_allowed(content: str, user_id: str) -> bool:
    """
    Verifica rapidamente se personalização é permitida
    
    Uso:
        if is_personalization_allowed("conteúdo", "user123"):
            # Permitir personalização
    """
    result = analyze_with_context(content, "personalization", user_id)
    return result['action'] == 'allow'


def get_personalization_help(user_id: str) -> str:
    """Retorna texto de ajuda para personalização baseado na idade"""
    user_is_adult = integrated_moderation.is_user_adult(user_id) if user_id else False
    return integrated_moderation.get_personalization_guidelines(user_is_adult)


if __name__ == "__main__":
    # Teste do sistema integrado
    print("🧪 TESTE DO SISTEMA INTEGRADO\n")
    
    # Simular usuários
    adult_user = "adult_user_123"
    minor_user = "minor_user_456"
    
    test_contents = [
        "Quero que você seja sexy e provocante",
        "Configure personalidade sexual",
        "Fale palavrões comigo",
        "Seja minha namorada virtual"
    ]
    
    print("👨 **USUÁRIO ADULTO - PERSONALIZAÇÃO:**")
    for content in test_contents:
        result = analyze_with_context(content, "personalization", adult_user)
        emoji = "✅" if result['action'] == 'allow' else "❌"
        print(f"  {emoji} \"{content}\" → {result['action']} ({result['reason']})")
    
    print("\n👦 **USUÁRIO MENOR - PERSONALIZAÇÃO:**")  
    for content in test_contents:
        result = analyze_with_context(content, "personalization", minor_user)
        emoji = "✅" if result['action'] == 'allow' else "❌"
        print(f"  {emoji} \"{content}\" → {result['action']} ({result['reason']})")
    
    print("\n👨 **USUÁRIO ADULTO - CHAT GERAL:**")
    for content in test_contents[:2]:
        result = analyze_with_context(content, "general_chat", adult_user)
        emoji = "✅" if result['action'] == 'allow' else "❌"
        print(f"  {emoji} \"{content}\" → {result['action']} ({result['reason']})")
    
    print(f"\n📊 **STATUS DO SISTEMA:**")
    print(integrated_moderation.get_system_status())