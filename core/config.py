#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERON.IA - SISTEMA DE CONFIGURAÇÃO CENTRALIZADO
===============================================

Arquivo de configuração unificado para todo o sistema.
Centraliza tokens, URLs, configurações de banco de dados,
e outras variáveis de ambiente.

Autor: Sistema Eron.IA
Data: 21/09/2025
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class EronConfig:
    """
    Classe principal de configuração do sistema Eron.IA
    Centraliza todas as configurações em um local único
    """
    
    def __init__(self):
        """Inicializa as configurações do sistema"""
        self.base_dir = Path(__file__).parent.absolute()
        self._load_configurations()
    
    def _load_configurations(self):
        """Carrega todas as configurações do sistema"""
        # Configurações do Telegram Bot
        self.telegram = {
            'token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
            'webhook_url': os.getenv('TELEGRAM_WEBHOOK_URL', ''),
            'max_concurrent_updates': int(os.getenv('TELEGRAM_MAX_CONCURRENT', '100')),
            'timeout': int(os.getenv('TELEGRAM_TIMEOUT', '30')),
            'pool_timeout': int(os.getenv('TELEGRAM_POOL_TIMEOUT', '1')),
            'connection_pool_size': int(os.getenv('TELEGRAM_POOL_SIZE', '8'))
        }
        
        # Configurações do Flask/Web App
        self.web = {
            'host': os.getenv('WEB_HOST', '127.0.0.1'),
            'port': int(os.getenv('WEB_PORT', '5000')),
            'debug': os.getenv('WEB_DEBUG', 'True').lower() == 'true',
            'secret_key': os.getenv('WEB_SECRET_KEY', 'eron-secret-key-2025'),
            'session_permanent': os.getenv('SESSION_PERMANENT', 'False').lower() == 'true',
            'session_lifetime_hours': int(os.getenv('SESSION_LIFETIME', '24'))
        }
        
        # Configurações da API LLM
        self.llm = {
            'base_url': os.getenv('LLM_BASE_URL', 'http://127.0.0.1:1234/v1'),
            'api_key': os.getenv('LLM_API_KEY', 'lm-studio'),
            'model_name': os.getenv('LLM_MODEL_NAME', 'lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF'),
            'max_tokens': int(os.getenv('LLM_MAX_TOKENS', '2048')),
            'temperature': float(os.getenv('LLM_TEMPERATURE', '0.7')),
            'timeout': int(os.getenv('LLM_TIMEOUT', '120'))
        }
        
        # Configurações dos bancos de dados
        self.database = {
            'memoria_path': self.base_dir / 'memoria' / 'eron_memory.db',
            'emotions_path': self.base_dir / 'memoria' / 'emotions.db',
            'knowledge_path': self.base_dir / 'memoria' / 'knowledge.db',
            'preferences_path': self.base_dir / 'memoria' / 'preferences.db',
            'user_profiles_path': self.base_dir / 'memoria' / 'user_profiles.db',
            'sensitive_memory_path': self.base_dir / 'memoria' / 'sensitive_memory.db',
            'sensitive_key_path': self.base_dir / 'memoria' / 'sensitive.key',
            'backup_interval_hours': int(os.getenv('DB_BACKUP_INTERVAL', '24')),
            'max_backups': int(os.getenv('DB_MAX_BACKUPS', '7'))
        }
        
        # Configurações do sistema adulto (18+)
        self.adult_system = {
            'enabled': os.getenv('ADULT_SYSTEM_ENABLED', 'True').lower() == 'true',
            'min_age': int(os.getenv('ADULT_MIN_AGE', '18')),
            'content_path': self.base_dir / 'outros' / 'adult_responses.csv',
            'max_intensity': int(os.getenv('ADULT_MAX_INTENSITY', '10')),
            'default_intensity': int(os.getenv('ADULT_DEFAULT_INTENSITY', '5'))
        }
        
        # Configurações de email
        self.email = {
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
            'username': os.getenv('EMAIL_USERNAME', ''),
            'password': os.getenv('EMAIL_PASSWORD', ''),
            'from_email': os.getenv('EMAIL_FROM', 'noreply@eron-ia.com'),
            'use_tls': os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
        }
        
        # Configurações de logging (Sistema robusto)
        self.logging = {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'format': os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            'file_enabled': os.getenv('LOG_FILE_ENABLED', 'True').lower() == 'true',
            'file_path': self.base_dir / 'logs' / 'eron.log',
            'max_file_size_mb': int(os.getenv('LOG_MAX_SIZE_MB', '10')),
            'backup_count': int(os.getenv('LOG_BACKUP_COUNT', '5')),
            'console_enabled': os.getenv('LOG_CONSOLE_ENABLED', 'True').lower() == 'true',
            
            # Configurações avançadas do sistema de logging
            'dir': str(self.base_dir / 'logs'),
            'max_size_bytes': int(os.getenv('LOG_MAX_SIZE', '10485760')),  # 10MB
            'structured_format': os.getenv('LOG_STRUCTURED', 'True').lower() == 'true',
            'filter_sensitive_data': os.getenv('LOG_FILTER_SENSITIVE', 'True').lower() == 'true',
            'max_age_days': int(os.getenv('LOG_MAX_AGE_DAYS', '30')),
            'performance_logging': os.getenv('LOG_PERFORMANCE', 'True').lower() == 'true',
            'user_interaction_logging': os.getenv('LOG_USER_INTERACTIONS', 'True').lower() == 'true',
            'security_logging': os.getenv('LOG_SECURITY_EVENTS', 'True').lower() == 'true'
        }
        
        # Configurações de segurança
        self.security = {
            'max_login_attempts': int(os.getenv('SECURITY_MAX_LOGIN_ATTEMPTS', '5')),
            'lockout_duration_minutes': int(os.getenv('SECURITY_LOCKOUT_DURATION', '15')),
            'password_min_length': int(os.getenv('SECURITY_PASSWORD_MIN_LENGTH', '8')),
            'require_password_complexity': os.getenv('SECURITY_REQUIRE_COMPLEXITY', 'True').lower() == 'true',
            'session_timeout_minutes': int(os.getenv('SECURITY_SESSION_TIMEOUT', '60'))
        }
        
        # Configurações de moderação de conteúdo adulto
        self.moderation = {
            'enabled': os.getenv('ADULT_MODERATION_ENABLED', 'True').lower() == 'true',
            'sensitivity': os.getenv('MODERATION_SENSITIVITY', 'medium'),
            'auto_warn_mild': os.getenv('AUTO_WARN_MILD', 'True').lower() == 'true',
            'auto_filter_moderate': os.getenv('AUTO_FILTER_MODERATE', 'True').lower() == 'true',
            'auto_block_severe': os.getenv('AUTO_BLOCK_SEVERE', 'True').lower() == 'true',
            'quarantine_duration_hours': int(os.getenv('QUARANTINE_DURATION_HOURS', '24')),
            'block_duration_hours': int(os.getenv('BLOCK_DURATION_HOURS', '72')),
            'max_violations_quarantine': int(os.getenv('MAX_VIOLATIONS_BEFORE_QUARANTINE', '3')),
            'max_violations_block': int(os.getenv('MAX_VIOLATIONS_BEFORE_BLOCK', '5')),
            'max_violations_ban': int(os.getenv('MAX_VIOLATIONS_BEFORE_BAN', '10')),
            'content_cache_duration_hours': int(os.getenv('CONTENT_CACHE_DURATION_HOURS', '24')),
            'logs_retention_days': int(os.getenv('MODERATION_LOGS_RETENTION_DAYS', '90'))
        }
        
        # Configurações de performance
        self.performance = {
            'cache_enabled': os.getenv('CACHE_ENABLED', 'True').lower() == 'true',
            'cache_max_size': int(os.getenv('CACHE_MAX_SIZE', '1000')),
            'cache_ttl_seconds': int(os.getenv('CACHE_TTL', '3600')),
            'max_concurrent_requests': int(os.getenv('MAX_CONCURRENT_REQUESTS', '50')),
            'request_timeout_seconds': int(os.getenv('REQUEST_TIMEOUT', '30'))
        }
        
        # Configurações do sistema de aprendizagem
        self.learning = {
            'fast_learning_enabled': os.getenv('FAST_LEARNING_ENABLED', 'True').lower() == 'true',
            'human_conversation_enabled': os.getenv('HUMAN_CONVERSATION_ENABLED', 'True').lower() == 'true',
            'advanced_adult_learning_enabled': os.getenv('ADVANCED_ADULT_LEARNING_ENABLED', 'True').lower() == 'true',
            'max_conversation_history': int(os.getenv('MAX_CONVERSATION_HISTORY', '100')),
            'learning_data_retention_days': int(os.getenv('LEARNING_DATA_RETENTION', '365'))
        }
    
    def get_config(self, section: str, key: Optional[str] = None) -> Any:
        """
        Obtém uma configuração específica
        
        Args:
            section: Seção da configuração (telegram, web, llm, etc.)
            key: Chave específica dentro da seção (opcional)
        
        Returns:
            Valor da configuração ou dicionário da seção completa
        """
        if not hasattr(self, section):
            raise ValueError(f"Seção de configuração '{section}' não encontrada")
        
        section_config = getattr(self, section)
        
        if key is None:
            return section_config
        
        if key not in section_config:
            raise ValueError(f"Chave '{key}' não encontrada na seção '{section}'")
        
        return section_config[key]
    
    def validate_required_configs(self) -> Dict[str, list]:
        """
        Valida se todas as configurações obrigatórias estão definidas
        
        Returns:
            Dicionário com configurações faltantes por seção
        """
        missing_configs = {}
        
        # Configurações obrigatórias do Telegram
        if not self.telegram['token']:
            missing_configs.setdefault('telegram', []).append('token')
        
        # Configurações obrigatórias do LLM
        if not self.llm['base_url']:
            missing_configs.setdefault('llm', []).append('base_url')
        
        # Configurações obrigatórias de email (se sistema de email habilitado)
        if self.email['username'] and not self.email['password']:
            missing_configs.setdefault('email', []).append('password')
        
        return missing_configs
    
    def create_directories(self):
        """Cria os diretórios necessários se não existirem"""
        directories = [
            self.base_dir / 'memoria',
            self.base_dir / 'logs',
            self.base_dir / 'backup',
            self.base_dir / 'temp',
            self.base_dir / 'outros'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_database_urls(self) -> Dict[str, str]:
        """Retorna URLs de conexão dos bancos de dados"""
        return {
            'memoria': f"sqlite:///{self.database['memoria_path']}",
            'emotions': f"sqlite:///{self.database['emotions_path']}",
            'knowledge': f"sqlite:///{self.database['knowledge_path']}",
            'preferences': f"sqlite:///{self.database['preferences_path']}",
            'user_profiles': f"sqlite:///{self.database['user_profiles_path']}",
            'sensitive_memory': f"sqlite:///{self.database['sensitive_memory_path']}"
        }
    
    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção"""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'production'
    
    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento"""
        return not self.is_production()
    
    def get_version(self) -> str:
        """Retorna a versão do sistema"""
        return os.getenv('ERON_VERSION', '2.0.0')
    
    def print_config_summary(self):
        """Imprime um resumo das configurações carregadas"""
        print("🔧 ERON.IA - CONFIGURAÇÕES CARREGADAS")
        print("=" * 50)
        print(f"📍 Diretório base: {self.base_dir}")
        print(f"🔢 Versão: {self.get_version()}")
        print(f"🌐 Ambiente: {'Produção' if self.is_production() else 'Desenvolvimento'}")
        print(f"🤖 Telegram Token: {'✅ Configurado' if self.telegram['token'] else '❌ Não configurado'}")
        print(f"🌐 Web Host: {self.web['host']}:{self.web['port']}")
        print(f"🧠 LLM URL: {self.llm['base_url']}")
        print(f"🔞 Sistema Adulto: {'✅ Habilitado' if self.adult_system['enabled'] else '❌ Desabilitado'}")
        print(f"📊 Logging: {'✅ Habilitado' if self.logging['file_enabled'] else '❌ Desabilitado'}")
        print("=" * 50)

# Instância global de configuração
config = EronConfig()

# Função de conveniência para obter configurações
def get_config(section: str, key: Optional[str] = None) -> Any:
    """
    Função helper para obter configurações
    
    Args:
        section: Seção da configuração
        key: Chave específica (opcional)
    
    Returns:
        Valor da configuração
    """
    return config.get_config(section, key)

# Validação automática na importação
if __name__ == "__main__":
    config.create_directories()
    config.print_config_summary()
    
    missing = config.validate_required_configs()
    if missing:
        print("⚠️ CONFIGURAÇÕES FALTANTES:")
        for section, keys in missing.items():
            print(f"  {section}: {', '.join(keys)}")
    else:
        print("✅ Todas as configurações obrigatórias estão definidas!")