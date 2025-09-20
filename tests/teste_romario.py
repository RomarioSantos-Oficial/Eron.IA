#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste da Personalização: Caso Romario/Mariana
"""

from src.user_profile_db import UserProfileDB
import re

def detect_and_save_personalization_test(user_message, user_id):
    """Cópia da função para teste"""
    user_profile_db = UserProfileDB()
    
    if not user_message or not user_id:
        return False
    
    message_lower = user_message.lower().strip()
    updates = {}
    
    # Detectar nome do usuário
    name_patterns = [
        r"meu nome é (\w+)",
        r"me chamo (\w+)", 
        r"sou (\w+)",
        r"pode me chamar de (\w+)",
        r"^(\w+)$"  # Resposta de uma palavra apenas
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, message_lower)
        if match:
            name = match.group(1).capitalize()
            if len(name) > 1 and name not in ['não', 'sim', 'ok', 'obrigado', 'obrigada']:
                updates['user_name'] = name
                break
    
    # Detectar nome do assistente 
    bot_name_patterns = [
        r"se chame (\w+)",
        r"seu nome seja (\w+)",
        r"te chamar de (\w+)",
        r"quero que se chame (\w+)"
    ]
    
    for pattern in bot_name_patterns:
        match = re.search(pattern, message_lower)
        if match:
            bot_name = match.group(1).capitalize()
            if len(bot_name) > 1:
                updates['bot_name'] = bot_name
                break
    
    # Se encontrou informações para salvar
    if updates:
        try:
            print(f"[DEBUG] Salvando automaticamente: {updates}")
            user_profile_db.save_profile(user_id=user_id, **updates)
            return True
        except Exception as e:
            print(f"[DEBUG] Erro ao salvar personalização: {e}")
            return False
    
    return False

# Teste com a mensagem exata do usuário
print("🧪 TESTE COMPLETO: CASO ROMARIO/MARIANA")
print("=" * 50)

test_user_id = "test_romario_123"
test_message = "Meu nome é Romario, quero que se chame Mariana"

print(f"Usuário: {test_user_id}")
print(f"Mensagem: '{test_message}'")
print()

# 1. Executar detecção
result = detect_and_save_personalization_test(test_message, test_user_id)
print(f"Detecção realizada: {result}")
print()

# 2. Verificar o que foi salvo
db = UserProfileDB()
profile = db.get_profile(test_user_id)

if profile:
    print("✅ DADOS SALVOS:")
    print(f"   👤 Nome do usuário: {profile.get('user_name')}")
    print(f"   🤖 Nome do bot: {profile.get('bot_name')}")
else:
    print("❌ NENHUM DADO SALVO")

print()
print("🎯 CONCLUSÃO:")
if profile and profile.get('bot_name') == 'Mariana':
    print("✅ Sistema funcionou! Bot deveria se chamar Mariana")
else:
    print("❌ Problema detectado! Investigar mais...")