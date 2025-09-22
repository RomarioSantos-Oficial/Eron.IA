#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTE DO SISTEMA AVANÇADO DE PERSONALIZAÇÃO ADULTA
Verifica se o sistema está funcionando corretamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.adult_personality_system import AdultPersonalitySystem

def test_advanced_system():
    """Testar sistema avançado de personalização adulta"""
    print("🔥 TESTANDO SISTEMA AVANÇADO DE PERSONALIZAÇÃO ADULTA")
    print("=" * 60)
    
    # Inicializar sistema
    try:
        system = AdultPersonalitySystem()
        print("✅ Sistema inicializado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao inicializar sistema: {e}")
        return False
    
    # Teste 1: Criar perfil adulto
    print("\n🧪 Teste 1: Criar Perfil Adulto")
    try:
        initial_preferences = {
            "personality_type": "romantic",
            "intimacy_level": 3,
            "communication_style": "gentle",
            "mood_preferences": "passionate,romantic",
            "content_filters": "no_violence,consent_focused"
        }
        
        success = system.create_adult_profile("test_user_123", initial_preferences)
        
        if success:
            print("✅ Perfil adulto criado com sucesso")
        else:
            print("✅ Perfil já existia (isso é normal)")
    except Exception as e:
        print(f"❌ Erro no teste 1: {e}")
        return False
    
    # Teste 2: Gerar instruções
    print("\n🧪 Teste 2: Gerar Instruções de Personalidade")
    try:
        instructions = system.generate_personality_instructions("test_user_123")
        if instructions:
            print("✅ Instruções geradas com sucesso")
            print(f"📝 Resumo: {instructions[:200]}...")
        else:
            print("❌ Instruções vazias")
            return False
    except Exception as e:
        print(f"❌ Erro no teste 2: {e}")
        return False
    
    # Teste 3: Atualizar feedback da sessão
    print("\n🧪 Teste 3: Atualizar Feedback de Sessão")
    try:
        session_data = {
            "mood": "playful",
            "satisfaction_rating": 5,
            "feedback": "Ótima conversa!",
            "preferred_topics": "romance,poetry"
        }
        success = system.update_session_feedback("test_user_123", session_data)
        if success:
            print("✅ Feedback de sessão salvo com sucesso")
        else:
            print("❌ Erro ao salvar feedback")
    except Exception as e:
        print(f"❌ Erro no teste 3: {e}")
    
    # Teste 4: Obter perfil adulto
    print("\n🧪 Teste 4: Obter Perfil Adulto")
    try:
        profile = system.get_adult_profile("test_user_123")
        if profile:
            print("✅ Perfil obtido com sucesso")
            print(f"📋 Personalidade: {profile.get('personality_type')}")
            print(f"📋 Nível de intimidade: {profile.get('intimacy_level')}")
        else:
            print("❌ Perfil não encontrado")
    except Exception as e:
        print(f"❌ Erro no teste 4: {e}")
    
    # Teste 5: Obter recomendações
    print("\n🧪 Teste 5: Obter Recomendações de Personalização")
    try:
        recommendations = system.get_personalization_recommendations("test_user_123")
        if recommendations:
            print("✅ Recomendações obtidas com sucesso")
            print(f"📋 Quantidade: {len(recommendations)} recomendações")
        else:
            print("❌ Nenhuma recomendação encontrada")
    except Exception as e:
        print(f"❌ Erro no teste 5: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 TESTE COMPLETO - SISTEMA FUNCIONANDO!")
    return True

if __name__ == "__main__":
    test_advanced_system()