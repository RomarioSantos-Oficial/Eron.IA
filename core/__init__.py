"""
Core - Componentes Centrais Compartilhados
Conexões de banco, modelos e serviços base
"""

from .database import DatabaseManager, get_db_connection
from .models import UserProfile, EmotionData, ConversationContext
from .services import ConfigService, SecurityService, LoggingService

__all__ = [
    'DatabaseManager',
    'get_db_connection', 
    'UserProfile',
    'EmotionData',
    'ConversationContext',
    'ConfigService',
    'SecurityService',
    'LoggingService'
]
