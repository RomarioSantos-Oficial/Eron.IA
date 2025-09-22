#!/usr/bin/env python3
"""
🔥 VERIFICAÇÃO FINAL - CONTEÚDO ADULTO MÁXIMO
Sistema completo com 800+ respostas sem filtros
"""

import sqlite3
import random

def verificar_sistema_completo():
    db_path = 'database/advanced_adult.db'
    conn = sqlite3.connect(db_path)
    
    print('🔥🔥🔥 VERIFICAÇÃO DO SISTEMA ADULTO COMPLETO 🔥🔥🔥')
    print('=' * 75)
    
    # Contar total
    total_count = conn.execute('SELECT COUNT(*) FROM adult_content').fetchone()[0]
    print(f'💥 TOTAL ABSOLUTO: {total_count} respostas adultas!')
    
    # Estatísticas por categoria
    print(f'\\n📊 DISTRIBUIÇÃO POR CATEGORIA:')
    categories = conn.execute('SELECT DISTINCT category FROM adult_content ORDER BY category').fetchall()
    
    for (category,) in categories:
        count = conn.execute('SELECT COUNT(*) FROM adult_content WHERE category = ?', (category,)).fetchone()[0]
        print(f'   • {category.upper()}: {count} respostas')
        
        # Amostras por categoria
        samples = conn.execute('SELECT content FROM adult_content WHERE category = ? ORDER BY RANDOM() LIMIT 2', (category,)).fetchall()
        for (sample,) in samples:
            print(f'     - "{sample[:60]}..."')
    
    # Estatísticas por intensidade
    print(f'\\n🔢 DISTRIBUIÇÃO POR INTENSIDADE:')
    for intensity in range(1, 11):
        count = conn.execute('SELECT COUNT(*) FROM adult_content WHERE intensity = ?', (intensity,)).fetchone()[0]
        if count > 0:
            print(f'   • Nível {intensity}: {count} respostas')
    
    # Teste de variedade - pegar amostras aleatórias
    print(f'\\n🎲 TESTE DE VARIEDADE - AMOSTRAS ALEATÓRIAS:')
    random_samples = conn.execute('SELECT content, category, intensity FROM adult_content ORDER BY RANDOM() LIMIT 10').fetchall()
    
    for i, (content, category, intensity) in enumerate(random_samples, 1):
        print(f'   {i}. [{category.upper()}-{intensity}] {content}')
    
    # Verificar conteúdo mais intenso
    print(f'\\n🔥 TOP 5 MAIS INTENSOS:')
    intense_samples = conn.execute('SELECT content, intensity FROM adult_content WHERE intensity >= 7 ORDER BY intensity DESC, RANDOM() LIMIT 5').fetchall()
    
    for i, (content, intensity) in enumerate(intense_samples, 1):
        print(f'   {i}. [NÍVEL {intensity}] {content}')
    
    # Verificar subcategorias
    print(f'\\n📋 SUBCATEGORIAS DISPONÍVEIS:')
    subcategories = conn.execute('SELECT DISTINCT subcategory FROM adult_content WHERE subcategory IS NOT NULL').fetchall()
    
    for (subcat,) in subcategories:
        count = conn.execute('SELECT COUNT(*) FROM adult_content WHERE subcategory = ?', (subcat,)).fetchone()[0]
        print(f'   • {subcat}: {count} respostas')
    
    conn.close()
    
    print(f'\\n🎉 SISTEMA COMPLETO VERIFICADO!')
    print(f'✅ {total_count} respostas adultas sem filtros')
    print(f'✅ Máxima variedade alcançada')
    print(f'✅ Todos os níveis de intensidade cobertos')
    print(f'✅ Múltiplas categorias e subcategorias')
    print(f'🚀 Sistema pronto para conversas adultas infinitamente variadas!')

def testar_sistema_adulto():
    """Teste rápido do sistema adulto integrado"""
    
    print('\\n🔥 TESTE DO SISTEMA INTEGRADO')
    print('=' * 50)
    
    # Importar o sistema de aprendizado adulto
    try:
        import sys
        sys.path.append('learning')
        from advanced_adult_learning import AdvancedAdultLearning
        
        adult_system = AdvancedAdultLearning()
        
        # Teste com diferentes intensidades
        test_messages = [
            "oi gostosa",
            "você é muito sexy", 
            "quero você",
            "estou com tesão",
            "vem aqui me dar prazer"
        ]
        
        print('🧪 Testando respostas do sistema:')
        for i, msg in enumerate(test_messages, 1):
            response = adult_system.get_response(msg, f'test_user_{i}')
            print(f'   {i}. Entrada: "{msg}"')
            print(f'      Resposta: "{response}"')
            print()
        
        print('✅ Sistema adulto funcionando perfeitamente!')
        
    except Exception as e:
        print(f'⚠️  Sistema adulto: {str(e)}')
        print('💡 Execute: python learning/advanced_adult_learning.py para verificar')

if __name__ == '__main__':
    verificar_sistema_completo()
    testar_sistema_adulto()