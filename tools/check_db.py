#!/usr/bin/env python3
"""
Script para verificar estrutura do banco de dados
"""

import sqlite3

# Conectar ao banco
conn = sqlite3.connect('memoria/eron_memory.db')

print("📊 ANÁLISE DO BANCO DE DADOS")
print("=" * 50)

# Listar todas as tabelas
print("🗂️ TABELAS DISPONÍVEIS:")
tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
for table in tables:
    print(f"   • {table}")

print(f"\n🔍 ESTRUTURA DA TABELA adult_content:")
try:
    columns = conn.execute("PRAGMA table_info(adult_content)").fetchall()
    for col in columns:
        print(f"   • {col[1]} ({col[2]})")
    
    # Contar registros
    count = conn.execute("SELECT COUNT(*) FROM adult_content").fetchone()[0]
    print(f"\n📈 TOTAL DE REGISTROS: {count}")
    
    # Mostrar alguns exemplos
    if count > 0:
        print("\n🎯 EXEMPLOS DE CONTEÚDO:")
        samples = conn.execute("SELECT category, content, intensity FROM adult_content LIMIT 3").fetchall()
        for sample in samples:
            print(f"   • {sample[0]}: {sample[1][:50]}... (Intensidade: {sample[2]})")
            
except Exception as e:
    print(f"❌ Erro: {e}")

conn.close()
print("\n✅ Verificação completa!")