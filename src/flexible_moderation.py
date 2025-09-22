"""
Configurações de Moderação Flexível - Eron.IA
==============================================

Este arquivo permite configurar o sistema de moderação de forma mais flexível,
incluindo modos permissivos ou completamente desabilitados para conversas adultas.

Opções de configuração:
1. DISABLED - Moderação completamente desabilitada
2. PERMISSIVE - Apenas bloqueia conteúdo extremamente ofensivo
3. MODERATE - Configuração padrão
4. STRICT - Configuração mais restritiva
5. ADULT_FRIENDLY - Permite conversas adultas mas bloqueia spam/abuso

Autor: Eron.IA System
"""

from enum import Enum
from typing import Dict, Any
import os

class ModerationMode(Enum):
    """Modos de moderação disponíveis"""
    DISABLED = "disabled"           # Sem moderação
    ADULT_FRIENDLY = "adult_friendly"  # Permite conversas adultas
    PERMISSIVE = "permissive"       # Muito permissivo
    MODERATE = "moderate"           # Padrão
    STRICT = "strict"               # Mais restritivo

class FlexibleModerationConfig:
    """Configuração flexível de moderação"""
    
    def __init__(self):
        self.mode = self._get_moderation_mode()
        self.config = self._get_config_for_mode()
    
    def _get_moderation_mode(self) -> ModerationMode:
        """Obtém modo de moderação do .env"""
        mode_str = os.getenv('MODERATION_MODE', 'moderate').lower()
        
        try:
            return ModerationMode(mode_str)
        except ValueError:
            print(f"⚠️ Modo '{mode_str}' inválido, usando 'moderate'")
            return ModerationMode.MODERATE
    
    def _get_config_for_mode(self) -> Dict[str, Any]:
        """Retorna configuração baseada no modo"""
        
        configs = {
            ModerationMode.DISABLED: {
                'enabled': False,
                'description': '🔓 Moderação completamente DESABILITADA - Sem filtros',
                'block_severe': False,
                'filter_moderate': False,
                'warn_mild': False,
                'auto_actions': False,
                'sensitivity_multiplier': 0.0,
                'patterns_active': [],
                'adult_content_allowed': True,
                'sexual_content_allowed': True,
                'drug_references_allowed': True,
                'offensive_language_allowed': True
            },
            
            ModerationMode.ADULT_FRIENDLY: {
                'enabled': True,
                'description': '💬 AMIGÁVEL PARA ADULTOS - Permite conversas explícitas',
                'block_severe': False,    # Não bloquear conteúdo severo
                'filter_moderate': False, # Não filtrar conteúdo moderado
                'warn_mild': False,      # Não avisar sobre conteúdo leve
                'auto_actions': False,   # Sem ações automáticas
                'sensitivity_multiplier': 0.1,  # Muito baixa sensibilidade
                'patterns_active': ['spam', 'harassment'],  # Apenas spam/assédio
                'adult_content_allowed': True,
                'sexual_content_allowed': True,
                'drug_references_allowed': True,
                'offensive_language_allowed': True,
                'only_block_patterns': ['spam repetitivo', 'assédio extremo', 'ameaças']
            },
            
            ModerationMode.PERMISSIVE: {
                'enabled': True,
                'description': '🟢 PERMISSIVO - Apenas bloqueia conteúdo extremamente ofensivo',
                'block_severe': False,
                'filter_moderate': False,
                'warn_mild': False,
                'auto_actions': False,
                'sensitivity_multiplier': 0.3,
                'patterns_active': ['extreme_violence', 'harassment'],
                'adult_content_allowed': True,
                'sexual_content_allowed': True,
                'drug_references_allowed': True,
                'offensive_language_allowed': True
            },
            
            ModerationMode.MODERATE: {
                'enabled': True,
                'description': '🟡 MODERADO - Configuração padrão balanceada',
                'block_severe': True,
                'filter_moderate': True,
                'warn_mild': True,
                'auto_actions': True,
                'sensitivity_multiplier': 1.0,
                'patterns_active': ['severe', 'moderate', 'mild'],
                'adult_content_allowed': False,
                'sexual_content_allowed': False,
                'drug_references_allowed': False,
                'offensive_language_allowed': False
            },
            
            ModerationMode.STRICT: {
                'enabled': True,
                'description': '🔴 RESTRITIVO - Bloqueia qualquer conteúdo questionável',
                'block_severe': True,
                'filter_moderate': True,
                'warn_mild': True,
                'auto_actions': True,
                'sensitivity_multiplier': 2.0,
                'patterns_active': ['severe', 'moderate', 'mild', 'suspicious'],
                'adult_content_allowed': False,
                'sexual_content_allowed': False,
                'drug_references_allowed': False,
                'offensive_language_allowed': False
            }
        }
        
        return configs[self.mode]
    
    def is_enabled(self) -> bool:
        """Verifica se moderação está habilitada"""
        return self.config['enabled']
    
    def should_analyze_content(self, content: str) -> bool:
        """Determina se deve analisar o conteúdo"""
        if not self.config['enabled']:
            return False
        
        # Se for adult-friendly, apenas verificar spam/assédio
        if self.mode == ModerationMode.ADULT_FRIENDLY:
            return self._check_only_spam_harassment(content)
        
        return True
    
    def _check_only_spam_harassment(self, content: str) -> bool:
        """Verificação apenas para spam/assédio em modo adult-friendly"""
        content_lower = content.lower()
        
        spam_patterns = [
            'compre agora', 'clique aqui', 'ganhe dinheiro',
            'oferta especial', 'promoção única'
        ]
        
        harassment_patterns = [
            'vou te matar', 'morte para', 'te destruir',
            'ameaça', 'violência física'
        ]
        
        # Verificar spam repetitivo (mesmo conteúdo)
        if len(content) > 100 and content_lower.count(content_lower[:20]) > 3:
            return True
        
        # Verificar padrões específicos
        for pattern in spam_patterns + harassment_patterns:
            if pattern in content_lower:
                return True
        
        return False
    
    def get_status_message(self) -> str:
        """Retorna mensagem de status da configuração"""
        status_msg = f"""
🛡️ **CONFIGURAÇÃO DE MODERAÇÃO**

**Modo Atual:** {self.config['description']}

**Configurações:**
• Moderação: {'✅ Ativa' if self.config['enabled'] else '❌ Desabilitada'}
• Conteúdo adulto: {'✅ Permitido' if self.config.get('adult_content_allowed', False) else '❌ Bloqueado'}
• Conteúdo sexual: {'✅ Permitido' if self.config.get('sexual_content_allowed', False) else '❌ Bloqueado'}  
• Referências a drogas: {'✅ Permitido' if self.config.get('drug_references_allowed', False) else '❌ Bloqueado'}
• Linguagem ofensiva: {'✅ Permitido' if self.config.get('offensive_language_allowed', False) else '❌ Bloqueado'}

**Ações Automáticas:** {'✅ Ativas' if self.config.get('auto_actions', False) else '❌ Desabilitadas'}
"""
        return status_msg.strip()


def get_moderation_config() -> FlexibleModerationConfig:
    """Retorna configuração de moderação atual"""
    return FlexibleModerationConfig()


def set_moderation_mode(mode: str) -> bool:
    """Define modo de moderação (atualiza .env)"""
    try:
        # Validar modo
        ModerationMode(mode.lower())
        
        # Atualizar .env
        env_file = '.env'
        lines = []
        
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        # Procurar e atualizar linha MODERATION_MODE
        mode_updated = False
        for i, line in enumerate(lines):
            if line.startswith('MODERATION_MODE='):
                lines[i] = f'MODERATION_MODE={mode.lower()}\n'
                mode_updated = True
                break
        
        # Adicionar se não existir
        if not mode_updated:
            lines.append(f'MODERATION_MODE={mode.lower()}\n')
        
        # Salvar arquivo
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True
        
    except ValueError:
        print(f"❌ Modo inválido: {mode}")
        print("Modos válidos: disabled, adult_friendly, permissive, moderate, strict")
        return False


def show_all_modes():
    """Mostra todos os modos disponíveis"""
    print("\n🛡️ MODOS DE MODERAÇÃO DISPONÍVEIS:\n")
    
    for mode in ModerationMode:
        config = FlexibleModerationConfig()
        config.mode = mode  
        config.config = config._get_config_for_mode()
        
        print(f"**{mode.value.upper()}**")
        print(f"  {config.config['description']}")
        
        if mode == ModerationMode.DISABLED:
            print("  • Sem nenhuma moderação ou filtro")
            print("  • Permite qualquer tipo de conteúdo")
        elif mode == ModerationMode.ADULT_FRIENDLY:
            print("  • Permite conversas sexualmente explícitas")
            print("  • Permite referências a drogas e linguagem ofensiva") 
            print("  • Bloqueia apenas spam e assédio extremo")
        elif mode == ModerationMode.PERMISSIVE:
            print("  • Muito permissivo, bloqueia apenas conteúdo extremo")
            print("  • Permite conversas adultas")
        elif mode == ModerationMode.MODERATE:
            print("  • Configuração padrão balanceada")
            print("  • Bloqueia conteúdo adulto e ofensivo")
        elif mode == ModerationMode.STRICT:
            print("  • Mais restritivo")
            print("  • Bloqueia qualquer conteúdo questionável")
        
        print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "show":
            show_all_modes()
        elif sys.argv[1] == "set" and len(sys.argv) > 2:
            if set_moderation_mode(sys.argv[2]):
                print(f"✅ Modo alterado para: {sys.argv[2]}")
            else:
                print(f"❌ Erro ao alterar modo")
        elif sys.argv[1] == "status":
            config = get_moderation_config()
            print(config.get_status_message())
    else:
        print("Uso:")
        print("  python flexible_moderation.py show     # Mostrar todos os modos")
        print("  python flexible_moderation.py set MODE # Definir modo")
        print("  python flexible_moderation.py status   # Ver configuração atual")
        print("\nModos: disabled, adult_friendly, permissive, moderate, strict")