"""
Validadores
Classes e funções para validação de dados
"""
import re
import os
from typing import Optional, List, Union, Dict, Any
from datetime import datetime

class EmailValidator:
    """Validador de emails"""
    
    def __init__(self):
        # Regex mais robusto para validação de email
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        # Domínios comuns para verificação adicional
        self.common_domains = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'live.com', 'icloud.com', 'protonmail.com', 'uol.com.br',
            'terra.com.br', 'ig.com.br', 'globo.com', 'bol.com.br'
        }
    
    def is_valid(self, email: str) -> bool:
        """Verificar se email é válido"""
        if not email or not isinstance(email, str):
            return False
        
        email = email.strip().lower()
        
        # Verificação básica de formato
        if not self.email_pattern.match(email):
            return False
        
        # Verificações adicionais
        local_part, domain = email.rsplit('@', 1)
        
        # Local part não pode ser muito longo
        if len(local_part) > 64:
            return False
        
        # Domain não pode ser muito longo
        if len(domain) > 253:
            return False
        
        # Verificar caracteres especiais
        if '..' in email or email.startswith('.') or email.endswith('.'):
            return False
        
        return True
    
    def suggest_corrections(self, email: str) -> List[str]:
        """Sugerir correções para emails com erros comuns"""
        if not email:
            return []
        
        suggestions = []
        email = email.strip().lower()
        
        # Correções de domínios comuns
        domain_corrections = {
            'gmail.co': 'gmail.com',
            'gmail.cm': 'gmail.com',
            'gmai.com': 'gmail.com',
            'gmial.com': 'gmail.com',
            'yahoo.co': 'yahoo.com',
            'yahoo.cm': 'yahoo.com',
            'hotmai.com': 'hotmail.com',
            'hotmial.com': 'hotmail.com'
        }
        
        if '@' in email:
            local_part, domain = email.rsplit('@', 1)
            
            for wrong_domain, correct_domain in domain_corrections.items():
                if domain == wrong_domain:
                    suggestions.append(f"{local_part}@{correct_domain}")
        
        return suggestions

class InputValidator:
    """Validador de entrada geral"""
    
    def __init__(self):
        # Padrões comuns
        self.patterns = {
            'phone_br': re.compile(r'^\(\d{2}\)\s\d{4,5}-\d{4}$'),
            'cpf': re.compile(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$'),
            'url': re.compile(r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.]*))?(?:\#(?:[\w.]*))?)?$')
        }
    
    def is_safe_string(self, text: str, max_length: int = 1000) -> bool:
        """Verificar se string é segura (sem caracteres perigosos)"""
        if not isinstance(text, str):
            return False
        
        if len(text) > max_length:
            return False
        
        # Caracteres perigosos
        dangerous_chars = ['<script', '</script>', '<iframe', 'javascript:', 'data:', 'vbscript:']
        text_lower = text.lower()
        
        return not any(char in text_lower for char in dangerous_chars)
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validar força da senha"""
        result = {
            'is_strong': False,
            'score': 0,
            'feedback': []
        }
        
        if not password:
            result['feedback'].append("Senha não pode estar vazia")
            return result
        
        # Critérios de avaliação
        criteria = {
            'length': len(password) >= 8,
            'lowercase': bool(re.search(r'[a-z]', password)),
            'uppercase': bool(re.search(r'[A-Z]', password)),
            'numbers': bool(re.search(r'\d', password)),
            'special_chars': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        }
        
        # Calcular score
        result['score'] = sum(criteria.values())
        
        # Feedback
        if not criteria['length']:
            result['feedback'].append("Deve ter pelo menos 8 caracteres")
        if not criteria['lowercase']:
            result['feedback'].append("Deve conter letras minúsculas")
        if not criteria['uppercase']:
            result['feedback'].append("Deve conter letras maiúsculas")
        if not criteria['numbers']:
            result['feedback'].append("Deve conter números")
        if not criteria['special_chars']:
            result['feedback'].append("Deve conter caracteres especiais")
        
        # Verificar padrões comuns
        common_patterns = [
            '123456', 'password', 'qwerty', 'abc123', 
            '111111', '000000', 'admin', 'login'
        ]
        
        if password.lower() in common_patterns:
            result['feedback'].append("Não use senhas comuns")
            result['score'] = 0
        
        result['is_strong'] = result['score'] >= 4 and len(result['feedback']) == 0
        
        return result
    
    def validate_phone_number(self, phone: str, country: str = 'BR') -> bool:
        """Validar número de telefone"""
        if not phone:
            return False
        
        # Remover caracteres não numéricos para validação básica
        digits_only = re.sub(r'\D', '', phone)
        
        if country == 'BR':
            # Brasil: 10 ou 11 dígitos (com DDD)
            if len(digits_only) in [10, 11]:
                # Verificar se DDD é válido (11-99)
                ddd = int(digits_only[:2])
                return 11 <= ddd <= 99
        
        return False
    
    def validate_url(self, url: str) -> bool:
        """Validar URL"""
        if not url:
            return False
        
        return self.patterns['url'].match(url) is not None
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitizar nome de arquivo"""
        if not filename:
            return "file"
        
        # Remover caracteres perigosos
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        
        # Remover espaços extras
        sanitized = re.sub(r'\s+', '_', sanitized.strip())
        
        # Limitar tamanho
        if len(sanitized) > 100:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:90] + ext
        
        return sanitized or "file"

class FileValidator:
    """Validador de arquivos"""
    
    def __init__(self):
        # Tipos MIME permitidos por categoria
        self.allowed_types = {
            'images': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            'documents': ['application/pdf', 'text/plain', 'application/msword'],
            'audio': ['audio/mpeg', 'audio/wav', 'audio/ogg'],
            'video': ['video/mp4', 'video/avi', 'video/webm']
        }
        
        # Extensões correspondentes
        self.allowed_extensions = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
            'documents': ['.pdf', '.txt', '.doc', '.docx'],
            'audio': ['.mp3', '.wav', '.ogg'],
            'video': ['.mp4', '.avi', '.webm']
        }
        
        # Tamanhos máximos (em bytes)
        self.max_sizes = {
            'images': 5 * 1024 * 1024,  # 5MB
            'documents': 10 * 1024 * 1024,  # 10MB
            'audio': 50 * 1024 * 1024,  # 50MB
            'video': 100 * 1024 * 1024  # 100MB
        }
    
    def validate_file(self, file_path: str, category: str = 'images') -> Dict[str, Any]:
        """Validar arquivo"""
        result = {
            'is_valid': False,
            'errors': [],
            'file_info': {}
        }
        
        if not os.path.exists(file_path):
            result['errors'].append("Arquivo não encontrado")
            return result
        
        # Informações básicas do arquivo
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        result['file_info'] = {
            'name': file_name,
            'size': file_size,
            'extension': file_ext
        }
        
        # Verificar categoria válida
        if category not in self.allowed_extensions:
            result['errors'].append(f"Categoria '{category}' não suportada")
            return result
        
        # Verificar extensão
        if file_ext not in self.allowed_extensions[category]:
            allowed = ', '.join(self.allowed_extensions[category])
            result['errors'].append(f"Extensão não permitida. Use: {allowed}")
        
        # Verificar tamanho
        max_size = self.max_sizes[category]
        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            result['errors'].append(f"Arquivo muito grande. Máximo: {max_size_mb}MB")
        
        # Verificar se arquivo está vazio
        if file_size == 0:
            result['errors'].append("Arquivo está vazio")
        
        result['is_valid'] = len(result['errors']) == 0
        
        return result
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Obter informações detalhadas do arquivo"""
        if not os.path.exists(file_path):
            return {}
        
        stat = os.stat(file_path)
        
        return {
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'extension': os.path.splitext(file_path)[1].lower(),
            'is_file': os.path.isfile(file_path),
            'is_readable': os.access(file_path, os.R_OK),
            'is_writable': os.access(file_path, os.W_OK)
        }

# Funções de conveniência
def validate_email(email: str) -> bool:
    """Função de conveniência para validação de email"""
    validator = EmailValidator()
    return validator.is_valid(email)

def validate_password(password: str) -> Dict[str, Any]:
    """Função de conveniência para validação de senha"""
    validator = InputValidator()
    return validator.validate_password_strength(password)

def is_safe_input(text: str, max_length: int = 1000) -> bool:
    """Função de conveniência para verificar entrada segura"""
    validator = InputValidator()
    return validator.is_safe_string(text, max_length)