#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verificador de Perfis do Telegram
"""

import sqlite3
import os

# Conectar ao banco
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'memoria', 'user_profiles.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🔍 PERFIS DO TELEGRAM NO BANCO DE DADOS:")
print("=" * 50)

# Buscar perfis do Telegram
cursor.execute("SELECT user_id, user_name, bot_name, bot_personality FROM profiles WHERE user_id LIKE 'telegram_%' OR user_id LIKE 'test_%'")
results = cursor.fetchall()

if results:
    for row in results:
        user_id, user_name, bot_name, personality = row
        print(f"📱 ID: {user_id}")
        print(f"   👤 Usuário: {user_name or 'Não definido'}")
        print(f"   🤖 Bot: {bot_name or 'ERON (padrão)'}")
        print(f"   ✨ Personalidade: {personality or 'Não definida'}")
        print()
else:
    print("❌ Nenhum perfil do Telegram encontrado")

conn.close()

print("✅ Verificação concluída!")