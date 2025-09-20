"""
Funções Auxiliares Gerais
Utilitários diversos para todo o sistema
"""
import uuid
import time
import random
import string
import hashlib
import json
from typing import Any, Dict, Optional, Callable, List, Union
from functools import wraps
import traceback

def generate_id(prefix: str = '', length: int = 8) -> str:
    """Gerar ID único"""
    if prefix:
        # ID com prefixo e timestamp
        timestamp = int(time.time() * 1000)  # milliseconds
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        return f"{prefix}_{timestamp}_{random_part}"
    else:
        # UUID4 simples
        return str(uuid.uuid4())

def generate_short_id(length: int = 8) -> str:
    """Gerar ID curto alfanumérico"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Obter valor do dicionário de forma segura, suportando chaves aninhadas"""
    try:
        # Suportar chaves com pontos (ex: 'user.profile.name')
        keys = key.split('.')
        current = dictionary
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    except (TypeError, AttributeError):
        return default

def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """Parser JSON seguro"""
    try:
        if not json_string:
            return default
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = '{}') -> str:
    """Serializar JSON de forma segura"""
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return default

def retry_operation(max_attempts: int = 3, delay: float = 1.0, 
                   backoff_factor: float = 2.0, 
                   exceptions: tuple = (Exception,)):
    """Decorator para retry de operações com backoff exponencial"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:  # Última tentativa
                        raise last_exception
                    
                    # Wait before retry
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
            
            # Nunca deveria chegar aqui, mas por segurança
            raise last_exception
        
        return wrapper
    return decorator

def measure_time(func: Callable) -> Callable:
    """Decorator para medir tempo de execução"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            print(f"{func.__name__} executado em {execution_time:.4f} segundos")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"{func.__name__} falhou em {execution_time:.4f} segundos: {e}")
            raise
    
    return wrapper

def cache_result(ttl_seconds: int = 300):
    """Decorator para cache simples com TTL"""
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Criar chave do cache
            cache_key = str(args) + str(sorted(kwargs.items()))
            current_time = time.time()
            
            # Verificar se resultado está em cache e não expirou
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if current_time - timestamp < ttl_seconds:
                    return result
            
            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            
            # Limpeza básica do cache (remover entradas muito antigas)
            if len(cache) > 100:  # Limite básico
                expired_keys = [
                    k for k, (_, timestamp) in cache.items()
                    if current_time - timestamp > ttl_seconds * 2
                ]
                for k in expired_keys:
                    del cache[k]
            
            return result
        
        return wrapper
    return decorator

def flatten_dict(dictionary: Dict[str, Any], parent_key: str = '', 
                separator: str = '.') -> Dict[str, Any]:
    """Achatar dicionário aninhado"""
    items = []
    
    for key, value in dictionary.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, separator).items())
        else:
            items.append((new_key, value))
    
    return dict(items)

def unflatten_dict(dictionary: Dict[str, Any], separator: str = '.') -> Dict[str, Any]:
    """Reverter achatamento de dicionário"""
    result = {}
    
    for key, value in dictionary.items():
        keys = key.split(separator)
        current = result
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    return result

def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Mesclar dicionários recursivamente"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def calculate_hash(data: Union[str, bytes, Dict[str, Any]], 
                  algorithm: str = 'sha256') -> str:
    """Calcular hash de dados"""
    # Converter dados para bytes se necessário
    if isinstance(data, dict):
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        data_bytes = data_str.encode('utf-8')
    elif isinstance(data, str):
        data_bytes = data.encode('utf-8')
    else:
        data_bytes = data
    
    # Calcular hash
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data_bytes)
    
    return hash_obj.hexdigest()

def truncate_text(text: str, max_length: int = 100, 
                 suffix: str = '...') -> str:
    """Truncar texto preservando palavras"""
    if len(text) <= max_length:
        return text
    
    # Truncar no último espaço antes do limite
    truncated = text[:max_length - len(suffix)]
    
    # Encontrar último espaço
    last_space = truncated.rfind(' ')
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + suffix

def format_file_size(size_bytes: int) -> str:
    """Formatar tamanho de arquivo para leitura humana"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    size_bytes = float(size_bytes)
    
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def extract_error_info(exception: Exception) -> Dict[str, Any]:
    """Extrair informações detalhadas de uma exceção"""
    return {
        'type': type(exception).__name__,
        'message': str(exception),
        'traceback': traceback.format_exc(),
        'args': exception.args,
        'timestamp': time.time()
    }

def sanitize_dict_keys(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitizar chaves de dicionário (remover caracteres especiais)"""
    sanitized = {}
    
    for key, value in dictionary.items():
        # Sanitizar chave
        clean_key = ''.join(c for c in str(key) if c.isalnum() or c in '_-')
        
        # Processar valor recursivamente se for dict
        if isinstance(value, dict):
            value = sanitize_dict_keys(value)
        
        sanitized[clean_key] = value
    
    return sanitized

def batch_process(items: List[Any], batch_size: int = 100, 
                 processor: Callable = None) -> List[Any]:
    """Processar lista em lotes"""
    if processor is None:
        processor = lambda x: x
    
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = [processor(item) for item in batch]
        results.extend(batch_results)
    
    return results

def find_duplicates(items: List[Any]) -> List[Any]:
    """Encontrar itens duplicados em lista"""
    seen = set()
    duplicates = set()
    
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    
    return list(duplicates)

def remove_duplicates(items: List[Any], preserve_order: bool = True) -> List[Any]:
    """Remover duplicatas de lista"""
    if preserve_order:
        seen = set()
        result = []
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
    else:
        return list(set(items))

def get_nested_value(data: Union[Dict, List], path: str, 
                    separator: str = '.', default: Any = None) -> Any:
    """Obter valor aninhado usando path string"""
    try:
        current = data
        keys = path.split(separator)
        
        for key in keys:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list):
                current = current[int(key)]
            else:
                return default
        
        return current
    
    except (KeyError, IndexError, ValueError, TypeError):
        return default

def set_nested_value(data: Dict, path: str, value: Any, 
                    separator: str = '.') -> None:
    """Definir valor aninhado usando path string"""
    keys = path.split(separator)
    current = data
    
    # Navegar até o penúltimo nível
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    # Definir valor final
    current[keys[-1]] = value