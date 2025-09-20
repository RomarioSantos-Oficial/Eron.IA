"""
Módulo de Aprendizado - Sistema Completo de IA Adaptativa
Componentes especializados para aprendizado e otimização
"""

from .fast_learning import FastLearning
from .pattern_recognition import PatternRecognitionSystem
from .response_optimizer import ResponseOptimizer
from .feedback_system import FeedbackSystem  
from .adaptation_system import AdaptationSystem

__all__ = [
    'FastLearning',
    'PatternRecognitionSystem', 
    'ResponseOptimizer',
    'FeedbackSystem',
    'AdaptationSystem'
]

# Versão do módulo
__version__ = '1.0.0'

# Configurações padrão
DEFAULT_CONFIG = {
    'learning_rate': 0.1,
    'adaptation_threshold': 0.6,
    'pattern_min_samples': 5,
    'feedback_retention_days': 90,
    'optimization_interval_hours': 24
}