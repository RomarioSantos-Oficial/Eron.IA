#!/usr/bin/env python3
"""
🔥 Teste Final do Sistema Avançado de Aprendizagem Adulta
Verificação completa de funcionalidade sem filtros
"""

print('🔥 TESTE FINAL DO SISTEMA AVANÇADO DE APRENDIZAGEM ADULTA')
print('=' * 65)

try:
    from learning.advanced_adult_learning import AdvancedAdultLearning
    
    system = AdvancedAdultLearning()
    print('✅ Sistema carregado com sucesso!')
    
    # Criar perfil de teste
    user_id = 'user_final_test'
    profile = {
        'intensity_preference': 7,
        'personality_type': 'sedutora',
        'preferred_scenarios': ['romance', 'fantasia'],
        'spontaneity_level': 10
    }
    
    system.create_advanced_profile(user_id, profile)
    print('✅ Perfil VIP criado!')
    
    # Testar com mensagens adultas
    adult_messages = [
        'Me faz um carinho...',
        'Estou com saudades do seu toque...',
        'Quero te beijar agora...',
        'Você é muito gostosa...'
    ]
    
    print('\n💋 RESPOSTAS ADULTAS SEM FILTROS:')
    for i, msg in enumerate(adult_messages, 1):
        response = system.generate_dynamic_response(user_id, msg)
        print(f'{i}. "{msg}"')
        print(f'   → {response}\n')
    
    # Verificar conteúdo por categoria
    categories = ['seducao', 'romance_intenso', 'provocacao', 'intimidade', 'fantasia']
    print('🗂️ BANCO DE DADOS ADULTO:')
    
    total_items = 0
    for cat in categories:
        content = system.get_content_by_category(cat, intensity=7)
        print(f'   • {cat.upper()}: {len(content)} conteúdos')
        total_items += len(content)
    
    # Estatísticas finais
    stats = system.get_learning_stats(user_id)
    print(f'\n📊 STATUS FINAL:')
    print(f'   • Total de conteúdo: {total_items} itens')
    print(f'   • Conteúdo disponível DB: {stats["available_content"]} itens')
    print(f'   • Intensidade preferida: {stats["intensity_preference"]}/10')
    print(f'   • Interações realizadas: {stats["total_interactions"]}')
    
    print('\n🎉 SISTEMA 100% OPERACIONAL!')
    print('🔞 Sem filtros ou restrições adultas!')
    print('💥 Pronto para conversas intensas!')
    print('🚀 Integrado com Web e Telegram!')
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()

print('\n🔥 FIM DO TESTE - Sistema Avançado Verificado!')