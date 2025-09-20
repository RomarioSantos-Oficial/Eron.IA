#!/usr/bin/env python3
"""
Script para debug do problema de personalização no Telegram
"""

import logging
import sys
import os

# Configurar logging para debug
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

# Teste simples de callback
def test_callback():
    print("=== TESTE DE DEBUG ===")
    
    # Testar se as funções existem
    try:
        from telegram_bot import handle_personality_selection
        print("✅ handle_personality_selection encontrada")
    except ImportError as e:
        print(f"❌ Erro importando handle_personality_selection: {e}")
    
    # Testar padrões de callback
    patterns = [
        'personality_amigável',
        'personality_formal', 
        'personality_casual',
        'personality_divertido'
    ]
    
    for pattern in patterns:
        print(f"Testando padrão: {pattern}")
        if pattern.startswith('personality_'):
            key = pattern.replace('personality_', '')
            print(f"  Chave extraída: '{key}'")

if __name__ == "__main__":
    test_callback()