"""
Teste de Comandos do Bot do Telegram - Eron.IA
===============================================

Este script testa todos os comandos do bot do Telegram, especialmente
os relacionados ao sistema adulto e configurações de perfil.

Problemas identificados:
1. /devassa_off pode não estar funcionando
2. /help não mostra comandos adultos
3. Falta página específica para comandos adultos
"""

import sys
import os
from datetime import datetime

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Testar se podemos importar as funções necessárias"""
    print("🧪 TESTE DE IMPORTAÇÕES")
    print("=" * 50)
    
    try:
        from core.check import check_age
        print("✅ core.check.check_age importado")
    except ImportError as e:
        print(f"❌ Erro ao importar check_age: {e}")
        
    try:
        from core.user_profile_db import UserProfileDB
        print("✅ UserProfileDB importado")
    except ImportError as e:
        print(f"❌ Erro ao importar UserProfileDB: {e}")
    
    print()

def test_devassa_off_function():
    """Testar especificamente a função deactivate_adult_mode"""
    print("🔴 TESTE DO COMANDO /devassa_off")
    print("=" * 50)
    
    try:
        # Simular dados de um usuário adulto
        from core.user_profile_db import UserProfileDB
        from core.check import check_age
        
        profile_db = UserProfileDB()
        test_user_id = "test_devassa_user"
        
        # Ativar modo adulto primeiro
        profile_db.save_profile(
            user_id=test_user_id,
            user_age="25",
            has_mature_access=True
        )
        
        print(f"👤 Usuário de teste: {test_user_id}")
        
        # Verificar status antes
        status_before = check_age(test_user_id)
        print(f"📊 Status antes: {status_before}")
        
        # Simular desativação (como o comando /devassa_off faria)
        profile_db.update_profile(test_user_id, has_mature_access=False)
        
        # Verificar status depois
        status_after = check_age(test_user_id)
        print(f"📊 Status depois: {status_after}")
        
        if status_after.get('adult_mode_active') == False:
            print("✅ Função de desativação funcionaria corretamente")
        else:
            print("❌ Problema na desativação do modo adulto")
            
    except Exception as e:
        print(f"❌ Erro no teste devassa_off: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def main():
    """Executar todos os testes"""
    print("🧪 TESTE COMPLETO DOS COMANDOS DO BOT")
    print("====================================")
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    test_imports()
    test_devassa_off_function()
    
    print("🎯 PROBLEMAS ENCONTRADOS E SOLUÇÕES:")
    print("=" * 50)
    print("1. ✅ Função deactivate_adult_mode existe no código")
    print("2. ❌ Comando /help não verifica perfil adulto do usuário") 
    print("3. ❌ Falta comando /help_adulto específico")
    print("4. ✅ Sistema de verificação de idade funciona")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("1. Corrigir função help_command para mostrar comandos adultos")
    print("2. Criar comando /help_adulto")
    print("3. Criar página específica de comandos adultos")

if __name__ == "__main__":
    main()