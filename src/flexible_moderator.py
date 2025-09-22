"""
Sistema de Moderação Flexível - Eron.IA
========================================

Versão flexível do sistema de moderação que permite conversas adultas
quando configurado no modo apropriado.

Funcionalidades:
- Modo DISABLED: Sem moderação
- Modo ADULT_FRIENDLY: Permite conversas explícitas
- Modo PERMISSIVE: Muito permissivo
- Configuração dinâmica via .env

Autor: Eron.IA System
"""

import sys
import os
from pathlib import Path

# Adicionar diretório pai para imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from src.flexible_moderation import get_moderation_config, ModerationMode
    from src.adult_content_moderator import AdultContentModerator, ContentSeverity, ModerationAction
except ImportError as e:
    print(f"❌ Erro ao importar: {e}")
    sys.exit(1)

class FlexibleModerator(AdultContentModerator):
    """Moderador flexível que respeita configurações permissivas"""
    
    def __init__(self):
        super().__init__()
        self.flex_config = get_moderation_config()
        
        print(f"🛡️ Moderador iniciado em modo: {self.flex_config.mode.value.upper()}")
        print(f"📋 {self.flex_config.config['description']}")
        
        if not self.flex_config.is_enabled():
            print("⚠️ MODERAÇÃO DESABILITADA - Todos os conteúdos serão permitidos")
    
    def analyze_content(self, content: str, user_id: str = None) -> dict:
        """Análise flexível de conteúdo baseada na configuração"""
        
        # Se moderação desabilitada, permitir tudo
        if not self.flex_config.is_enabled():
            return {
                'content_hash': str(hash(content)),
                'severity': ContentSeverity.CLEAN,
                'action': ModerationAction.ALLOW,
                'confidence': 0.0,
                'flagged_words': [],
                'reason': "Moderação desabilitada - conteúdo permitido",
                'timestamp': self._get_timestamp(),
                'user_id': user_id,
                'mode': self.flex_config.mode.value
            }
        
        # Se modo adult-friendly, verificar apenas spam/assédio
        if self.flex_config.mode == ModerationMode.ADULT_FRIENDLY:
            return self._analyze_adult_friendly(content, user_id)
        
        # Se modo permissivo, usar análise relaxada
        if self.flex_config.mode == ModerationMode.PERMISSIVE:
            return self._analyze_permissive(content, user_id)
        
        # Para outros modos, usar análise padrão mas com configurações específicas
        result = super().analyze_content(content, user_id)
        result['mode'] = self.flex_config.mode.value
        
        # Ajustar ação baseada na configuração flexível
        result = self._adjust_action_for_mode(result)
        
        return result
    
    def _analyze_adult_friendly(self, content: str, user_id: str = None) -> dict:
        """Análise para modo adult-friendly - apenas spam/assédio"""
        
        content_lower = content.lower()
        flagged_words = []
        reason = "Conteúdo permitido - modo adult-friendly"
        
        # Verificar apenas spam/assédio extremo
        spam_harassment_patterns = [
            r'\b(spam|compre agora|clique aqui|ganhe dinheiro)\b',
            r'\b(ameaça|vou te matar|morte para|te destruir)\b',
            r'\b(assédio|perseguição|stalking)\b'
        ]
        
        import re
        for pattern in spam_harassment_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                flagged_words.extend(matches)
        
        # Verificar conteúdo repetitivo (spam)
        if len(content) > 50 and len(set(content.split())) < len(content.split()) * 0.3:
            flagged_words.append("conteúdo repetitivo")
        
        # Determinar severidade e ação
        if flagged_words:
            severity = ContentSeverity.MILD
            action = ModerationAction.WARN  # Apenas avisar
            reason = f"Possível spam/assédio detectado: {', '.join(flagged_words[:3])}"
        else:
            severity = ContentSeverity.CLEAN
            action = ModerationAction.ALLOW
        
        return {
            'content_hash': str(hash(content)),
            'severity': severity,
            'action': action,
            'confidence': 0.1 if flagged_words else 0.0,
            'flagged_words': flagged_words[:5],
            'reason': reason,
            'timestamp': self._get_timestamp(),
            'user_id': user_id,
            'mode': 'adult_friendly'
        }
    
    def _analyze_permissive(self, content: str, user_id: str = None) -> dict:
        """Análise permissiva - bloqueia apenas conteúdo extremo"""
        
        # Usar análise padrão mas com sensibilidade muito baixa
        result = super().analyze_content(content, user_id)
        
        # Ajustar para ser mais permissivo
        if result['severity'] == ContentSeverity.MILD:
            result['severity'] = ContentSeverity.CLEAN
            result['action'] = ModerationAction.ALLOW
            result['reason'] = "Conteúdo permitido - modo permissivo"
        
        elif result['severity'] == ContentSeverity.MODERATE:
            # Em modo permissivo, moderate vira apenas um aviso
            result['action'] = ModerationAction.FILTER  # Apenas filtrar, não bloquear
        
        # Apenas conteúdo SEVERE é realmente bloqueado
        result['mode'] = 'permissive'
        return result
    
    def _adjust_action_for_mode(self, result: dict) -> dict:
        """Ajusta ação baseada no modo de moderação"""
        
        mode = self.flex_config.mode
        config = self.flex_config.config
        
        # Se ações automáticas desabilitadas, apenas permitir ou filtrar
        if not config.get('auto_actions', True):
            if result['action'] in [ModerationAction.QUARANTINE, ModerationAction.BLOCK, ModerationAction.BAN]:
                result['action'] = ModerationAction.FILTER
                result['reason'] += " (ação automática desabilitada)"
        
        # Aplicar configurações específicas do modo
        severity = result['severity']
        
        if severity == ContentSeverity.SEVERE and not config.get('block_severe', True):
            result['action'] = ModerationAction.WARN
            result['reason'] += " (bloqueio severo desabilitado)"
        
        elif severity == ContentSeverity.MODERATE and not config.get('filter_moderate', True):
            result['action'] = ModerationAction.ALLOW
            result['reason'] = "Conteúdo permitido - filtro moderado desabilitado"
        
        elif severity == ContentSeverity.MILD and not config.get('warn_mild', True):
            result['action'] = ModerationAction.ALLOW
            result['reason'] = "Conteúdo permitido - aviso leve desabilitado"
        
        return result
    
    def _get_timestamp(self):
        """Obter timestamp atual"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_config_status(self) -> str:
        """Retorna status da configuração"""
        return self.flex_config.get_status_message()


def test_flexible_moderation():
    """Testar moderação flexível com diferentes conteúdos"""
    
    print("🧪 TESTE DE MODERAÇÃO FLEXÍVEL\n")
    
    moderator = FlexibleModerator()
    
    # Conteúdos de teste
    test_contents = [
        "Olá, como você está hoje?",
        "Vamos conversar sobre sexo?",
        "Quero fazer sexo com você",
        "Pornografia explícita aqui",
        "Drogas e maconha são legais",
        "Você é um idiota!",
        "Compre agora! Oferta especial! Clique aqui!",
        "Vou te matar, ameaça de morte",
    ]
    
    print(f"Configuração atual:")
    print(moderator.get_config_status())
    print("\n" + "="*60)
    
    for i, content in enumerate(test_contents, 1):
        result = moderator.analyze_content(content, f"test_user_{i}")
        
        action_emoji = {
            ModerationAction.ALLOW: "✅",
            ModerationAction.FILTER: "🔄", 
            ModerationAction.WARN: "⚠️",
            ModerationAction.QUARANTINE: "🔒",
            ModerationAction.BLOCK: "🚫",
            ModerationAction.BAN: "❌"
        }
        
        emoji = action_emoji.get(result['action'], "❓")
        
        print(f"\n{i}. \"{content}\"")
        print(f"   {emoji} {result['severity'].name} → {result['action'].name}")
        print(f"   💬 {result['reason']}")
        
        if result['flagged_words']:
            print(f"   🏷️ Flagged: {', '.join(result['flagged_words'])}")


if __name__ == "__main__":
    # Permitir configuração via argumentos
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_flexible_moderation()
        elif sys.argv[1] == "config":
            moderator = FlexibleModerator()
            print(moderator.get_config_status())
        else:
            print("Comandos disponíveis:")
            print("  python flexible_moderator.py test    # Testar com diferentes conteúdos")
            print("  python flexible_moderator.py config  # Ver configuração atual")
    else:
        # Teste básico
        test_flexible_moderation()