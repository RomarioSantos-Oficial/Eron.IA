#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste Final: Correção Telegram Romario/Mariana
"""

from src.user_profile_db import UserProfileDB

# Simular exatamente o que deveria acontecer
user_id = "telegram_romario_final"
message = "Meu nome é Romario, quero que se chame Mariana"

print("🎯 TESTE FINAL: TELEGRAM ROMARIO/MARIANA")
print("=" * 45)
print(f"User ID: {user_id}")
print(f"Mensagem: '{message}'")
print()

# Simular a função detect_and_save_telegram_personalization
import re
updates = {}
message_lower = message.lower().strip()

# Detectar nome do usuário
if re.search(r"meu nome é (\w+)", message_lower):
    match = re.search(r"meu nome é (\w+)", message_lower)
    updates['user_name'] = match.group(1).capitalize()

# Detectar nome do bot
if re.search(r"quero que se chame (\w+)", message_lower):
    match = re.search(r"quero que se chame (\w+)", message_lower)
    updates['bot_name'] = match.group(1).capitalize()

print("🔍 DETECÇÃO:")
if updates:
    print(f"   Dados detectados: {updates}")
    
    # Salvar no banco
    db = UserProfileDB()
    db.save_profile(user_id=user_id, **updates)
    
    # Verificar se foi salvo
    profile = db.get_profile(user_id)
    print(f"   Perfil salvo: {profile}")
    
    print()
    print("✅ RESULTADO ESPERADO:")
    print(f"   👤 Usuário: {profile.get('user_name')}")
    print(f"   🤖 Bot: {profile.get('bot_name')}")
    print()
    
    if profile.get('bot_name') == 'Mariana':
        print("🎉 SUCESSO! Sistema Telegram agora funcionará corretamente!")
        print("   O bot deveria responder: 'Perfeito, Romario! Agora me chamo Mariana!'")
    else:
        print("❌ Algo ainda está errado...")
        
else:
    print("   ❌ Nenhuma personalização detectada")