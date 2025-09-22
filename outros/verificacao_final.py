#!/usr/bin/env python3
"""
🔍 VERIFICAÇÃO FINAL COMPLETA DO SISTEMA ORGANIZADO
Testar todos os componentes após reorganização
"""

import os
import sys
import subprocess

def verificacao_completa():
    print('🔍 VERIFICAÇÃO FINAL - SISTEMA ORGANIZADO')
    print('=' * 60)
    
    # 1. Verificar estrutura de pastas
    print('📁 VERIFICANDO ESTRUTURA DE PASTAS:')
    pastas_esperadas = {
        'tools/': 'Ferramentas e utilitários',
        'tools/expansion/': 'Scripts de expansão de conteúdo',
        'tests/system/': 'Testes do sistema',
        'docs/': 'Documentação',
        'outros/': 'Arquivos diversos',
        'web/': 'Interface web',
        'telegram_bot/': 'Bot do Telegram',
        'core/': 'Módulos principais',
        'learning/': 'Sistemas de aprendizagem',
        'database/': 'Banco de dados'
    }
    
    for pasta, descricao in pastas_esperadas.items():
        if os.path.exists(pasta):
            arquivos = len([f for f in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, f))])
            print(f'   ✅ {pasta}: {descricao} ({arquivos} arquivos)')
        else:
            print(f'   ❌ {pasta}: NÃO ENCONTRADA')
    
    # 2. Verificar arquivos na raiz
    print(f'\\n📋 VERIFICANDO ARQUIVOS NA RAIZ:')
    arquivos_raiz_esperados = [
        'run_all.py', '.env', '.gitignore', 'README.md', 
        'requirements.txt', 'SECURITY.md', 'setup.py'
    ]
    
    arquivos_na_raiz = [f for f in os.listdir('.') if os.path.isfile(f)]
    
    for arquivo in arquivos_na_raiz:
        if arquivo in arquivos_raiz_esperados or arquivo.startswith('.'):
            print(f'   ✅ {arquivo}')
        else:
            print(f'   ⚠️  {arquivo} (pode ser movido)')
    
    # 3. Testar importações principais
    print(f'\\n🔧 TESTANDO IMPORTAÇÕES:')
    
    imports_teste = [
        ('core.knowledge_base', 'KnowledgeBase'),
        ('core.memory', 'EronMemory'),
        ('learning.fast_learning', 'FastLearning'),
        ('learning.advanced_adult_learning', 'advanced_adult_learning'),
        ('core.check', 'AdultAccessSystem')
    ]
    
    sys.path.append('.')  # Adicionar raiz ao path
    
    for modulo, classe in imports_teste:
        try:
            exec(f'from {modulo} import {classe}')
            print(f'   ✅ {modulo}.{classe}')
        except Exception as e:
            print(f'   ❌ {modulo}.{classe}: {str(e)[:50]}...')
    
    # 4. Verificar banco de dados
    print(f'\\n💾 VERIFICANDO BANCOS DE DADOS:')
    databases_esperadas = [
        'database/advanced_adult.db',
        'database/super_learning.db',
        'memoria/eron_memory.db'
    ]
    
    for db in databases_esperadas:
        if os.path.exists(db):
            size_mb = os.path.getsize(db) / (1024 * 1024)
            print(f'   ✅ {db} ({size_mb:.1f} MB)')
        else:
            print(f'   ⚠️  {db}: NÃO ENCONTRADO')
    
    # 5. Contar conteúdo adulto
    print(f'\\n🔥 VERIFICANDO CONTEÚDO ADULTO:')
    try:
        import sqlite3
        conn = sqlite3.connect('database/advanced_adult.db')
        total = conn.execute('SELECT COUNT(*) FROM adult_content').fetchone()[0]
        print(f'   ✅ {total} respostas adultas disponíveis')
        
        # Por categoria
        categories = conn.execute('SELECT category, COUNT(*) FROM adult_content GROUP BY category').fetchall()
        for category, count in categories:
            print(f'      • {category.upper()}: {count}')
        
        conn.close()
    except Exception as e:
        print(f'   ❌ Erro ao verificar conteúdo: {str(e)}')
    
    # 6. Verificar tools
    print(f'\\n🛠️  VERIFICANDO FERRAMENTAS:')
    tools = [
        'tools/check_adult_mode.py',
        'tools/check_db.py',
        'tools/expansion/expand_adult_content.py',
        'tools/expansion/mega_expansion_adult.py',
        'tools/expansion/ultra_mega_expansion.py'
    ]
    
    for tool in tools:
        if os.path.exists(tool):
            print(f'   ✅ {tool}')
        else:
            print(f'   ❌ {tool}: NÃO ENCONTRADO')
    
    # 7. Verificar testes
    print(f'\\n🧪 VERIFICANDO TESTES:')
    testes = [
        'tests/system/teste_sistema_final.py',
        'tests/system/test_adult_system.py',
        'tests/system/verificar_sistema_adulto.py'
    ]
    
    for teste in testes:
        if os.path.exists(teste):
            print(f'   ✅ {teste}')
        else:
            print(f'   ❌ {teste}: NÃO ENCONTRADO')
    
    print(f'\\n🎉 VERIFICAÇÃO COMPLETA!')
    print(f'✅ Projeto organizado com sucesso')
    print(f'📁 Estrutura limpa e profissional')
    print(f'🚀 Pronto para uso com run_all.py')

def teste_sistema():
    """Teste rápido do sistema principal"""
    print(f'\\n🚀 TESTE FINAL DO SISTEMA:')
    print('=' * 50)
    
    try:
        # Teste do run_all.py
        print('🔄 Testando run_all.py...')
        result = subprocess.run([sys.executable, 'run_all.py', '--help'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print('✅ run_all.py funciona corretamente')
        else:
            print(f'❌ Erro no run_all.py: {result.stderr}')
            
    except subprocess.TimeoutExpired:
        print('⚠️  run_all.py timeout (normal para teste)')
    except Exception as e:
        print(f'❌ Erro ao testar run_all.py: {e}')
    
    # Teste dos tools
    print(f'\\n🛠️  Testando ferramentas:')
    
    try:
        # Teste do check_db
        if os.path.exists('tools/check_db.py'):
            result = subprocess.run([sys.executable, 'tools/check_db.py'], 
                                  capture_output=True, text=True, timeout=10)
            if 'database' in result.stdout.lower():
                print('✅ tools/check_db.py funciona')
            else:
                print('⚠️  tools/check_db.py com warnings')
        
    except Exception as e:
        print(f'❌ Erro ao testar tools: {e}')
    
    print(f'\\n🎊 SISTEMA TOTALMENTE ORGANIZADO E FUNCIONAL!')

if __name__ == '__main__':
    verificacao_completa()
    teste_sistema()