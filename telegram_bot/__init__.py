"""
Telegram Bot - Sistema Completo de Bot
Módulo principal do bot Telegram
"""

# Importações do sistema principal funcional
from .telegram_bot_original import (
    get_adult_personality_context,
    is_advanced_adult_active,
    get_personality_instructions_for_llm,
    format_adult_response_with_personality,
    get_adult_system_status_summary
)

__all__ = [
    'get_adult_personality_context',
    'is_advanced_adult_active', 
    'get_personality_instructions_for_llm',
    'format_adult_response_with_personality',
    'get_adult_system_status_summary'
]
