#!/usr/bin/env python3
"""
Script para encontrar o banco correto
"""

import sqlite3
import os

print('🔍 PROCURANDO ARQUIVOS DE BANCO:')
for file in os.listdir('memoria'):
    if file.endswith('.db'):
        print(f'   • {file}')
        
# Verificar o banco correto
try:
    conn = sqlite3.connect('memoria/advanced_adult.db')
    print('\n📊 BANCO advanced_adult.db:')
    tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    for table in tables:
        print(f'   • Tabela: {table}')
        count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
        print(f'     Registros: {count}')
        
        # Mostrar estrutura da tabela adult_content
        if table == 'adult_content':
            print(f'     Colunas:')
            columns = conn.execute(f"PRAGMA table_info({table})").fetchall()
            for col in columns:
                print(f'       - {col[1]} ({col[2]})')
    conn.close()
except Exception as e:
    print(f'❌ Erro: {e}')

print('\n✅ Análise completa!')