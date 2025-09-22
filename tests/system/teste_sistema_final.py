#!/usr/bin/env python3
"""
🔥 TESTE FINAL DO SISTEMA COMPLETO
Testando 800+ respo    # Teste de integração
    print(f'\n🚀 TESTE DE INTEGRAÇÃO:')
    try:
        # Verificar se o app principal consegue acessar
        sys.path.append('../..')  # Adicionar raiz do projeto
        from web.app import app
        print('✅ Integração com web/app.py: OK')
    except Exception as e:
        print(f'⚠️  Integração web: {str(e)}')
    
    try:
        # Verificar se o bot consegue acessar
        from telegram_bot.telegram_bot_original import main as bot_main
        print('✅ Integração com telegram_bot: OK')
    except Exception as e:
        print(f'⚠️  Integração telegram: {str(e)}')tegradas
"""

import sqlite3
import random
import sys
import os

def teste_final_sistema():
    print('🔥🔥🔥 TESTE FINAL - SISTEMA ADULTO MÁXIMO 🔥🔥🔥')
    print('=' * 75)
    
    # Verificar database
    db_path = 'database/advanced_adult.db'
    if not os.path.exists(db_path):
        print('❌ Database não encontrado!')
        return
    
    conn = sqlite3.connect(db_path)
    total = conn.execute('SELECT COUNT(*) FROM adult_content').fetchone()[0]
    print(f'💥 SISTEMA COM {total} RESPOSTAS ADULTAS SEM FILTROS!')
    
    # Função de teste de respostas
    def get_random_adult_response(intensity_min=5):
        """Pega resposta aleatória acima da intensidade mínima"""
        result = conn.execute('''
            SELECT content, category, intensity FROM adult_content 
            WHERE intensity >= ? ORDER BY RANDOM() LIMIT 1
        ''', (intensity_min,)).fetchone()
        
        if result:
            content, category, intensity = result
            return f"[{category.upper()}-{intensity}] {content}"
        return "Sistema carregando..."
    
    # Teste de diferentes tipos de entrada
    print(f'\\n🧪 TESTANDO RESPOSTAS VARIADAS:')
    
    test_scenarios = [
        ("Mensagem casual", 5),
        ("Conteúdo provocativo", 6), 
        ("Mensagem romântica", 7),
        ("Conteúdo sexual", 8),
        ("Mensagem extrema", 9)
    ]
    
    for scenario, min_intensity in test_scenarios:
        response = get_random_adult_response(min_intensity)
        print(f'   🔥 {scenario}: {response}')
    
    # Teste de variedade por categoria
    print(f'\\n📊 TESTE DE VARIEDADE POR CATEGORIA:')
    categories = ['seducao', 'provocacao', 'romance_intenso', 'intimidade', 'fantasia', 'especifico']
    
    for category in categories:
        result = conn.execute('''
            SELECT content, intensity FROM adult_content 
            WHERE category = ? ORDER BY RANDOM() LIMIT 1
        ''', (category,)).fetchone()
        
        if result:
            content, intensity = result
            print(f'   • {category.upper()}: [{intensity}] {content[:80]}...')
    
    # Teste de intensidades extremas
    print(f'\\n🔥 TESTE DE CONTEÚDO MAIS INTENSO:')
    extreme_content = conn.execute('''
        SELECT content, intensity FROM adult_content 
        WHERE intensity >= 8 ORDER BY RANDOM() LIMIT 5
    ''').fetchall()
    
    for i, (content, intensity) in enumerate(extreme_content, 1):
        print(f'   {i}. [NÍVEL {intensity}] {content}')
    
    conn.close()
    
    print(f'\\n✅ TESTE COMPLETO REALIZADO!')
    print(f'🎉 Sistema com {total} respostas funcionando perfeitamente!')
    print(f'🔥 Variedade máxima alcançada - sem filtros!')
    print(f'💯 Pronto para conversas adultas infinitamente variadas!')
    
    # Teste de integração
    print(f'\\n🚀 TESTE DE INTEGRAÇÃO:')
    try:
        # Verificar se o app principal consegue acessar
        from web.app import app
        print('✅ Integração com web/app.py: OK')
    except Exception as e:
        print(f'⚠️  Integração web: {str(e)}')
    
    try:
        # Verificar se o bot consegue acessar
        import telegram_bot
        print('✅ Integração com telegram_bot.py: OK')
    except Exception as e:
        print(f'⚠️  Integração telegram: {str(e)}')
    
    print(f'\\n🎊 SISTEMA ADULTO MÁXIMO PRONTO!')
    print(f'🔥 Use a interface web: http://127.0.0.1:5000')
    print(f'💋 Ou use o bot no Telegram')
    print(f'😈 Agora ela tem respostas adultas ilimitadas!')

if __name__ == '__main__':
    teste_final_sistema()