"""
Exemplos de Integração - Sistema de Logging
==========================================

Exemplos práticos de como integrar o sistema de logging estruturado
do Eron.IA em diferentes partes do sistema.

Autor: Eron.IA System
Data: 2024
"""

import time
import sys
import os

# Adicionar diretório pai para import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logging_system import (
    get_logger, 
    LogCategory,
    log_performance,
    log_user_interaction,
    log_llm_interaction,
    log_security_event
)


def exemplo_telegram_bot():
    """Exemplo de integração com bot do Telegram"""
    print("\n🤖 EXEMPLO: Integração com Telegram Bot")
    print("-" * 40)
    
    # Logger específico para Telegram
    logger = get_logger(LogCategory.TELEGRAM, "bot_handler")
    
    # Simular recebimento de mensagem
    logger.info("Bot iniciado e aguardando mensagens")
    
    # Simular processamento de comando
    start_time = time.time()
    logger.info("Processando comando /start do usuário")
    
    # Simular tempo de processamento
    time.sleep(0.1)
    end_time = time.time()
    
    # Log de performance
    log_performance(
        LogCategory.TELEGRAM,
        "process_start_command",
        (end_time - start_time) * 1000,
        {"command": "/start", "success": True}
    )
    
    # Log de interação do usuário
    log_user_interaction(
        user_id=123456789,
        chat_id=987654321,
        action="start_command",
        details={"timestamp": time.time()}
    )
    
    logger.info("Comando processado com sucesso")
    print("✅ Logs do Telegram gerados")


def exemplo_web_app():
    """Exemplo de integração com aplicação web Flask"""
    print("\n🌐 EXEMPLO: Integração com Web App")
    print("-" * 40)
    
    # Logger para web
    logger = get_logger(LogCategory.WEB, "flask_app")
    
    # Simular requisição web
    logger.info("Servidor web iniciado na porta 5000")
    
    # Simular processamento de rota
    start_time = time.time()
    logger.info("Processando requisição GET /chat")
    
    time.sleep(0.05)
    end_time = time.time()
    
    # Log de performance da requisição web
    log_performance(
        LogCategory.WEB,
        "handle_chat_request",
        (end_time - start_time) * 1000,
        {
            "method": "GET",
            "endpoint": "/chat",
            "status_code": 200,
            "user_agent": "Mozilla/5.0"
        }
    )
    
    logger.info("Requisição processada com status 200")
    print("✅ Logs da aplicação web gerados")


def exemplo_llm_integration():
    """Exemplo de integração com sistema LLM"""
    print("\n🧠 EXEMPLO: Integração com LLM")
    print("-" * 40)
    
    # Logger para LLM
    logger = get_logger(LogCategory.LLM, "openai_client")
    
    # Simular chamada para LLM
    logger.info("Enviando prompt para modelo LLM")
    
    start_time = time.time()
    time.sleep(0.2)  # Simular tempo de resposta do LLM
    end_time = time.time()
    
    # Log específico para LLM
    log_llm_interaction(
        model="gpt-3.5-turbo",
        tokens_used=150,
        response_time=(end_time - start_time) * 1000,
        prompt_type="conversation"
    )
    
    logger.info("Resposta recebida do modelo LLM")
    print("✅ Logs de LLM gerados")


def exemplo_database_operations():
    """Exemplo de integração com operações de banco"""
    print("\n🗄️ EXEMPLO: Integração com Database")
    print("-" * 40)
    
    # Logger para database
    logger = get_logger(LogCategory.DATABASE, "sqlite_handler")
    
    # Simular operações de banco
    logger.info("Conectando ao banco de dados")
    
    start_time = time.time()
    logger.debug("Executando query: SELECT * FROM users WHERE active = 1")
    
    time.sleep(0.03)  # Simular tempo de query
    end_time = time.time()
    
    # Log de performance de database
    log_performance(
        LogCategory.DATABASE,
        "execute_user_query",
        (end_time - start_time) * 1000,
        {
            "query_type": "SELECT",
            "table": "users",
            "rows_affected": 42,
            "execution_plan": "index_scan"
        }
    )
    
    logger.info("Query executada com sucesso - 42 registros retornados")
    print("✅ Logs de database gerados")


def exemplo_security_events():
    """Exemplo de logging de eventos de segurança"""
    print("\n🔒 EXEMPLO: Eventos de Segurança")
    print("-" * 40)
    
    # Logger para segurança
    logger = get_logger(LogCategory.SECURITY, "auth_handler")
    
    # Evento de segurança - tentativa de login
    logger.warning("Tentativa de login com credenciais inválidas detectada")
    
    log_security_event(
        event_type="invalid_login_attempt",
        severity="medium",
        details={
            "username": "admin",
            "ip_address": "192.168.1.100",
            "user_agent": "curl/7.68.0",
            "attempts_count": 3
        },
        user_id=None
    )
    
    # Evento crítico de segurança
    logger.critical("Múltiplas tentativas de acesso não autorizado")
    
    log_security_event(
        event_type="brute_force_detected",
        severity="critical",
        details={
            "ip_address": "192.168.1.100",
            "attempts_in_5min": 25,
            "blocked": True
        }
    )
    
    print("✅ Logs de segurança gerados")


def exemplo_memory_system():
    """Exemplo de integração com sistema de memória"""
    print("\n🧠 EXEMPLO: Sistema de Memória")
    print("-" * 40)
    
    # Logger para sistema de memória
    logger = get_logger(LogCategory.MEMORY, "emotion_handler")
    
    # Operações de memória emocional
    logger.info("Analisando estado emocional do usuário")
    
    start_time = time.time()
    logger.debug("Recuperando histórico emocional dos últimos 7 dias")
    
    time.sleep(0.02)
    end_time = time.time()
    
    log_performance(
        LogCategory.MEMORY,
        "retrieve_emotion_history",
        (end_time - start_time) * 1000,
        {
            "user_id": 123456,
            "days_back": 7,
            "emotions_found": 15,
            "primary_emotion": "happiness"
        }
    )
    
    logger.info("Estado emocional atualizado: felicidade (85%)")
    print("✅ Logs do sistema de memória gerados")


def exemplo_error_handling():
    """Exemplo de tratamento de erros com logging"""
    print("\n❌ EXEMPLO: Tratamento de Erros")
    print("-" * 40)
    
    logger = get_logger(LogCategory.GENERAL, "error_handler")
    
    try:
        # Simular erro
        result = 1 / 0
    except ZeroDivisionError as e:
        logger.error(f"Erro de divisão por zero: {str(e)}", exc_info=True)
        
        # Log de evento de segurança para erros críticos
        log_security_event(
            event_type="application_error",
            severity="low",
            details={
                "error_type": "ZeroDivisionError",
                "function": "exemplo_error_handling",
                "line": 42
            }
        )
    
    print("✅ Logs de erro gerados")


if __name__ == "__main__":
    print("🔧 SISTEMA DE LOGGING - EXEMPLOS DE INTEGRAÇÃO")
    print("=" * 60)
    
    # Executar exemplos
    exemplo_telegram_bot()
    exemplo_web_app()
    exemplo_llm_integration()
    exemplo_database_operations()
    exemplo_security_events()
    exemplo_memory_system()
    exemplo_error_handling()
    
    print("\n" + "=" * 60)
    print("✅ TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
    print(f"📁 Verifique os logs gerados na pasta: logs/")
    print("📊 Diferentes tipos de arquivo foram criados:")
    print("   - eron_general.log (todos os logs)")
    print("   - eron_errors.log (apenas erros)")
    print("   - eron_telegram.log (logs do Telegram)")
    print("   - eron_database.log (logs de banco)")