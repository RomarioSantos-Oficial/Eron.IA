"""
Sistema de Logging Estruturado do Eron.IA
==========================================

Sistema centralizado de logging com:
- Rotação automática de arquivos
- Diferentes níveis de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Formatação estruturada
- Logs separados por categoria
- Integração com sistema de configuração
- Filtragem de informações sensíveis

Autor: Eron.IA System
Data: 2024
"""

import logging
import logging.handlers
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import json
import re
from enum import Enum

# Importar configuração
try:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from core.config import config
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from core.config import config


class LogLevel(Enum):
    """Níveis de log disponíveis"""
    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(Enum):
    """Categorias de log para organização"""
    TELEGRAM = "telegram"
    WEB = "web"
    LLM = "llm"
    DATABASE = "database"
    SECURITY = "security"
    MEMORY = "memory"
    EMOTIONS = "emotions"
    GENERAL = "general"
    ERROR = "error"


class SensitiveDataFilter(logging.Filter):
    """Filtro para remover dados sensíveis dos logs"""
    
    def __init__(self):
        super().__init__()
        self.sensitive_patterns = [
            # Tokens e chaves
            r'token["\s]*[:=]["\s]*[\w-]+',
            r'key["\s]*[:=]["\s]*[\w-]+',
            r'password["\s]*[:=]["\s]*[\w-]+',
            r'secret["\s]*[:=]["\s]*[\w-]+',
            
            # IDs de usuário específicos (manter formato geral)
            r'\b\d{8,12}\b',  # IDs do Telegram
            
            # URLs com tokens
            r'https?://[^\s]*[?&]token=[\w-]+',
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.sensitive_patterns]
    
    def filter(self, record):
        """Filtra dados sensíveis da mensagem de log"""
        if hasattr(record, 'msg'):
            msg = str(record.msg)
            for pattern in self.compiled_patterns:
                msg = pattern.sub('[REDACTED]', msg)
            record.msg = msg
        
        return True


class StructuredFormatter(logging.Formatter):
    """Formatador estruturado para logs"""
    
    def __init__(self, format_type='text'):
        self.format_type = format_type
        super().__init__()
    
    def format(self, record):
        """Formata o registro de log"""
        
        # Informações base
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'category': getattr(record, 'category', 'general'),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage()
        }
        
        # Adicionar informações extras se disponíveis
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = getattr(record, 'user_id', 'unknown')
        
        if hasattr(record, 'chat_id'):
            log_entry['chat_id'] = getattr(record, 'chat_id', 'unknown')
        
        if hasattr(record, 'execution_time'):
            log_entry['execution_time_ms'] = getattr(record, 'execution_time', 0)
        
        # Formatação baseada no tipo
        if self.format_type == 'json':
            return json.dumps(log_entry, ensure_ascii=False, indent=None)
        else:
            # Formato texto estruturado
            return (
                f"[{log_entry['timestamp']}] "
                f"{log_entry['level']:<8} "
                f"[{log_entry['category']:<10}] "
                f"{log_entry['module']}.{log_entry['function']}:{log_entry['line']} - "
                f"{log_entry['message']}"
            )


class EronLogger:
    """Sistema de logging centralizado do Eron.IA"""
    
    def __init__(self):
        self.loggers: Dict[str, logging.Logger] = {}
        self.handlers_created = False
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura o sistema de logging"""
        
        # Criar diretório de logs
        log_dir = Path(config.logging['dir'])
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuração base
        logging.basicConfig(level=getattr(logging, config.logging['level'].upper()))
        
        # Criar handlers para cada categoria
        self._create_handlers()
        self.handlers_created = True
    
    def _create_handlers(self):
        """Cria handlers para diferentes categorias de log"""
        
        log_dir = Path(config.logging['dir'])
        
        # Handler para arquivo geral (todos os logs)
        general_handler = logging.handlers.RotatingFileHandler(
            log_dir / "eron_general.log",
            maxBytes=config.logging['max_size_bytes'],
            backupCount=config.logging['backup_count'],
            encoding='utf-8'
        )
        general_handler.setFormatter(StructuredFormatter('text'))
        general_handler.addFilter(SensitiveDataFilter())
        
        # Handler para erros específicos
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "eron_errors.log",
            maxBytes=config.logging['max_size_bytes'],
            backupCount=config.logging['backup_count'],
            encoding='utf-8'
        )
        error_handler.setFormatter(StructuredFormatter('json'))
        error_handler.setLevel(logging.ERROR)
        error_handler.addFilter(SensitiveDataFilter())
        
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredFormatter('text'))
        console_handler.addFilter(SensitiveDataFilter())
        
        # Configurar logger root
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.addHandler(general_handler)
        root_logger.addHandler(error_handler)
        
        if config.logging['console_enabled']:
            root_logger.addHandler(console_handler)
    
    def get_logger(self, category: LogCategory, name: str = None) -> logging.Logger:
        """Obtém um logger para uma categoria específica"""
        
        logger_name = f"eron.{category.value}"
        if name:
            logger_name += f".{name}"
        
        if logger_name not in self.loggers:
            logger = logging.getLogger(logger_name)
            
            # Configurar logger específico da categoria se necessário
            if category == LogCategory.DATABASE:
                db_handler = logging.handlers.RotatingFileHandler(
                    Path(config.logging['dir']) / "eron_database.log",
                    maxBytes=config.logging['max_size_bytes'] // 2,
                    backupCount=5,
                    encoding='utf-8'
                )
                db_handler.setFormatter(StructuredFormatter('text'))
                db_handler.addFilter(SensitiveDataFilter())
                logger.addHandler(db_handler)
            
            elif category == LogCategory.TELEGRAM:
                tg_handler = logging.handlers.RotatingFileHandler(
                    Path(config.logging['dir']) / "eron_telegram.log",
                    maxBytes=config.logging['max_size_bytes'],
                    backupCount=3,
                    encoding='utf-8'
                )
                tg_handler.setFormatter(StructuredFormatter('text'))
                tg_handler.addFilter(SensitiveDataFilter())
                logger.addHandler(tg_handler)
            
            self.loggers[logger_name] = logger
        
        return self.loggers[logger_name]
    
    def log_performance(self, category: LogCategory, operation: str, 
                       execution_time: float, details: Dict[str, Any] = None):
        """Log específico para métricas de performance"""
        
        logger = self.get_logger(category, "performance")
        
        extra = {
            'category': f"{category.value}_performance",
            'execution_time': execution_time
        }
        
        details_str = ""
        if details:
            details_str = f" - {json.dumps(details, ensure_ascii=False)}"
        
        logger.info(
            f"PERFORMANCE: {operation} executado em {execution_time:.2f}ms{details_str}",
            extra=extra
        )
    
    def log_user_interaction(self, user_id: int, chat_id: int, action: str, 
                           details: Dict[str, Any] = None):
        """Log específico para interações de usuário"""
        
        logger = self.get_logger(LogCategory.TELEGRAM, "user_interaction")
        
        extra = {
            'category': 'user_interaction',
            'user_id': user_id,
            'chat_id': chat_id
        }
        
        details_str = ""
        if details:
            details_str = f" - {json.dumps(details, ensure_ascii=False)}"
        
        logger.info(f"USER_ACTION: {action}{details_str}", extra=extra)
    
    def log_llm_interaction(self, model: str, tokens_used: int, 
                           response_time: float, prompt_type: str):
        """Log específico para interações com LLM"""
        
        logger = self.get_logger(LogCategory.LLM, "interaction")
        
        extra = {
            'category': 'llm_interaction',
            'execution_time': response_time
        }
        
        logger.info(
            f"LLM_CALL: model={model}, tokens={tokens_used}, "
            f"time={response_time:.2f}ms, type={prompt_type}",
            extra=extra
        )
    
    def log_security_event(self, event_type: str, severity: str, 
                          details: Dict[str, Any], user_id: int = None):
        """Log específico para eventos de segurança"""
        
        logger = self.get_logger(LogCategory.SECURITY, "events")
        
        extra = {
            'category': 'security_event',
            'user_id': user_id
        }
        
        level_map = {
            'low': logging.INFO,
            'medium': logging.WARNING,
            'high': logging.ERROR,
            'critical': logging.CRITICAL
        }
        
        level = level_map.get(severity.lower(), logging.WARNING)
        
        logger.log(
            level,
            f"SECURITY: {event_type} - {json.dumps(details, ensure_ascii=False)}",
            extra=extra
        )
    
    def cleanup_old_logs(self):
        """Remove logs antigos baseado na configuração"""
        
        log_dir = Path(config.logging['dir'])
        if not log_dir.exists():
            return
        
        current_time = datetime.now()
        max_age_days = config.logging['max_age_days']
        
        for log_file in log_dir.glob("*.log*"):
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                age_days = (current_time - file_time).days
                
                if age_days > max_age_days:
                    log_file.unlink()
                    print(f"Arquivo de log antigo removido: {log_file}")
            
            except Exception as e:
                print(f"Erro ao limpar log {log_file}: {e}")


# Instância global do sistema de logging
logger_system = EronLogger()


def get_logger(category: LogCategory, name: str = None) -> logging.Logger:
    """Função conveniente para obter um logger"""
    return logger_system.get_logger(category, name)


def log_performance(category: LogCategory, operation: str, 
                   execution_time: float, details: Dict[str, Any] = None):
    """Função conveniente para log de performance"""
    logger_system.log_performance(category, operation, execution_time, details)


def log_user_interaction(user_id: int, chat_id: int, action: str, 
                        details: Dict[str, Any] = None):
    """Função conveniente para log de interação do usuário"""
    logger_system.log_user_interaction(user_id, chat_id, action, details)


def log_llm_interaction(model: str, tokens_used: int, 
                       response_time: float, prompt_type: str):
    """Função conveniente para log de LLM"""
    logger_system.log_llm_interaction(model, tokens_used, response_time, prompt_type)


def log_security_event(event_type: str, severity: str, 
                      details: Dict[str, Any], user_id: int = None):
    """Função conveniente para log de segurança"""
    logger_system.log_security_event(event_type, severity, details, user_id)


# Exemplo de uso
if __name__ == "__main__":
    print("🔧 TESTANDO SISTEMA DE LOGGING")
    print("=" * 50)
    
    # Teste básico
    general_logger = get_logger(LogCategory.GENERAL)
    general_logger.info("Sistema de logging inicializado com sucesso!")
    
    # Teste de performance
    log_performance(
        LogCategory.LLM, 
        "generate_response", 
        1250.5, 
        {"tokens": 150, "model": "llama"}
    )
    
    # Teste de interação
    log_user_interaction(
        12345, 
        67890, 
        "send_message", 
        {"message_length": 45, "command": "/start"}
    )
    
    # Teste de segurança
    log_security_event(
        "failed_login_attempt", 
        "medium",
        {"attempts": 3, "ip": "192.168.1.1"},
        user_id=12345
    )
    
    print("✅ Testes concluídos! Verifique os logs em:", config.logging['dir'])