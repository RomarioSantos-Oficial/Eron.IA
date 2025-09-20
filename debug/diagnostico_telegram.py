#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Diagnóstico: Por que o Telegram ainda não funciona?
"""

import sqlite3
import os

# Conectar ao banco
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'memoria', 'user_profiles.db')

print("🔍 DIAGNÓSTICO: POR QUE O TELEGRAM AINDA NÃO FUNCIONA?")
print("=" * 55)

# Verificar perfis recentes
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n📊 ÚLTIMOS PERFIS SALVOS:")
cursor.execute("SELECT user_id, user_name, bot_name, rowid FROM profiles ORDER BY rowid DESC LIMIT 5")
results = cursor.fetchall()

for i, row in enumerate(results, 1):
    user_id, user_name, bot_name, rowid = row
    print(f"{i}. ID: {user_id} | Usuário: {user_name or 'None'} | Bot: {bot_name or 'None'} | Row: {rowid}")

# Verificar se há perfis específicos do teste
print("\n🔍 PERFIS DE TESTE CRIADOS:")
cursor.execute("SELECT user_id, user_name, bot_name FROM profiles WHERE user_id LIKE '%test%' OR user_id LIKE '%romario%' OR bot_name = 'Mariana'")
test_results = cursor.fetchall()

if test_results:
    for row in test_results:
        print(f"   ✅ {row[0]} | {row[1]} | {row[2]}")
else:
    print("   ❌ Nenhum perfil de teste encontrado")

conn.close()

print("\n🤔 POSSÍVEIS CAUSAS:")
print("1. Bot não está usando a versão corrigida do código")
print("2. Bot precisa ser reiniciado para carregar mudanças")
print("3. Seu user_id real não está sendo detectado corretamente")
print("4. Cache ou sessão antiga do Telegram")

print("\n✅ SOLUÇÕES:")
print("1. Parar e reiniciar o bot completamente")
print("2. Limpar cache do Telegram (/start novamente)")
print("3. Verificar logs do bot em execução")