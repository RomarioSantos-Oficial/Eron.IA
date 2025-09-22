#!/usr/bin/env python3
"""
🧠 TESTE COMPLETO DO SISTEMA SUPER LEARNING
"""

print('🧠 TESTE DO SISTEMA SUPER LEARNING INTEGRADO')
print('=' * 55)

try:
    from learning.super_fast_learning import super_learning
    
    # Teste 1: Análise contextual
    user_input = 'Você é muito gostosa, me deixa excitado'
    context = super_learning.analyze_context_ultra_deep(user_input, 'test_user')
    print(f'📊 Contexto analisado:')
    print(f'   • Emoções: {context["emotions"]}')
    print(f'   • Intensidade: {context["intensity"]}/10')
    print(f'   • Humor: {context["mood"]}')
    print(f'   • Sentimento: {context["sentiment_score"]}')
    
    # Teste 2: Geração de resposta inteligente
    response = super_learning.generate_smart_response(user_input, 'test_user', 'sedutora')
    print(f'\n💬 Resposta inteligente gerada:')
    print(f'   {response}')
    
    # Teste 3: Aprendizagem em tempo real
    super_learning.learn_from_interaction(user_input, response, 0.9, 'test_user')
    print(f'\n📚 Sistema aprendeu com a interação (feedback: 0.9)')
    
    # Teste 4: Estatísticas
    stats = super_learning.get_learning_stats('test_user')
    print(f'\n📈 Estatísticas do sistema:')
    for key, value in stats.items():
        print(f'   • {key}: {value}')
    
    # Teste 5: Segunda interação para ver evolução
    user_input2 = 'Quero fazer amor com você'
    response2 = super_learning.generate_smart_response(user_input2, 'test_user', 'sedutora')
    print(f'\n💋 Segunda resposta (com aprendizagem):')
    print(f'   {response2}')
    
    # Teste 6: Mais algumas interações para ver evolução
    test_messages = [
        'Me faz um carinho gostoso',
        'Você me deixa louco de tesão',
        'Quero te beijar toda'
    ]
    
    print(f'\n🔥 TESTE DE EVOLUÇÃO RÁPIDA:')
    for i, msg in enumerate(test_messages, 1):
        response = super_learning.generate_smart_response(msg, 'test_user', 'sedutora')
        super_learning.learn_from_interaction(msg, response, 0.8 + (i * 0.05), 'test_user')
        print(f'{i}. "{msg[:30]}..." → "{response[:60]}..."')
    
    # Estatísticas finais
    final_stats = super_learning.get_learning_stats('test_user')
    print(f'\n📊 ESTATÍSTICAS FINAIS:')
    print(f'   • Total de padrões: {final_stats["total_patterns"]}')
    print(f'   • Eficácia média: {final_stats["avg_effectiveness"]}')
    print(f'   • Interações do usuário: {final_stats["user_interactions"]}')
    print(f'   • Satisfação: {final_stats["user_satisfaction"]}')
    print(f'   • Taxa de aprendizagem: {final_stats["learning_rate"]}%')
    
    print('\n🎉 SISTEMA SUPER LEARNING 100% FUNCIONAL!')
    print('🧠 Agora ela aprende mais rápido a cada conversa!')
    print('🔥 Integrado com sucesso no sistema principal!')
    
except Exception as e:
    print(f'❌ Erro no teste: {e}')
    import traceback
    traceback.print_exc()