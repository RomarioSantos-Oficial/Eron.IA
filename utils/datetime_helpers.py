"""
Helpers para Data e Hora
Utilitários para manipulação de timestamps e cálculos temporais
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
import locale

# Configurar locale para português (se disponível)
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
    except:
        pass  # Usar locale padrão se português não estiver disponível

def format_timestamp(timestamp: Union[datetime, str, float], 
                    format_type: str = 'friendly') -> str:
    """Formatar timestamp para exibição amigável"""
    
    # Converter para datetime se necessário
    if isinstance(timestamp, str):
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    elif isinstance(timestamp, float):
        dt = datetime.fromtimestamp(timestamp)
    else:
        dt = timestamp
    
    # Garantir timezone local se não especificada
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    
    if format_type == 'friendly':
        # Formato amigável baseado na diferença de tempo
        diff = now - dt
        
        if diff.total_seconds() < 60:
            return "agora há pouco"
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() // 60)
            return f"há {minutes} minuto{'s' if minutes > 1 else ''}"
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() // 3600)
            return f"há {hours} hora{'s' if hours > 1 else ''}"
        elif diff.days == 1:
            return "ontem às " + dt.strftime("%H:%M")
        elif diff.days < 7:
            days = ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado', 'domingo']
            return f"{days[dt.weekday()]} às {dt.strftime('%H:%M')}"
        else:
            return dt.strftime("%d/%m/%Y às %H:%M")
    
    elif format_type == 'short':
        return dt.strftime("%d/%m/%Y %H:%M")
    
    elif format_type == 'long':
        return dt.strftime("%A, %d de %B de %Y às %H:%M")
    
    elif format_type == 'iso':
        return dt.isoformat()
    
    else:
        # Formato personalizado
        return dt.strftime(format_type)

def calculate_time_ago(timestamp: Union[datetime, str, float]) -> str:
    """Calcular quanto tempo se passou desde o timestamp"""
    
    # Converter para datetime se necessário
    if isinstance(timestamp, str):
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    elif isinstance(timestamp, float):
        dt = datetime.fromtimestamp(timestamp)
    else:
        dt = timestamp
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    diff = now - dt
    
    seconds = int(diff.total_seconds())
    
    if seconds < 0:
        return "no futuro"
    elif seconds < 60:
        return f"{seconds} segundo{'s' if seconds != 1 else ''} atrás"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minuto{'s' if minutes != 1 else ''} atrás"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hora{'s' if hours != 1 else ''} atrás"
    elif seconds < 2592000:  # 30 days
        days = seconds // 86400
        return f"{days} dia{'s' if days != 1 else ''} atrás"
    elif seconds < 31536000:  # 365 days
        months = seconds // 2592000
        return f"{months} mês{'es' if months != 1 else ''} atrás"
    else:
        years = seconds // 31536000
        return f"{years} ano{'s' if years != 1 else ''} atrás"

def is_business_hours(timestamp: Optional[Union[datetime, str, float]] = None,
                     start_hour: int = 9, end_hour: int = 18,
                     weekdays_only: bool = True) -> bool:
    """Verificar se timestamp está em horário comercial"""
    
    if timestamp is None:
        dt = datetime.now()
    elif isinstance(timestamp, str):
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    elif isinstance(timestamp, float):
        dt = datetime.fromtimestamp(timestamp)
    else:
        dt = timestamp
    
    # Verificar dia da semana (0=segunda, 6=domingo)
    if weekdays_only and dt.weekday() >= 5:  # sábado ou domingo
        return False
    
    # Verificar horário
    return start_hour <= dt.hour < end_hour

def get_next_business_day(timestamp: Optional[Union[datetime, str, float]] = None) -> datetime:
    """Obter próximo dia útil"""
    
    if timestamp is None:
        dt = datetime.now()
    elif isinstance(timestamp, str):
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    elif isinstance(timestamp, float):
        dt = datetime.fromtimestamp(timestamp)
    else:
        dt = timestamp
    
    # Começar do próximo dia
    next_day = dt + timedelta(days=1)
    next_day = next_day.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Pular fins de semana
    while next_day.weekday() >= 5:  # sábado ou domingo
        next_day += timedelta(days=1)
    
    return next_day

def create_time_slots(start_time: datetime, end_time: datetime, 
                     duration_minutes: int = 30) -> list[datetime]:
    """Criar slots de tempo entre duas datas"""
    slots = []
    current = start_time
    duration = timedelta(minutes=duration_minutes)
    
    while current < end_time:
        slots.append(current)
        current += duration
    
    return slots

def parse_natural_time(time_text: str) -> Optional[datetime]:
    """Tentar parsear texto de tempo natural (básico)"""
    time_text = time_text.lower().strip()
    now = datetime.now()
    
    # Padrões básicos
    if time_text in ['agora', 'já', 'imediatamente']:
        return now
    elif time_text in ['amanhã', 'tomorrow']:
        return now + timedelta(days=1)
    elif time_text in ['ontem', 'yesterday']:
        return now - timedelta(days=1)
    elif 'próxima semana' in time_text:
        return now + timedelta(weeks=1)
    elif 'semana passada' in time_text:
        return now - timedelta(weeks=1)
    elif 'próximo mês' in time_text:
        return now + timedelta(days=30)
    elif 'mês passado' in time_text:
        return now - timedelta(days=30)
    
    # Tentar parsear formatos comuns
    formats = [
        '%d/%m/%Y %H:%M',
        '%d/%m/%Y',
        '%H:%M',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(time_text, fmt)
        except ValueError:
            continue
    
    return None

def get_timezone_offset() -> str:
    """Obter offset do timezone local"""
    now = datetime.now()
    utc_offset = now.astimezone().utcoffset()
    
    if utc_offset is None:
        return "+00:00"
    
    total_seconds = int(utc_offset.total_seconds())
    hours, remainder = divmod(abs(total_seconds), 3600)
    minutes = remainder // 60
    
    sign = '+' if total_seconds >= 0 else '-'
    return f"{sign}{hours:02d}:{minutes:02d}"

def duration_to_human_readable(seconds: Union[int, float]) -> str:
    """Converter duração em segundos para texto legível"""
    seconds = int(seconds)
    
    if seconds < 60:
        return f"{seconds} segundo{'s' if seconds != 1 else ''}"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds == 0:
            return f"{minutes} minuto{'s' if minutes != 1 else ''}"
        else:
            return f"{minutes}m {remaining_seconds}s"
    elif seconds < 86400:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        if remaining_minutes == 0:
            return f"{hours} hora{'s' if hours != 1 else ''}"
        else:
            return f"{hours}h {remaining_minutes}m"
    else:
        days = seconds // 86400
        remaining_hours = (seconds % 86400) // 3600
        if remaining_hours == 0:
            return f"{days} dia{'s' if days != 1 else ''}"
        else:
            return f"{days}d {remaining_hours}h"

def get_week_boundaries(date: Optional[datetime] = None) -> tuple[datetime, datetime]:
    """Obter início e fim da semana para uma data"""
    if date is None:
        date = datetime.now()
    
    # Início da semana (segunda-feira)
    start_of_week = date - timedelta(days=date.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Fim da semana (domingo)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)
    
    return start_of_week, end_of_week

def get_month_boundaries(date: Optional[datetime] = None) -> tuple[datetime, datetime]:
    """Obter início e fim do mês para uma data"""
    if date is None:
        date = datetime.now()
    
    # Início do mês
    start_of_month = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Fim do mês
    if date.month == 12:
        next_month = date.replace(year=date.year + 1, month=1, day=1)
    else:
        next_month = date.replace(month=date.month + 1, day=1)
    
    end_of_month = next_month - timedelta(microseconds=1)
    
    return start_of_month, end_of_month