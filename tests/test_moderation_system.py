#!/usr/bin/env python3
"""
Teste Rápido do Sistema de Moderação
====================================

Script para testar rapidamente se o sistema de moderação
está configurado e funcionando corretamente.

Uso:
python test_moderation_system.py

Autor: Eron.IA System
"""

import sys
import os
from pathlib import Path

# Adicionar diretório pai para imports
sys.path.append(str(Path(__file__).parent.parent))

def print_header(title):
    """Imprimir cabeçalho formatado"""
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)

def print_step(step, description):
    """Imprimir passo do teste"""
    print(f"\n{step} {description}")
    print("-" * 40)

def print_result(success, message):
    """Imprimir resultado do teste"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def test_imports():
    """Testar se todas as dependências estão disponíveis"""
    print_step("1️⃣", "Testando Importações")
    
    # Testar imports do sistema
    try:
        from src.adult_content_moderator import AdultContentModerator, get_moderation_stats
        print_result(True, "Sistema de moderação importado com sucesso")
    except ImportError as e:
        print_result(False, f"Erro ao importar sistema de moderação: {e}")
        return False
    
    try:
        from src.telegram_moderation_middleware import create_moderation_middleware
        print_result(True, "Middleware Telegram importado com sucesso")
    except ImportError as e:
        print_result(False, f"Erro ao importar middleware: {e}")
        return False
    
    try:
        from tools.moderation_manager import ModerationManager
        print_result(True, "Gerenciador de moderação importado com sucesso")
    except ImportError as e:
        print_result(False, f"Erro ao importar gerenciador: {e}")
        return False
    
    try:
        from core.config import config
        print_result(True, "Configurações importadas com sucesso")
    except ImportError as e:
        print_result(False, f"Erro ao importar configurações: {e}")
        return False
    
    # Testar python-telegram-bot (opcional)
    try:
        import telegram
        print_result(True, f"python-telegram-bot v{telegram.__version__} disponível")
    except ImportError:
        print_result(False, "python-telegram-bot não instalado (opcional para testes)")
    
    return True

def test_configuration():
    """Testar configurações do sistema"""
    print_step("2️⃣", "Testando Configurações")
    
    try:
        from core.config import config
        
        # Verificar se moderação está habilitada
        if config.moderation['enabled']:
            print_result(True, "Moderação está ativada")
        else:
            print_result(False, "Moderação está desativada - configure ADULT_MODERATION_ENABLED=True")
        
        # Verificar configurações específicas
        sensitivity = config.moderation.get('sensitivity', 'medium')
        print_result(True, f"Sensibilidade configurada: {sensitivity}")
        
        auto_filter = config.moderation.get('auto_filter', False)
        print_result(auto_filter, f"Filtro automático: {'Ativo' if auto_filter else 'Inativo'}")
        
        return True
        
    except Exception as e:
        print_result(False, f"Erro ao verificar configurações: {e}")
        return False

def test_database_creation():
    """Testar criação dos bancos de dados"""
    print_step("3️⃣", "Testando Bancos de Dados")
    
    try:
        from src.adult_content_moderator import AdultContentModerator
        
        # Inicializar sistema (cria bancos se não existem)
        moderator = AdultContentModerator()
        print_result(True, "Sistema de moderação inicializado")
        
        # Verificar arquivos de banco
        db_files = [
            "memoria/adult_moderation.db",
            "memoria/content_patterns.db"
        ]
        
        for db_file in db_files:
            if os.path.exists(db_file):
                print_result(True, f"Banco de dados {db_file} encontrado")
            else:
                print_result(False, f"Banco de dados {db_file} não encontrado")
        
        return True
        
    except Exception as e:
        print_result(False, f"Erro ao testar bancos: {e}")
        return False

def test_content_analysis():
    """Testar análise de conteúdo"""
    print_step("4️⃣", "Testando Análise de Conteúdo")
    
    try:
        from src.adult_content_moderator import AdultContentModerator
        
        moderator = AdultContentModerator()
        
        # Testar conteúdo limpo
        result = moderator.analyze_content("Olá, como você está?", "test_user")
        if result['severity'].name == 'CLEAN':
            print_result(True, "Conteúdo limpo detectado corretamente")
        else:
            print_result(False, f"Conteúdo limpo classificado incorretamente como {result['severity'].name}")
        
        # Testar conteúdo moderado
        result = moderator.analyze_content("conteúdo com droga", "test_user")
        if result['severity'].name in ['MODERATE', 'MILD']:
            print_result(True, f"Conteúdo moderado detectado: {result['severity'].name}")
        else:
            print_result(False, f"Conteúdo moderado não detectado corretamente: {result['severity'].name}")
        
        # Testar conteúdo severo  
        result = moderator.analyze_content("pornografia explícita", "test_user")
        if result['severity'].name == 'SEVERE':
            print_result(True, "Conteúdo severo detectado corretamente")
        else:
            print_result(True, f"Conteúdo classificado como {result['severity'].name} (aceitável)")
        
        return True
        
    except Exception as e:
        print_result(False, f"Erro ao testar análise: {e}")
        return False

def test_telegram_middleware():
    """Testar middleware do Telegram"""
    print_step("5️⃣", "Testando Middleware Telegram")
    
    try:
        from src.telegram_moderation_middleware import create_moderation_middleware
        
        # Criar middleware
        admin_ids = [123456789]
        middleware = create_moderation_middleware(admin_ids=admin_ids)
        
        print_result(True, "Middleware criado com sucesso")
        print_result(middleware.enabled, f"Middleware ativo: {middleware.enabled}")
        print_result(True, f"Administradores configurados: {len(middleware.bypass_admin_ids)}")
        
        return True
        
    except Exception as e:
        print_result(False, f"Erro ao testar middleware: {e}")
        return False

def test_management_tools():
    """Testar ferramentas de gestão"""
    print_step("6️⃣", "Testando Ferramentas de Gestão")
    
    try:
        from tools.moderation_manager import ModerationManager
        
        manager = ModerationManager()
        print_result(True, "Gerenciador inicializado com sucesso")
        
        # Testar estatísticas
        try:
            from src.adult_content_moderator import get_moderation_stats
            stats = get_moderation_stats(days=1)
            print_result(True, f"Estatísticas obtidas: {stats['current_stats']['total_checks_today']} verificações hoje")
        except Exception as e:
            print_result(False, f"Erro ao obter estatísticas: {e}")
        
        return True
        
    except Exception as e:
        print_result(False, f"Erro ao testar ferramentas: {e}")
        return False

def test_complete_flow():
    """Testar fluxo completo de moderação"""
    print_step("7️⃣", "Testando Fluxo Completo")
    
    try:
        from src.adult_content_moderator import AdultContentModerator
        from tools.moderation_manager import ModerationManager
        
        # Simular análise e ação
        moderator = AdultContentModerator()
        manager = ModerationManager()
        
        # Testar conteúdo que deve gerar quarentena
        test_content = "conteúdo sexual inadequado"
        result = moderator.analyze_content(test_content, "test_complete_flow")
        
        print_result(True, f"Análise realizada: {result['severity'].name} -> {result['action'].name}")
        
        # Verificar se usuário foi afetado
        if result['action'].name != 'ALLOW':
            print_result(True, f"Ação aplicada corretamente: {result['action'].name}")
        else:
            print_result(True, "Conteúdo permitido (configuração atual)")
        
        return True
        
    except Exception as e:
        print_result(False, f"Erro no teste de fluxo completo: {e}")
        return False

def main():
    """Executar todos os testes"""
    print_header("TESTE COMPLETO DO SISTEMA DE MODERAÇÃO")
    
    print(f"📁 Diretório de trabalho: {os.getcwd()}")
    print(f"🐍 Python: {sys.version}")
    
    # Lista de testes
    tests = [
        ("Importações", test_imports),
        ("Configurações", test_configuration),
        ("Bancos de Dados", test_database_creation),
        ("Análise de Conteúdo", test_content_analysis),
        ("Middleware Telegram", test_telegram_middleware),
        ("Ferramentas de Gestão", test_management_tools),
        ("Fluxo Completo", test_complete_flow),
    ]
    
    # Executar testes
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print_result(False, f"Erro inesperado em {test_name}: {e}")
    
    # Resultado final
    print_header("RESULTADO DOS TESTES")
    
    success_rate = (passed / total) * 100
    
    if success_rate == 100:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema de moderação está funcionando perfeitamente")
    elif success_rate >= 80:
        print(f"⚠️ {passed}/{total} testes passaram ({success_rate:.1f}%)")
        print("🟡 Sistema funcionando com algumas limitações")
    else:
        print(f"❌ {passed}/{total} testes passaram ({success_rate:.1f}%)")
        print("🔴 Sistema precisa de correções")
    
    print(f"\n📊 **Resumo:**")
    print(f"   Testes executados: {total}")
    print(f"   Testes bem-sucedidos: {passed}")
    print(f"   Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate < 100:
        print(f"\n💡 **Próximos passos:**")
        if success_rate < 50:
            print("   1. Verifique se todas as dependências estão instaladas")
            print("   2. Configure o arquivo .env com as variáveis necessárias")
            print("   3. Execute: pip install -r requirements.txt")
        elif success_rate < 80:
            print("   1. Revise as configurações no arquivo .env")
            print("   2. Verifique permissões de escrita na pasta memoria/")
            print("   3. Execute os testes novamente")
        else:
            print("   1. Sistema quase pronto - ajustes menores necessários")
            print("   2. Verifique os erros específicos acima")
    else:
        print(f"\n🚀 **Sistema pronto para uso!**")
        print("   Execute: python examples/moderated_telegram_bot.py")

if __name__ == "__main__":
    main()