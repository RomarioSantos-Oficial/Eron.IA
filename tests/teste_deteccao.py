#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def test_bot_name_detection(message):
    """Testa se detecta nome do bot corretamente"""
    patterns = [
        r"quero que se chame (\w+)",
        r"seu nome seja (\w+)",
        r"te chamar de (\w+)",
        r"se chame (\w+)"
    ]
    
    message_lower = message.lower().strip()
    
    for pattern in patterns:
        match = re.search(pattern, message_lower)
        if match:
            return match.group(1).capitalize()
    
    return None

# Teste com sua mensagem
test_message = "Meu nome é Romario, quero que se chame Mariana"
detected_name = test_bot_name_detection(test_message)

print(f"🧪 TESTE DE DETECÇÃO:")
print(f"Mensagem: '{test_message}'")
print(f"Nome detectado: {detected_name}")

if detected_name:
    print("✅ Sistema detectou corretamente!")
else:
    print("❌ Sistema NÃO detectou o nome")
