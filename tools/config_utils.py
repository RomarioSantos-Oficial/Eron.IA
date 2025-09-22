#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERON.IA - UTILITÁRIO DE CONFIGURAÇÃO
===================================

Script utilitário para testar, validar e gerenciar
as configurações do sistema Eron.IA.

Uso:
    python config_utils.py --validate    # Validar configurações
    python config_utils.py --show        # Mostrar configurações
    python config_utils.py --create-env  # Criar arquivo .env
    python config_utils.py --test        # Testar conexões
"""

import sys
import os
import argparse
from pathlib import Path

# Adicionar o diretório raiz ao path para importar config
sys.path.append(str(Path(__file__).parent.parent))

try:
    from core.config import config, get_config
except ImportError:
    print("❌ Erro: Não foi possível importar o módulo config.py")
    print("Certifique-se de que o arquivo config.py está no mesmo diretório.")
    sys.exit(1)

def validate_configuration():
    """Valida todas as configurações do sistema"""
    print("🔍 VALIDANDO CONFIGURAÇÕES DO ERON.IA")
    print("=" * 60)
    
    # Verificar configurações obrigatórias
    missing_configs = config.validate_required_configs()
    
    if missing_configs:
        print("❌ CONFIGURAÇÕES FALTANTES:")
        for section, keys in missing_configs.items():
            print(f"  📁 {section.upper()}:")
            for key in keys:
                print(f"    • {key}")
        print("\n💡 Configure as variáveis em falta no arquivo .env")
        return False
    
    # Verificar arquivos e diretórios
    print("📁 VERIFICANDO ESTRUTURA DE DIRETÓRIOS...")
    config.create_directories()
    
    required_dirs = [
        config.base_dir / 'memoria',
        config.base_dir / 'logs',
        config.base_dir / 'backup',
        config.base_dir / 'outros'
    ]
    
    for directory in required_dirs:
        if directory.exists():
            print(f"✅ {directory.name}/")
        else:
            print(f"❌ {directory.name}/ (será criado)")
    
    # Verificar arquivos de banco
    print("\n🗄️ VERIFICANDO BANCOS DE DADOS...")
    db_files = [
        ('memoria', config.database['memoria_path']),
        ('emotions', config.database['emotions_path']),
        ('knowledge', config.database['knowledge_path']),
        ('preferences', config.database['preferences_path']),
        ('user_profiles', config.database['user_profiles_path']),
        ('sensitive_memory', config.database['sensitive_memory_path'])
    ]
    
    for name, path in db_files:
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {name}.db ({size:,} bytes)")
        else:
            print(f"⚠️ {name}.db (será criado)")
    
    print("\n✅ VALIDAÇÃO CONCLUÍDA!")
    return True

def show_configuration():
    """Mostra um resumo detalhado das configurações"""
    config.print_config_summary()
    
    print("\n📋 CONFIGURAÇÕES DETALHADAS")
    print("=" * 60)
    
    sections = [
        ('telegram', '🤖 TELEGRAM BOT'),
        ('web', '🌐 WEB APPLICATION'),
        ('llm', '🧠 LLM/AI MODEL'),
        ('database', '🗄️ DATABASE'),
        ('adult_system', '🔞 SISTEMA ADULTO'),
        ('email', '📧 EMAIL'),
        ('logging', '📝 LOGGING'),
        ('security', '🔒 SECURITY'),
        ('performance', '⚡ PERFORMANCE'),
        ('learning', '🎓 LEARNING')
    ]
    
    for section_key, section_title in sections:
        print(f"\n{section_title}")
        print("-" * 40)
        
        section_config = getattr(config, section_key)
        for key, value in section_config.items():
            # Ocultar valores sensíveis
            if any(sensitive in key.lower() for sensitive in ['token', 'password', 'key', 'secret']):
                if value:
                    display_value = "***CONFIGURADO***"
                else:
                    display_value = "❌ NÃO CONFIGURADO"
            else:
                display_value = str(value)
            
            print(f"  {key}: {display_value}")

def create_env_file():
    """Cria um arquivo .env baseado no .env.example"""
    env_path = config.base_dir / '.env'
    env_example_path = config.base_dir / '.env.example'
    
    if env_path.exists():
        response = input("📝 Arquivo .env já existe. Sobrescrever? (s/N): ")
        if response.lower() != 's':
            print("❌ Operação cancelada.")
            return
    
    if not env_example_path.exists():
        print("❌ Arquivo .env.example não encontrado!")
        return
    
    try:
        # Copiar .env.example para .env
        content = env_example_path.read_text(encoding='utf-8')
        env_path.write_text(content, encoding='utf-8')
        
        print(f"✅ Arquivo .env criado em: {env_path}")
        print("⚠️ IMPORTANTE: Configure os valores reais no arquivo .env!")
        print("\n📝 Próximos passos:")
        print("1. Edite o arquivo .env")
        print("2. Configure TELEGRAM_BOT_TOKEN com seu token real")
        print("3. Configure outras variáveis conforme necessário")
        print("4. Execute: python config_utils.py --validate")
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivo .env: {e}")

def test_connections():
    """Testa as conexões com serviços externos"""
    print("🔌 TESTANDO CONEXÕES")
    print("=" * 60)
    
    # Teste do LLM
    print("🧠 Testando conexão com LLM...")
    try:
        import requests
        llm_url = config.llm['base_url']
        response = requests.get(f"{llm_url}/models", timeout=5)
        if response.status_code == 200:
            print(f"✅ LLM conectado: {llm_url}")
        else:
            print(f"❌ LLM retornou status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar com LLM: {e}")
    except ImportError:
        print("⚠️ Biblioteca 'requests' não instalada. Pulando teste do LLM.")
    
    # Teste do Telegram (apenas validação do token)
    print("\n🤖 Validando token do Telegram...")
    telegram_token = config.telegram['token']
    if telegram_token and len(telegram_token) > 20:
        print("✅ Token do Telegram parece válido")
    else:
        print("❌ Token do Telegram inválido ou não configurado")
    
    # Teste de email (apenas configuração)
    print("\n📧 Verificando configuração de email...")
    if config.email['username'] and config.email['password']:
        print("✅ Configurações de email definidas")
    else:
        print("⚠️ Configurações de email não definidas (opcional)")
    
    print("\n✅ TESTES CONCLUÍDOS!")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Utilitário de configuração do Eron.IA")
    parser.add_argument('--validate', action='store_true', help="Validar configurações")
    parser.add_argument('--show', action='store_true', help="Mostrar configurações")
    parser.add_argument('--create-env', action='store_true', help="Criar arquivo .env")
    parser.add_argument('--test', action='store_true', help="Testar conexões")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    try:
        if args.validate:
            validate_configuration()
        
        if args.show:
            show_configuration()
        
        if args.create_env:
            create_env_file()
        
        if args.test:
            test_connections()
            
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()