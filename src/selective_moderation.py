"""
Sistema de Moderação Seletiva - Eron.IA
=======================================

Configuração específica que permite que apenas a personalização
não tenha moderação, enquanto outras funcionalidades mantêm as restrições.

Funcionalidades:
- Personalização: SEM moderação (adultos podem conversar livremente)
- Chat geral: COM moderação
- Outros recursos: COM moderação

Autor: Eron.IA System
"""

from enum import Enum
from typing import Dict, Any, Optional
import os

class ModerationContext(Enum):
    """Contextos onde a moderação pode ser aplicada"""
    PERSONALIZATION = "personalization"    # Sem moderação para personalização
    GENERAL_CHAT = "general_chat"         # Com moderação
    PUBLIC_CHAT = "public_chat"           # Com moderação
    TELEGRAM_BOT = "telegram_bot"         # Com moderação
    WEB_INTERFACE = "web_interface"       # Com moderação

class SelectiveModerationConfig:
    """Configuração seletiva de moderação por contexto"""
    
    def __init__(self):
        self.moderation_settings = self._get_default_settings()
    
    def _get_default_settings(self) -> Dict[ModerationContext, Dict[str, Any]]:
        """Define configurações padrão por contexto"""
        
        return {
            # PERSONALIZAÇÃO: Sem moderação para adultos
            ModerationContext.PERSONALIZATION: {
                'enabled': False,
                'description': '💬 Personalização livre para adultos',
                'adult_content_allowed': True,
                'sexual_content_allowed': True,
                'explicit_language_allowed': True,
                'drug_references_allowed': True,
                'only_check_spam': False,
                'require_adult_verification': True,
                'reasons': [
                    'Permite conversas adultas na personalização',
                    'Usuários podem definir preferências explícitas',
                    'Personalização de personalidade sem limitações'
                ]
            },
            
            # CHAT GERAL: Com moderação normal
            ModerationContext.GENERAL_CHAT: {
                'enabled': True,
                'description': '🛡️ Chat geral com moderação',
                'adult_content_allowed': False,
                'sexual_content_allowed': False,
                'explicit_language_allowed': False,
                'drug_references_allowed': False,
                'only_check_spam': False,
                'require_adult_verification': False,
                'auto_filter': True,
                'warn_inappropriate': True
            },
            
            # CHAT PÚBLICO: Moderação mais rigorosa
            ModerationContext.PUBLIC_CHAT: {
                'enabled': True,
                'description': '🔒 Chat público com moderação rigorosa',
                'adult_content_allowed': False,
                'sexual_content_allowed': False,
                'explicit_language_allowed': False,
                'drug_references_allowed': False,
                'only_check_spam': False,
                'require_adult_verification': False,
                'auto_filter': True,
                'strict_mode': True
            },
            
            # TELEGRAM BOT: Moderação padrão
            ModerationContext.TELEGRAM_BOT: {
                'enabled': True,
                'description': '🤖 Telegram com moderação padrão',
                'adult_content_allowed': False,
                'sexual_content_allowed': False,
                'explicit_language_allowed': False,
                'drug_references_allowed': False,
                'only_check_spam': False,
                'require_adult_verification': False,
                'auto_filter': True
            },
            
            # WEB INTERFACE: Moderação padrão
            ModerationContext.WEB_INTERFACE: {
                'enabled': True,
                'description': '🌐 Web interface com moderação',
                'adult_content_allowed': False,
                'sexual_content_allowed': False,
                'explicit_language_allowed': False,
                'drug_references_allowed': False,
                'only_check_spam': False,
                'require_adult_verification': False,
                'auto_filter': True
            }
        }
    
    def get_context_config(self, context: ModerationContext) -> Dict[str, Any]:
        """Obtém configuração para um contexto específico"""
        return self.moderation_settings.get(context, self.moderation_settings[ModerationContext.GENERAL_CHAT])
    
    def should_moderate(self, context: ModerationContext, user_is_adult: bool = False) -> bool:
        """Determina se deve moderar baseado no contexto"""
        config = self.get_context_config(context)
        
        # Se for personalização e usuário for adulto, não moderar
        if context == ModerationContext.PERSONALIZATION and user_is_adult:
            return False
        
        return config.get('enabled', True)
    
    def is_content_allowed(self, context: ModerationContext, content_type: str, user_is_adult: bool = False) -> bool:
        """Verifica se um tipo de conteúdo é permitido no contexto"""
        config = self.get_context_config(context)
        
        # Mapeamento de tipos de conteúdo
        content_mapping = {
            'adult': 'adult_content_allowed',
            'sexual': 'sexual_content_allowed',
            'explicit': 'explicit_language_allowed',
            'drugs': 'drug_references_allowed'
        }
        
        config_key = content_mapping.get(content_type)
        if not config_key:
            return True  # Se não reconhecer o tipo, permitir
        
        # Para personalização de adultos, sempre permitir
        if context == ModerationContext.PERSONALIZATION and user_is_adult:
            return True
        
        return config.get(config_key, False)
    
    def get_moderation_message(self, context: ModerationContext) -> str:
        """Retorna mensagem de moderação para o contexto"""
        config = self.get_context_config(context)
        
        if context == ModerationContext.PERSONALIZATION:
            return """
🎭 **PERSONALIZAÇÃO LIVRE**

Para usuários adultos verificados, a personalização permite:
• Conversas explícitas sobre preferências
• Definição de personalidade adulta
• Configuração de linguagem sem restrições
• Temas adultos na personalização do bot

⚠️ **Nota:** Apenas aplicável na configuração da personalização.
Outros chats mantêm moderação normal.
"""
        else:
            return f"🛡️ **MODERAÇÃO ATIVA** - {config['description']}"
    
    def get_status_summary(self) -> str:
        """Retorna resumo do status de moderação"""
        status = "🎯 **CONFIGURAÇÃO DE MODERAÇÃO SELETIVA**\n\n"
        
        for context, config in self.moderation_settings.items():
            emoji = "❌" if not config['enabled'] else "✅"
            status += f"{emoji} **{context.value.title()}:** {config['description']}\n"
        
        status += "\n💡 **Resumo:**\n"
        status += "• Personalização: Livre para adultos\n"
        status += "• Demais contextos: Moderação ativa\n"
        
        return status


class PersonalizationModerator:
    """Moderador específico para personalização"""
    
    def __init__(self):
        self.config = SelectiveModerationConfig()
    
    def should_allow_personalization_content(self, user_id: str, content: str, user_is_adult: bool = False) -> Dict[str, Any]:
        """Verifica se deve permitir conteúdo na personalização"""
        
        # Se usuário é adulto, permitir tudo na personalização
        if user_is_adult:
            return {
                'allowed': True,
                'reason': 'Usuário adulto - personalização livre',
                'action': 'allow',
                'context': 'personalization',
                'moderation_disabled': True
            }
        
        # Para menores, aplicar moderação leve (apenas verificar spam/assédio)
        if self._is_spam_or_harassment(content):
            return {
                'allowed': False,
                'reason': 'Possível spam ou assédio detectado',
                'action': 'filter',
                'context': 'personalization',
                'moderation_disabled': False
            }
        
        return {
            'allowed': True,
            'reason': 'Conteúdo de personalização permitido',
            'action': 'allow',
            'context': 'personalization',
            'moderation_disabled': False
        }
    
    def _is_spam_or_harassment(self, content: str) -> bool:
        """Verificação básica de spam/assédio"""
        content_lower = content.lower()
        
        spam_indicators = ['compre agora', 'clique aqui', 'promoção única']
        harassment_indicators = ['ameaça', 'vou te matar', 'odeio você']
        
        for indicator in spam_indicators + harassment_indicators:
            if indicator in content_lower:
                return True
        
        # Verificar repetição excessiva
        words = content_lower.split()
        if len(words) > 10 and len(set(words)) < len(words) * 0.5:
            return True
        
        return False


# Instância global
selective_config = SelectiveModerationConfig()
personalization_moderator = PersonalizationModerator()


def get_selective_config() -> SelectiveModerationConfig:
    """Retorna configuração seletiva global"""
    return selective_config


def check_personalization_moderation(user_id: str, content: str, user_is_adult: bool = False) -> Dict[str, Any]:
    """Função helper para verificar moderação na personalização"""
    return personalization_moderator.should_allow_personalization_content(user_id, content, user_is_adult)


def is_moderation_enabled_for_context(context: str, user_is_adult: bool = False) -> bool:
    """Verifica se moderação está habilitada para um contexto"""
    try:
        context_enum = ModerationContext(context)
        return selective_config.should_moderate(context_enum, user_is_adult)
    except ValueError:
        return True  # Por segurança, habilitar moderação se contexto desconhecido


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            config = get_selective_config()
            print(config.get_status_summary())
        elif sys.argv[1] == "test":
            # Teste rápido
            print("🧪 TESTE DE MODERAÇÃO SELETIVA\n")
            
            test_cases = [
                ("Personalização adulto", "personalization", "Quero conversar sobre sexo", True),
                ("Personalização menor", "personalization", "Quero conversar sobre sexo", False),
                ("Chat geral", "general_chat", "Quero conversar sobre sexo", True),
                ("Telegram bot", "telegram_bot", "Palavrão aqui", False)
            ]
            
            for name, context, content, is_adult in test_cases:
                try:
                    context_enum = ModerationContext(context)
                    should_moderate = selective_config.should_moderate(context_enum, is_adult)
                    emoji = "✅" if not should_moderate else "🛡️"
                    print(f"{emoji} {name}: {'Permitido' if not should_moderate else 'Moderado'}")
                except ValueError:
                    print(f"❓ {name}: Contexto inválido")
    else:
        print("Comandos:")
        print("  python selective_moderation.py status  # Ver configurações")
        print("  python selective_moderation.py test    # Teste rápido")