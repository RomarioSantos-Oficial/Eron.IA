"""
Serviços Centrais Compartilhados
Configuração, segurança e logging unificados
"""
import os
import json
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet
import sqlite3

class ConfigService:
    """Serviço de configuração centralizado"""
    
    def __init__(self, config_file: Optional[str] = None):
        if config_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_file = os.path.join(base_dir, 'config.json')
        
        self.config_file = config_file
        self._config_cache = {}
        self._default_config = {
            'app': {
                'name': 'Eron.IA',
                'version': '2.0.0',
                'debug': False,
                'port': 5000,
                'host': '0.0.0.0'
            },
            'telegram': {
                'token': '',
                'webhook_url': '',
                'max_connections': 100
            },
            'ai': {
                'model': 'Qwen2.5-4B',
                'max_tokens': 2048,
                'temperature': 0.7,
                'top_p': 0.9
            },
            'learning': {
                'enabled': True,
                'learning_rate': 0.1,
                'min_confidence': 0.6,
                'adaptation_threshold': 0.7
            },
            'security': {
                'secret_key': '',
                'encryption_enabled': True,
                'session_timeout': 1800,
                'max_login_attempts': 5
            },
            'database': {
                'backup_enabled': True,
                'backup_interval_hours': 24,
                'cleanup_days': 90
            }
        }
        self.load_config()
    
    def load_config(self):
        """Carregar configurações do arquivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._config_cache = self._merge_configs(self._default_config, file_config)
            else:
                # Criar arquivo de configuração com padrões
                self._config_cache = self._default_config.copy()
                self.save_config()
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
            self._config_cache = self._default_config.copy()
    
    def save_config(self):
        """Salvar configurações no arquivo"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
    
    def _merge_configs(self, default: Dict, custom: Dict) -> Dict:
        """Mesclar configurações mantendo estrutura padrão"""
        merged = default.copy()
        
        for key, value in custom.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Obter valor de configuração usando path com pontos"""
        keys = key_path.split('.')
        current = self._config_cache
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Definir valor de configuração"""
        keys = key_path.split('.')
        current = self._config_cache
        
        # Navegar até o último nível
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Definir valor
        current[keys[-1]] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Obter seção completa de configuração"""
        return self._config_cache.get(section, {})
    
    def update_section(self, section: str, values: Dict[str, Any]):
        """Atualizar seção de configuração"""
        if section not in self._config_cache:
            self._config_cache[section] = {}
        
        self._config_cache[section].update(values)
    
    def reload(self):
        """Recarregar configurações do arquivo"""
        self.load_config()
    
    def reset_to_defaults(self):
        """Resetar para configurações padrão"""
        self._config_cache = self._default_config.copy()
        self.save_config()

class SecurityService:
    """Serviço de segurança centralizado"""
    
    def __init__(self, key_file: Optional[str] = None):
        if key_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            key_file = os.path.join(base_dir, 'database', 'security.key')
        
        self.key_file = key_file
        self._cipher = None
        self._load_or_create_key()
        
        # Rastreamento de tentativas de login
        self._login_attempts = {}
    
    def _load_or_create_key(self):
        """Carregar ou criar chave de criptografia"""
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f:
                    key = f.read()
            else:
                # Gerar nova chave
                key = Fernet.generate_key()
                os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
                with open(self.key_file, 'wb') as f:
                    f.write(key)
            
            self._cipher = Fernet(key)
        except Exception as e:
            print(f"Erro ao configurar criptografia: {e}")
            # Usar chave temporária se houver erro
            self._cipher = Fernet(Fernet.generate_key())
    
    def encrypt(self, data: str) -> str:
        """Criptografar string"""
        try:
            encrypted = self._cipher.encrypt(data.encode('utf-8'))
            return encrypted.decode('utf-8')
        except Exception as e:
            print(f"Erro ao criptografar: {e}")
            return data  # Retornar original se criptografia falhar
    
    def decrypt(self, encrypted_data: str) -> str:
        """Descriptografar string"""
        try:
            decrypted = self._cipher.decrypt(encrypted_data.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"Erro ao descriptografar: {e}")
            return encrypted_data  # Retornar original se falhar
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Gerar hash de senha com salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Usar PBKDF2 para hash seguro
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100k iterações
        )
        
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verificar senha contra hash"""
        try:
            computed_hash, _ = self.hash_password(password, salt)
            return secrets.compare_digest(computed_hash, password_hash)
        except Exception:
            return False
    
    def generate_session_token(self) -> str:
        """Gerar token de sessão seguro"""
        return secrets.token_urlsafe(32)
    
    def generate_api_key(self) -> str:
        """Gerar chave de API"""
        return secrets.token_urlsafe(48)
    
    def sanitize_input(self, user_input: str) -> str:
        """Sanitizar entrada do usuário"""
        # Remover caracteres perigosos
        dangerous_chars = ['<', '>', '"', "'", '&', '\0']
        sanitized = user_input
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Limitar tamanho
        return sanitized[:1000]  # Máximo 1000 caracteres
    
    def check_rate_limit(self, user_id: str, action: str, max_attempts: int = 10, 
                        window_minutes: int = 60) -> bool:
        """Verificar limite de taxa de ações"""
        current_time = datetime.now()
        key = f"{user_id}_{action}"
        
        if key not in self._login_attempts:
            self._login_attempts[key] = []
        
        # Remover tentativas antigas
        cutoff_time = current_time - timedelta(minutes=window_minutes)
        self._login_attempts[key] = [
            timestamp for timestamp in self._login_attempts[key]
            if timestamp > cutoff_time
        ]
        
        # Verificar se excedeu limite
        if len(self._login_attempts[key]) >= max_attempts:
            return False
        
        # Registrar nova tentativa
        self._login_attempts[key].append(current_time)
        return True
    
    def validate_email(self, email: str) -> bool:
        """Validar formato de email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def generate_secure_filename(self, original_filename: str) -> str:
        """Gerar nome de arquivo seguro"""
        # Manter apenas caracteres alfanuméricos e pontos
        import re
        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '', original_filename)
        
        # Adicionar timestamp para unicidade
        timestamp = int(datetime.now().timestamp())
        name, ext = os.path.splitext(safe_name)
        
        return f"{name}_{timestamp}{ext}"
    
    def create_audit_log_entry(self, user_id: str, action: str, details: Dict[str, Any]):
        """Criar entrada de log de auditoria"""
        # Esta função seria integrada com o sistema de logging
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'details': details,
            'ip_address': details.get('ip_address', 'unknown')
        }
        
        # Aqui seria salvo no banco ou arquivo de auditoria
        return log_entry

class LoggingService:
    """Serviço de logging centralizado"""
    
    def __init__(self, log_dir: Optional[str] = None):
        if log_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_dir = os.path.join(base_dir, 'logs')
        
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Configurar loggers
        self._setup_loggers()
    
    def _setup_loggers(self):
        """Configurar sistema de logging"""
        # Logger principal da aplicação
        self.app_logger = logging.getLogger('eron_app')
        self.app_logger.setLevel(logging.INFO)
        
        # Logger para sistema de aprendizado
        self.learning_logger = logging.getLogger('eron_learning')
        self.learning_logger.setLevel(logging.DEBUG)
        
        # Logger para segurança
        self.security_logger = logging.getLogger('eron_security')
        self.security_logger.setLevel(logging.WARNING)
        
        # Configurar handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configurar handlers de logging"""
        # Formatter comum
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para arquivo principal
        app_handler = logging.FileHandler(
            os.path.join(self.log_dir, 'app.log'), 
            encoding='utf-8'
        )
        app_handler.setFormatter(formatter)
        self.app_logger.addHandler(app_handler)
        
        # Handler para aprendizado
        learning_handler = logging.FileHandler(
            os.path.join(self.log_dir, 'learning.log'),
            encoding='utf-8'
        )
        learning_handler.setFormatter(formatter)
        self.learning_logger.addHandler(learning_handler)
        
        # Handler para segurança
        security_handler = logging.FileHandler(
            os.path.join(self.log_dir, 'security.log'),
            encoding='utf-8'
        )
        security_handler.setFormatter(formatter)
        self.security_logger.addHandler(security_handler)
        
        # Handler para console (desenvolvimento)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.ERROR)
        
        self.app_logger.addHandler(console_handler)
        self.learning_logger.addHandler(console_handler)
        self.security_logger.addHandler(console_handler)
    
    def log_user_action(self, user_id: str, action: str, details: Optional[Dict] = None):
        """Registrar ação do usuário"""
        message = f"User {user_id} performed action: {action}"
        if details:
            message += f" - Details: {json.dumps(details)}"
        
        self.app_logger.info(message)
    
    def log_learning_event(self, user_id: str, event_type: str, data: Dict[str, Any]):
        """Registrar evento de aprendizado"""
        message = f"Learning event for user {user_id}: {event_type} - {json.dumps(data)}"
        self.learning_logger.info(message)
    
    def log_security_event(self, user_id: str, event: str, severity: str = 'warning', 
                          details: Optional[Dict] = None):
        """Registrar evento de segurança"""
        message = f"Security event for user {user_id}: {event}"
        if details:
            message += f" - {json.dumps(details)}"
        
        if severity == 'critical':
            self.security_logger.critical(message)
        elif severity == 'error':
            self.security_logger.error(message)
        else:
            self.security_logger.warning(message)
    
    def log_error(self, error: Exception, context: Optional[str] = None):
        """Registrar erro com contexto"""
        message = f"Error: {str(error)}"
        if context:
            message = f"{context} - {message}"
        
        self.app_logger.error(message, exc_info=True)
    
    def get_recent_logs(self, logger_name: str = 'app', lines: int = 100) -> List[str]:
        """Obter logs recentes"""
        log_file = os.path.join(self.log_dir, f'{logger_name}.log')
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except Exception:
            return []
    
    def cleanup_old_logs(self, days_old: int = 30):
        """Limpar logs antigos"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for log_file in os.listdir(self.log_dir):
            file_path = os.path.join(self.log_dir, log_file)
            
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_time < cutoff_date:
                    try:
                        os.remove(file_path)
                        self.app_logger.info(f"Removed old log file: {log_file}")
                    except Exception as e:
                        self.app_logger.error(f"Failed to remove log file {log_file}: {e}")

# Instâncias globais dos serviços
_config_service = None
_security_service = None
_logging_service = None

def get_config_service() -> ConfigService:
    """Obter instância global do serviço de configuração"""
    global _config_service
    if _config_service is None:
        _config_service = ConfigService()
    return _config_service

def get_security_service() -> SecurityService:
    """Obter instância global do serviço de segurança"""
    global _security_service
    if _security_service is None:
        _security_service = SecurityService()
    return _security_service

def get_logging_service() -> LoggingService:
    """Obter instância global do serviço de logging"""
    global _logging_service
    if _logging_service is None:
        _logging_service = LoggingService()
    return _logging_service
