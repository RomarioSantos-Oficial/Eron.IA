"""
EXEMPLO DE INTEGRAÇÃO - WEB/APP.PY
==================================

Este arquivo demonstra como integrar o sistema de configuração
centralizado no código existente do Eron.IA.

ANTES (código antigo):
    app.config['SECRET_KEY'] = 'hardcoded-secret'
    app.run(host='127.0.0.1', port=5000, debug=True)

DEPOIS (com configuração centralizada):
    from core.config import get_config
    app.config['SECRET_KEY'] = get_config('web', 'secret_key')
    web_config = get_config('web')
    app.run(host=web_config['host'], port=web_config['port'], debug=web_config['debug'])
"""

# Exemplo de integração no código Flask
def create_flask_app_with_config():
    """Exemplo de como configurar Flask usando o sistema centralizado"""
    
    from flask import Flask
    from core.config import get_config, config
    
    # Criar aplicação Flask
    app = Flask(__name__)
    
    # ✅ NOVA FORMA: Configuração centralizada
    web_config = get_config('web')
    app.config.update({
        'SECRET_KEY': web_config['secret_key'],
        'DEBUG': web_config['debug'],
        'PERMANENT_SESSION_LIFETIME': web_config['session_lifetime_hours'] * 3600,
        'SESSION_PERMANENT': web_config.get('session_permanent', False)
    })
    
    # Configurações de segurança
    security_config = get_config('security')
    app.config.update({
        'MAX_LOGIN_ATTEMPTS': security_config['max_login_attempts'],
        'PASSWORD_MIN_LENGTH': security_config['password_min_length']
    })
    
    return app, web_config

# Exemplo de integração no Telegram Bot
def create_telegram_bot_with_config():
    """Exemplo de como configurar Telegram Bot usando o sistema centralizado"""
    
    from telegram.ext import ApplicationBuilder
    from core.config import get_config
    
    # ✅ NOVA FORMA: Configuração centralizada
    telegram_config = get_config('telegram')
    
    application = ApplicationBuilder() \
        .token(telegram_config['token']) \
        .concurrent_updates(telegram_config['max_concurrent_updates']) \
        .pool_timeout(telegram_config['pool_timeout']) \
        .connection_pool_size(telegram_config['connection_pool_size']) \
        .build()
    
    return application, telegram_config

# Exemplo de integração nas requisições LLM
def get_llm_response_with_config(messages):
    """Exemplo de como configurar requisições LLM usando o sistema centralizado"""
    
    import requests
    from core.config import get_config
    
    # ✅ NOVA FORMA: Configuração centralizada
    llm_config = get_config('llm')
    
    payload = {
        "model": llm_config['model_name'],
        "messages": messages,
        "max_tokens": llm_config['max_tokens'],
        "temperature": llm_config['temperature']
    }
    
    headers = {
        "Authorization": f"Bearer {llm_config['api_key']}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{llm_config['base_url']}/chat/completions",
            json=payload,
            headers=headers,
            timeout=llm_config['timeout']
        )
        return response.json()
    except requests.exceptions.Timeout:
        print(f"❌ Timeout após {llm_config['timeout']}s")
        return None

# Exemplo de configuração de logging
def setup_logging_with_config():
    """Exemplo de como configurar logging usando o sistema centralizado"""
    
    import logging
    from logging.handlers import RotatingFileHandler
    from core.config import get_config
    
    # ✅ NOVA FORMA: Configuração centralizada
    logging_config = get_config('logging')
    
    # Configurar nível de logging
    level = getattr(logging, logging_config['level'].upper())
    
    # Configurar formatação
    formatter = logging.Formatter(logging_config['format'])
    
    # Configurar handler de arquivo se habilitado
    if logging_config['file_enabled']:
        file_handler = RotatingFileHandler(
            logging_config['file_path'],
            maxBytes=logging_config['max_file_size_mb'] * 1024 * 1024,
            backupCount=logging_config['backup_count']
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
    
    # Configurar handler de console se habilitado
    if logging_config['console_enabled']:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
    
    return logging_config

# Exemplo de configuração de banco de dados
def get_database_connection_with_config(db_name):
    """Exemplo de como conectar aos bancos usando o sistema centralizado"""
    
    import sqlite3
    from core.config import get_config
    
    # ✅ NOVA FORMA: Configuração centralizada
    db_config = get_config('database')
    db_path = db_config[f'{db_name}_path']
    
    try:
        connection = sqlite3.connect(str(db_path))
        connection.row_factory = sqlite3.Row  # Para acessar colunas por nome
        return connection
    except sqlite3.Error as e:
        print(f"❌ Erro ao conectar com {db_name}: {e}")
        return None

# Exemplo de verificação de configurações na inicialização
def validate_startup_configuration():
    """Exemplo de validação de configurações na inicialização"""
    
    from core.config import config
    
    print("🔧 Verificando configurações de inicialização...")
    
    # Verificar configurações obrigatórias
    missing_configs = config.validate_required_configs()
    if missing_configs:
        print("❌ ERRO: Configurações obrigatórias em falta:")
        for section, keys in missing_configs.items():
            print(f"  {section}: {', '.join(keys)}")
        return False
    
    # Criar diretórios necessários
    config.create_directories()
    
    # Verificar se está em produção
    if config.is_production():
        print("🏭 Executando em modo PRODUÇÃO")
        # Configurações específicas de produção
    else:
        print("🛠️ Executando em modo DESENVOLVIMENTO")
        # Configurações específicas de desenvolvimento
    
    print("✅ Configurações validadas com sucesso!")
    return True

if __name__ == "__main__":
    print("📋 EXEMPLOS DE INTEGRAÇÃO - SISTEMA DE CONFIGURAÇÃO")
    print("=" * 60)
    
    # Adicionar o diretório pai ao sys.path para importar config
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    
    # Mostrar como usar as configurações
    from core.config import get_config, config
    
    print("🌐 Configurações Web:")
    web_config = get_config('web')
    print(f"  Host: {web_config['host']}")
    print(f"  Port: {web_config['port']}")
    print(f"  Debug: {web_config['debug']}")
    
    print("\n🤖 Configurações Telegram:")
    telegram_config = get_config('telegram')
    print(f"  Token configurado: {'Sim' if telegram_config['token'] else 'Não'}")
    print(f"  Max concurrent: {telegram_config['max_concurrent_updates']}")
    
    print("\n🧠 Configurações LLM:")
    llm_config = get_config('llm')
    print(f"  URL: {llm_config['base_url']}")
    print(f"  Model: {llm_config['model_name']}")
    print(f"  Max tokens: {llm_config['max_tokens']}")
    
    print("\n✅ Sistema de configuração funcionando!")
