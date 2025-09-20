"""
Modelos de Dados Centrais
Classes para representar estruturas de dados compartilhadas
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List, Any
import json

@dataclass
class UserProfile:
    """Perfil completo do usuário"""
    user_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    platform: str = 'web'
    preferences: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_active is None:
            self.last_active = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'platform': self.platform,
            'preferences': json.dumps(self.preferences) if self.preferences else '{}',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Criar instância a partir de dicionário"""
        return cls(
            user_id=data['user_id'],
            name=data.get('name'),
            email=data.get('email'),
            platform=data.get('platform', 'web'),
            preferences=json.loads(data.get('preferences', '{}')) if data.get('preferences') else {},
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            last_active=datetime.fromisoformat(data['last_active']) if data.get('last_active') else None,
            is_active=data.get('is_active', True)
        )
    
    def update_last_active(self):
        """Atualizar último acesso"""
        self.last_active = datetime.now()
    
    def set_preference(self, key: str, value: Any):
        """Definir preferência específica"""
        if self.preferences is None:
            self.preferences = {}
        self.preferences[key] = value
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Obter preferência específica"""
        if self.preferences is None:
            return default
        return self.preferences.get(key, default)

@dataclass
class EmotionData:
    """Dados emocionais do usuário"""
    user_id: str
    emotion_type: str
    intensity: float
    context: Optional[str] = None
    triggers: Optional[List[str]] = None
    timestamp: Optional[datetime] = None
    platform: str = 'web'
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.triggers is None:
            self.triggers = []
        
        # Validar intensidade
        self.intensity = max(0.0, min(1.0, self.intensity))
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'user_id': self.user_id,
            'emotion_type': self.emotion_type,
            'intensity': self.intensity,
            'context': self.context,
            'triggers': json.dumps(self.triggers) if self.triggers else '[]',
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'platform': self.platform
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionData':
        """Criar instância a partir de dicionário"""
        return cls(
            user_id=data['user_id'],
            emotion_type=data['emotion_type'],
            intensity=float(data['intensity']),
            context=data.get('context'),
            triggers=json.loads(data.get('triggers', '[]')) if data.get('triggers') else [],
            timestamp=datetime.fromisoformat(data['timestamp']) if data.get('timestamp') else None,
            platform=data.get('platform', 'web')
        )
    
    def add_trigger(self, trigger: str):
        """Adicionar trigger emocional"""
        if self.triggers is None:
            self.triggers = []
        if trigger not in self.triggers:
            self.triggers.append(trigger)
    
    def is_intense(self, threshold: float = 0.7) -> bool:
        """Verificar se emoção é intensa"""
        return self.intensity >= threshold
    
    def is_positive(self) -> bool:
        """Verificar se emoção é positiva"""
        positive_emotions = ['alegria', 'felicidade', 'entusiasmo', 'satisfacao', 'amor']
        return self.emotion_type.lower() in positive_emotions
    
    def is_negative(self) -> bool:
        """Verificar se emoção é negativa"""
        negative_emotions = ['tristeza', 'raiva', 'medo', 'ansiedade', 'frustracao']
        return self.emotion_type.lower() in negative_emotions

@dataclass 
class ConversationContext:
    """Contexto de conversação"""
    user_id: str
    conversation_id: Optional[str] = None
    topic: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = None
    emotion_state: Optional[EmotionData] = None
    preferences_applied: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    platform: str = 'web'
    
    def __post_init__(self):
        if self.messages is None:
            self.messages = []
        if self.started_at is None:
            self.started_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.preferences_applied is None:
            self.preferences_applied = {}
        if self.conversation_id is None:
            # Gerar ID baseado em timestamp e user_id
            timestamp = int(self.started_at.timestamp())
            self.conversation_id = f"{self.user_id}_{timestamp}"
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Adicionar mensagem ao contexto"""
        message = {
            'role': role,  # 'user' ou 'assistant'
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_recent_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obter mensagens recentes"""
        return self.messages[-limit:] if self.messages else []
    
    def update_topic(self, new_topic: str):
        """Atualizar tópico da conversa"""
        self.topic = new_topic
        self.updated_at = datetime.now()
    
    def update_emotion_state(self, emotion: EmotionData):
        """Atualizar estado emocional"""
        self.emotion_state = emotion
        self.updated_at = datetime.now()
    
    def apply_preference(self, key: str, value: Any):
        """Aplicar preferência específica"""
        if self.preferences_applied is None:
            self.preferences_applied = {}
        self.preferences_applied[key] = value
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'user_id': self.user_id,
            'conversation_id': self.conversation_id,
            'topic': self.topic,
            'messages': json.dumps(self.messages) if self.messages else '[]',
            'emotion_state': self.emotion_state.to_dict() if self.emotion_state else None,
            'preferences_applied': json.dumps(self.preferences_applied) if self.preferences_applied else '{}',
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'platform': self.platform
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """Criar instância a partir de dicionário"""
        emotion_state = None
        if data.get('emotion_state'):
            emotion_state = EmotionData.from_dict(data['emotion_state'])
        
        return cls(
            user_id=data['user_id'],
            conversation_id=data.get('conversation_id'),
            topic=data.get('topic'),
            messages=json.loads(data.get('messages', '[]')) if data.get('messages') else [],
            emotion_state=emotion_state,
            preferences_applied=json.loads(data.get('preferences_applied', '{}')) if data.get('preferences_applied') else {},
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
            platform=data.get('platform', 'web')
        )
    
    def get_conversation_duration(self) -> float:
        """Obter duração da conversa em minutos"""
        if not self.started_at or not self.updated_at:
            return 0.0
        
        duration = self.updated_at - self.started_at
        return duration.total_seconds() / 60.0
    
    def get_message_count(self) -> int:
        """Obter número de mensagens"""
        return len(self.messages) if self.messages else 0
    
    def is_active(self, timeout_minutes: int = 30) -> bool:
        """Verificar se conversa está ativa"""
        if not self.updated_at:
            return False
        
        time_diff = datetime.now() - self.updated_at
        return time_diff.total_seconds() < (timeout_minutes * 60)

@dataclass
class LearningPattern:
    """Padrão de aprendizado identificado"""
    pattern_id: str
    user_id: str
    pattern_type: str
    pattern_data: Dict[str, Any]
    confidence_score: float
    sample_size: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        
        # Validar confidence score
        self.confidence_score = max(0.0, min(1.0, self.confidence_score))
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'pattern_id': self.pattern_id,
            'user_id': self.user_id,
            'pattern_type': self.pattern_type,
            'pattern_data': json.dumps(self.pattern_data) if self.pattern_data else '{}',
            'confidence_score': self.confidence_score,
            'sample_size': self.sample_size,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningPattern':
        """Criar instância a partir de dicionário"""
        return cls(
            pattern_id=data['pattern_id'],
            user_id=data['user_id'],
            pattern_type=data['pattern_type'],
            pattern_data=json.loads(data.get('pattern_data', '{}')) if data.get('pattern_data') else {},
            confidence_score=float(data['confidence_score']),
            sample_size=int(data['sample_size']),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
    
    def update_confidence(self, new_evidence_score: float, weight: float = 0.1):
        """Atualizar confiança com nova evidência"""
        # Média ponderada
        self.confidence_score = (
            self.confidence_score * (1 - weight) + 
            new_evidence_score * weight
        )
        self.confidence_score = max(0.0, min(1.0, self.confidence_score))
        self.updated_at = datetime.now()
    
    def increment_sample_size(self):
        """Incrementar tamanho da amostra"""
        self.sample_size += 1
        self.updated_at = datetime.now()
    
    def is_reliable(self, min_confidence: float = 0.7, min_samples: int = 5) -> bool:
        """Verificar se padrão é confiável"""
        return (
            self.confidence_score >= min_confidence and 
            self.sample_size >= min_samples
        )