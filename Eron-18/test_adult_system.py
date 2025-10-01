"""
Script de Teste - Sistema Adulto Eron.IA
CONTEÚDO ADULTO (+18) - APENAS PARA TESTES
"""

import os
import sys

# Adicionar caminhos corretos
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
scripts_dir = os.path.join(current_dir, 'Scripts18')

sys.path.append(current_dir)
sys.path.append(project_root) 
sys.path.append(scripts_dir)

print(f"Diretório atual: {current_dir}")
print(f"Diretório do projeto: {project_root}")
print(f"Diretório dos scripts: {scripts_dir}")

try:
    from adult_personality_db import AdultPersonalityDB
    from adult_commands import AdultCommandSystem
    from devassa_personality import DevassaPersonality
    
    def test_adult_system():
        print("🔞 TESTANDO SISTEMA ADULTO ERON.IA")
        print("=" * 50)
        
        # Inicializar sistema
        print("1. Inicializando banco de dados...")
        adult_db = AdultPersonalityDB()
        print("✅ Banco inicializado")
        
        print("\n2. Inicializando sistema de comandos...")
        adult_commands = AdultCommandSystem(adult_db)
        print("✅ Sistema de comandos inicializado")
        
        # Simular usuário teste
        test_user_id = 12345
        print(f"\n3. Testando com usuário ID: {test_user_id}")
        
        # Teste 1: Ativação de comandos
        print("\n--- TESTE 1: Ativação do modo adulto ---")
        result = adult_commands.handle_adult_activation_command(test_user_id)
        print(f"Status: {result['status']}")
        print(f"Resposta: {result['message'][:100]}...")
        
        if result['status'] == 'terms_required':
            token = result['token']
            print(f"Token gerado: {token}")
            
            # Teste 2: Aceitar termos
            print("\n--- TESTE 2: Aceitar termos ---")
            terms_result = adult_commands.handle_terms_response(test_user_id, "ACEITO18", token)
            print(f"Status: {terms_result['status']}")
            print(f"Resposta: {terms_result['message'][:100]}...")
            
            if terms_result['status'] == 'age_verification':
                # Teste 3: Verificação de idade
                print("\n--- TESTE 3: Verificação de idade ---")
                age_result = adult_commands.handle_age_verification(
                    test_user_id, "25", token, terms_result['question_type']
                )
                print(f"Status: {age_result['status']}")
                print(f"Resposta: {age_result['message'][:100]}...")
                
                if age_result['status'] == 'access_granted':
                    print("✅ Acesso adulto concedido!")
                    
                    # Teste 4: Personalidade Devassa
                    print("\n--- TESTE 4: Personalidade Devassa ---")
                    
                    # Perfil de teste
                    test_profile = {
                        'user_id': test_user_id,
                        'user_name': 'João',
                        'bot_name': 'Joana',
                        'bot_gender': 'feminino',
                        'user_gender': 'masculino'
                    }
                    
                    devassa = DevassaPersonality(adult_db, test_profile)
                    
                    # Testar diferentes mensagens
                    test_messages = [
                        "Oi Joana",
                        "Como você está?", 
                        "Estou com tesão",
                        "Você é gostosa"
                    ]
                    
                    for msg in test_messages:
                        response = devassa.get_adaptive_response(msg)
                        print(f"Mensagem: {msg}")
                        print(f"Resposta: {response}")
                        print("-" * 30)
                    
                    # Teste 5: Configurações
                    print("\n--- TESTE 5: Menu de configuração ---")
                    config_result = adult_commands.get_adult_config_menu(test_user_id)
                    print(f"Status: {config_result['status']}")
                    print(f"Menu: {config_result['message'][:200]}...")
                    
                    # Teste 6: Alterar intensidade
                    print("\n--- TESTE 6: Alterar intensidade ---")
                    intensity_result = adult_commands.update_intensity(test_user_id, 3)
                    print(f"Status: {intensity_result['status']}")
                    print(f"Resposta: {intensity_result['message']}")
                    
                    # Teste 7: Status
                    print("\n--- TESTE 7: Status do sistema ---")
                    status_result = adult_commands.get_adult_status(test_user_id)
                    print(f"Status: {status_result['status']}")
                    print(f"Info: {status_result['message'][:200]}...")
                    
                    # Teste 8: Desativação
                    print("\n--- TESTE 8: Desativar modo adulto ---")
                    deactivate_result = adult_commands.deactivate_adult_mode(test_user_id)
                    print(f"Status: {deactivate_result['status']}")
                    print(f"Resposta: {deactivate_result['message']}")
                    
        print("\n🎉 TESTES CONCLUÍDOS!")
        print("=" * 50)

    if __name__ == "__main__":
        test_adult_system()

except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("Certifique-se de que todos os arquivos do sistema adulto estão presentes:")
    print(f"- {os.path.join(scripts_dir, 'adult_personality_db.py')}")
    print(f"- {os.path.join(scripts_dir, 'adult_commands.py')}")
    print(f"- {os.path.join(scripts_dir, 'devassa_personality.py')}")
    print(f"\nArquivos encontrados no diretório Scripts18:")
    if os.path.exists(scripts_dir):
        for f in os.listdir(scripts_dir):
            print(f"  - {f}")
    else:
        print(f"  Diretório {scripts_dir} não encontrado!")
except Exception as e:
    print(f"❌ Erro durante os testes: {e}")
    import traceback
    traceback.print_exc()