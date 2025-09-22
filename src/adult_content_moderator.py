"""
Sistema de Feedback para Conteúdo Adulto - Eron.IA
==================================================

Sistema avançado de detecção, moderação e feedback para conteúdos adultos com:
- Detecção automática de conteúdo impróprio
- Sistema de moderação por níveis
- Feedback educativo para usuários  
- Relatórios de segurança
- Integração com logging e configuração
- Palavras-chave e padrões configuráveis
- Sistema de quarentena e bloqueio
- Analytics de comportamento

Autor: Eron.IA System
Data: 2024
"""

import re
import json
import time
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

try:
    from core.config import config
    from src.logging_system import get_logger, LogCategory, log_security_event
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from core.config import config
    from src.logging_system import get_logger, LogCategory, log_security_event


class ContentSeverity(Enum):
    """Níveis de severidade do conteúdo adulto"""
    CLEAN = "clean"          # Conteúdo limpo
    MILD = "mild"            # Levemente sugestivo
    MODERATE = "moderate"    # Moderadamente adulto
    SEVERE = "severe"        # Severamente adulto
    BLOCKED = "blocked"      # Bloqueado/banido


class ModerationAction(Enum):
    """Ações de moderação disponíveis"""
    ALLOW = "allow"          # Permitir conteúdo
    WARN = "warn"            # Avisar usuário
    FILTER = "filter"        # Filtrar/censurar conteúdo
    QUARANTINE = "quarantine" # Colocar em quarentena
    BLOCK = "block"          # Bloquear usuário temporariamente
    BAN = "ban"              # Banir usuário permanentemente


class AdultContentModerator:
    """Sistema principal de moderação de conteúdo adulto"""
    
    def __init__(self):
        self.logger = get_logger(LogCategory.SECURITY, "adult_content")
        self.db_path = Path(config.database['sensitive_memory_path']).parent / 'adult_moderation.db'
        self.patterns_db_path = Path(config.database['sensitive_memory_path']).parent / 'content_patterns.db'
        
        # Inicializar bancos de dados
        self._init_databases()
        
        # Carregar padrões e configurações
        self.load_patterns()
        
        # Estatísticas em memória
        self.stats = {
            'total_checks': 0,
            'blocks_today': 0,
            'warnings_today': 0,
            'last_reset': datetime.now().date()
        }
    
    def _init_databases(self):
        """Inicializa os bancos de dados necessários"""
        
        # Banco de moderação
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS moderation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    content_snippet TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    action_taken TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_violations (
                    user_id TEXT PRIMARY KEY,
                    violation_count INTEGER DEFAULT 0,
                    severe_violations INTEGER DEFAULT 0,
                    last_violation DATETIME,
                    status TEXT DEFAULT 'active',
                    quarantine_until DATETIME NULL,
                    ban_until DATETIME NULL,
                    warnings_sent INTEGER DEFAULT 0
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS content_cache (
                    content_hash TEXT PRIMARY KEY,
                    severity TEXT NOT NULL,
                    flagged_words TEXT,
                    confidence_score REAL,
                    last_checked DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        # Banco de padrões
        with sqlite3.connect(self.patterns_db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS content_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    is_regex BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            ''')
            
            # Inserir padrões padrão se tabela estiver vazia
            cursor = conn.execute('SELECT COUNT(*) FROM content_patterns')
            if cursor.fetchone()[0] == 0:
                self._insert_default_patterns(conn)
    
    def _insert_default_patterns(self, conn):
        """Insere padrões padrão no banco"""
        default_patterns = [
            # Padrões severos
            ('palavrão1|palavrão2|palavrão3', 'explicit', 'severe', True, 'Linguagem explícita'),
            ('sexo|sexual|xxx', 'sexual', 'moderate', False, 'Conteúdo sexual'),
            ('drogas|maconha|cocaína', 'drugs', 'severe', False, 'Referências a drogas'),
            
            # Padrões moderados
            ('maldito|droga|merda', 'profanity', 'moderate', False, 'Palavrões moderados'),
            ('nude|nu|pelado', 'suggestive', 'mild', False, 'Conteúdo sugestivo'),
            
            # Padrões de spam/phishing
            (r'https?://[^\s]+\.(tk|ml|ga|cf)', 'spam', 'severe', True, 'Links suspeitos'),
            ('clique aqui|ganhe dinheiro|oferta imperdível', 'spam', 'moderate', False, 'Spam comum'),
        ]
        
        for pattern, type_, severity, is_regex, description in default_patterns:
            conn.execute('''
                INSERT INTO content_patterns 
                (pattern, pattern_type, severity, is_regex, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (pattern, type_, severity, is_regex, description))
    
    def load_patterns(self):
        """Carrega padrões do banco de dados"""
        self.patterns = {
            'mild': [],
            'moderate': [],
            'severe': []
        }
        
        with sqlite3.connect(self.patterns_db_path) as conn:
            cursor = conn.execute('''
                SELECT pattern, pattern_type, severity, is_regex 
                FROM content_patterns 
                WHERE is_active = TRUE
            ''')
            
            for pattern, type_, severity, is_regex in cursor.fetchall():
                if is_regex:
                    try:
                        compiled_pattern = re.compile(pattern, re.IGNORECASE)
                        self.patterns[severity].append(compiled_pattern)
                    except re.error:
                        self.logger.error(f"Padrão regex inválido: {pattern}")
                else:
                    # Padrão simples de palavras
                    words = pattern.split('|')
                    for word in words:
                        word_pattern = re.compile(r'\b' + re.escape(word.strip()) + r'\b', re.IGNORECASE)
                        self.patterns[severity].append(word_pattern)
    
    def analyze_content(self, content: str, user_id: str = None) -> Dict[str, Any]:
        """
        Analisa conteúdo e retorna resultado da moderação
        
        Args:
            content: Texto a ser analisado
            user_id: ID do usuário (opcional)
            
        Returns:
            Dict com resultado da análise
        """
        self.stats['total_checks'] += 1
        self._reset_daily_stats()
        
        # Gerar hash do conteúdo para cache
        content_hash = str(hash(content))
        
        # Verificar cache
        cached_result = self._get_cached_result(content_hash)
        if cached_result:
            return cached_result
        
        # Análise do conteúdo
        analysis_result = self._analyze_text(content)
        
        # Determinar ação baseada na severidade
        action = self._determine_action(analysis_result['severity'], user_id)
        
        # Preparar resultado completo
        result = {
            'content_hash': content_hash,
            'severity': analysis_result['severity'],
            'action': action,
            'confidence': analysis_result['confidence'],
            'flagged_words': analysis_result['flagged_words'],
            'reason': analysis_result['reason'],
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id
        }
        
        # Salvar resultado no cache
        self._cache_result(result)
        
        # Executar ação se necessário
        if user_id and action != ModerationAction.ALLOW:
            self._execute_moderation_action(user_id, result)
        
        # Log de segurança
        self._log_moderation_event(result)
        
        return result
    
    def _analyze_text(self, content: str) -> Dict[str, Any]:
        """Analisa o texto e determina severidade"""
        content_clean = content.lower().strip()
        
        flagged_words = []
        max_severity = ContentSeverity.CLEAN
        total_matches = 0
        
        # Verificar padrões por severidade (do mais severo para o mais leve)
        for severity in ['severe', 'moderate', 'mild']:
            for pattern in self.patterns[severity]:
                matches = pattern.findall(content_clean)
                if matches:
                    flagged_words.extend(matches)
                    total_matches += len(matches)
                    if ContentSeverity(severity).value != max_severity.value:
                        max_severity = ContentSeverity(severity)
        
        # Calcular confiança baseada no número de matches
        confidence = min(0.9, total_matches * 0.2) if total_matches > 0 else 0.1
        
        # Determinar razão
        if max_severity == ContentSeverity.CLEAN:
            reason = "Conteúdo aprovado - nenhum problema detectado"
        else:
            reason = f"Conteúdo {max_severity.value} detectado - {len(flagged_words)} palavras/padrões flagrados"
        
        return {
            'severity': max_severity,
            'confidence': confidence,
            'flagged_words': flagged_words[:5],  # Limitar a 5 palavras
            'reason': reason
        }
    
    def _determine_action(self, severity: ContentSeverity, user_id: str = None) -> ModerationAction:
        """Determina ação baseada na severidade e histórico do usuário"""
        
        if severity == ContentSeverity.CLEAN:
            return ModerationAction.ALLOW
        
        # Verificar histórico do usuário se disponível
        if user_id:
            user_status = self._get_user_status(user_id)
            
            # Usuário banido
            if user_status['status'] == 'banned':
                return ModerationAction.BAN
            
            # Usuário em quarentena
            if user_status['status'] == 'quarantined':
                return ModerationAction.QUARANTINE
            
            # Determinar ação baseada em severidade + histórico
            violation_count = user_status['violation_count']
            
            if severity == ContentSeverity.SEVERE:
                if violation_count >= 3:
                    return ModerationAction.BAN
                elif violation_count >= 1:
                    return ModerationAction.BLOCK
                else:
                    return ModerationAction.QUARANTINE
            
            elif severity == ContentSeverity.MODERATE:
                if violation_count >= 5:
                    return ModerationAction.BLOCK
                elif violation_count >= 3:
                    return ModerationAction.QUARANTINE
                else:
                    return ModerationAction.WARN
            
            elif severity == ContentSeverity.MILD:
                if violation_count >= 10:
                    return ModerationAction.WARN
                else:
                    return ModerationAction.FILTER
        
        # Ações padrão sem histórico
        action_map = {
            ContentSeverity.SEVERE: ModerationAction.BLOCK,
            ContentSeverity.MODERATE: ModerationAction.WARN,
            ContentSeverity.MILD: ModerationAction.FILTER
        }
        
        return action_map.get(severity, ModerationAction.ALLOW)
    
    def _get_user_status(self, user_id: str) -> Dict[str, Any]:
        """Obtém status atual do usuário"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT violation_count, severe_violations, last_violation, 
                       status, quarantine_until, ban_until, warnings_sent
                FROM user_violations WHERE user_id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'violation_count': row[0],
                    'severe_violations': row[1],
                    'last_violation': row[2],
                    'status': row[3],
                    'quarantine_until': row[4],
                    'ban_until': row[5],
                    'warnings_sent': row[6]
                }
            else:
                return {
                    'violation_count': 0,
                    'severe_violations': 0,
                    'last_violation': None,
                    'status': 'active',
                    'quarantine_until': None,
                    'ban_until': None,
                    'warnings_sent': 0
                }
    
    def _execute_moderation_action(self, user_id: str, result: Dict[str, Any]):
        """Executa ação de moderação"""
        action = ModerationAction(result['action'])
        severity = result['severity']
        
        # Atualizar contador de violações
        self._update_user_violations(user_id, severity)
        
        # Incrementar estatísticas diárias
        if action in [ModerationAction.BLOCK, ModerationAction.BAN, ModerationAction.QUARANTINE]:
            self.stats['blocks_today'] += 1
        elif action == ModerationAction.WARN:
            self.stats['warnings_today'] += 1
        
        # Executar ação específica
        if action == ModerationAction.QUARANTINE:
            self._quarantine_user(user_id, hours=24)
        elif action == ModerationAction.BLOCK:
            self._block_user(user_id, hours=72)
        elif action == ModerationAction.BAN:
            self._ban_user(user_id)
    
    def _update_user_violations(self, user_id: str, severity: str):
        """Atualiza contador de violações do usuário"""
        with sqlite3.connect(self.db_path) as conn:
            # Verificar se usuário existe
            cursor = conn.execute('SELECT violation_count FROM user_violations WHERE user_id = ?', (user_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Atualizar contador existente
                severe_increment = 1 if severity == 'severe' else 0
                conn.execute('''
                    UPDATE user_violations 
                    SET violation_count = violation_count + 1,
                        severe_violations = severe_violations + ?,
                        last_violation = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (severe_increment, user_id))
            else:
                # Criar novo registro
                severe_count = 1 if severity == 'severe' else 0
                conn.execute('''
                    INSERT INTO user_violations 
                    (user_id, violation_count, severe_violations, last_violation)
                    VALUES (?, 1, ?, CURRENT_TIMESTAMP)
                ''', (user_id, severe_count))
    
    def _quarantine_user(self, user_id: str, hours: int = 24):
        """Coloca usuário em quarentena"""
        until = datetime.now() + timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE user_violations 
                SET status = 'quarantined', quarantine_until = ?
                WHERE user_id = ?
            ''', (until.isoformat(), user_id))
        
        self.logger.warning(f"Usuário {user_id} colocado em quarentena até {until}")
    
    def _block_user(self, user_id: str, hours: int = 72):
        """Bloqueia usuário temporariamente"""
        until = datetime.now() + timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE user_violations 
                SET status = 'blocked', ban_until = ?
                WHERE user_id = ?
            ''', (until.isoformat(), user_id))
        
        self.logger.error(f"Usuário {user_id} bloqueado até {until}")
    
    def _ban_user(self, user_id: str):
        """Bane usuário permanentemente"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE user_violations 
                SET status = 'banned', ban_until = NULL
                WHERE user_id = ?
            ''', (user_id,))
        
        self.logger.critical(f"Usuário {user_id} banido permanentemente")
    
    def _get_cached_result(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """Verifica resultado em cache"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT severity, flagged_words, confidence_score, last_checked
                FROM content_cache WHERE content_hash = ?
            ''', (content_hash,))
            
            row = cursor.fetchone()
            if row:
                # Verificar se cache ainda é válido (24 horas)
                last_checked = datetime.fromisoformat(row[3])
                if datetime.now() - last_checked < timedelta(hours=24):
                    return {
                        'content_hash': content_hash,
                        'severity': row[0],
                        'action': ModerationAction.ALLOW,  # Cache sempre permite
                        'confidence': row[2],
                        'flagged_words': json.loads(row[1]) if row[1] else [],
                        'reason': f"Resultado em cache - {row[0]}",
                        'timestamp': datetime.now().isoformat(),
                        'cached': True
                    }
        return None
    
    def _cache_result(self, result: Dict[str, Any]):
        """Salva resultado no cache"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO content_cache 
                (content_hash, severity, flagged_words, confidence_score)
                VALUES (?, ?, ?, ?)
            ''', (
                result['content_hash'],
                result['severity'].value if hasattr(result['severity'], 'value') else str(result['severity']),
                json.dumps(result['flagged_words']),
                result['confidence']
            ))
    
    def _log_moderation_event(self, result: Dict[str, Any]):
        """Log do evento de moderação"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO moderation_logs 
                (user_id, content_hash, content_snippet, severity, action_taken, reason, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.get('user_id'),
                result['content_hash'],
                str(result['flagged_words'])[:100],  # Snippet das palavras
                result['severity'].value if hasattr(result['severity'], 'value') else str(result['severity']),
                result['action'].value if hasattr(result['action'], 'value') else str(result['action']),
                result['reason'],
                json.dumps({'confidence': result['confidence']})
            ))
        
        # Log de segurança estruturado
        log_security_event(
            event_type="content_moderation",
            severity=result['severity'].value if hasattr(result['severity'], 'value') else str(result['severity']),
            details={
                'action': str(result['action']),
                'confidence': result['confidence'],
                'flagged_count': len(result['flagged_words'])
            },
            user_id=result.get('user_id')
        )
    
    def _reset_daily_stats(self):
        """Reset estatísticas diárias"""
        today = datetime.now().date()
        if today != self.stats['last_reset']:
            self.stats['blocks_today'] = 0
            self.stats['warnings_today'] = 0
            self.stats['last_reset'] = today
    
    def get_user_feedback_message(self, result: Dict[str, Any]) -> str:
        """Gera mensagem de feedback para o usuário"""
        action = ModerationAction(result['action']) if isinstance(result['action'], str) else result['action']
        severity = result['severity']
        
        if action == ModerationAction.ALLOW:
            return None  # Sem feedback necessário
        
        messages = {
            ModerationAction.WARN: {
                'mild': "⚠️ **Atenção**: Sua mensagem contém conteúdo que pode ser inadequado. Por favor, mantenha as conversas respeitosas.",
                'moderate': "⚠️ **Aviso**: Detectamos linguagem inapropriada em sua mensagem. Continued violações podem resultar em restrições.",
                'severe': "🚨 **Aviso Sério**: Sua mensagem contém conteúdo altamente inadequado. Isso vai contra nossas diretrizes da comunidade."
            },
            ModerationAction.FILTER: {
                'mild': "🔄 **Mensagem Filtrada**: Algumas palavras foram censuradas para manter um ambiente respeitoso.",
                'moderate': "🔄 **Conteúdo Moderado**: Sua mensagem foi alterada para remover linguagem inadequada.",
                'severe': "🔄 **Mensagem Bloqueada**: O conteúdo não pôde ser enviado devido a violações graves."
            },
            ModerationAction.QUARANTINE: {
                'mild': "⏸️ **Quarentena**: Você foi temporariamente restrito devido a múltiplas violações leves. Tempo: 24h.",
                'moderate': "⏸️ **Quarentena Ativa**: Suas mensagens serão revisadas antes da publicação. Duração: 24h.",
                'severe': "🚫 **Quarentena Severa**: Acesso temporariamente limitado devido a conteúdo grave. Duração: 24h."
            },
            ModerationAction.BLOCK: {
                'mild': "🚫 **Bloqueio Temporário**: Você foi bloqueado por 72 horas devido a violações repetidas.",
                'moderate': "🚫 **Conta Bloqueada**: Acesso suspenso por 72 horas. Revise nossas diretrizes da comunidade.",
                'severe': "🚫 **Bloqueio Severo**: Conta suspensa por 72 horas devido a violações graves das diretrizes."
            },
            ModerationAction.BAN: {
                'mild': "⛔ **Banimento**: Sua conta foi banida permanentemente devido a violações contínuas.",
                'moderate': "⛔ **Conta Banida**: Banimento permanente aplicado. Contate o suporte se acreditar que há erro.",
                'severe': "⛔ **Banimento Permanente**: Sua conta foi banida permanentemente por violações graves."
            }
        }
        
        return messages.get(action, {}).get(severity, "🤖 Ação de moderação aplicada.")
    
    def get_moderation_stats(self, days: int = 7) -> Dict[str, Any]:
        """Obtém estatísticas de moderação"""
        since_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            # Estatísticas gerais
            cursor = conn.execute('''
                SELECT severity, action_taken, COUNT(*) 
                FROM moderation_logs 
                WHERE timestamp >= ?
                GROUP BY severity, action_taken
            ''', (since_date.isoformat(),))
            
            action_stats = {}
            for severity, action, count in cursor.fetchall():
                key = f"{severity}_{action}"
                action_stats[key] = count
            
            # Top usuários com violações
            cursor = conn.execute('''
                SELECT user_id, violation_count, severe_violations, status
                FROM user_violations 
                ORDER BY violation_count DESC 
                LIMIT 10
            ''')
            
            top_violators = [
                {
                    'user_id': row[0],
                    'violations': row[1],
                    'severe': row[2],
                    'status': row[3]
                }
                for row in cursor.fetchall()
            ]
            
            # Estatísticas diárias atuais
            current_stats = {
                'total_checks_today': self.stats['total_checks'],
                'blocks_today': self.stats['blocks_today'],
                'warnings_today': self.stats['warnings_today']
            }
        
        return {
            'period_days': days,
            'action_stats': action_stats,
            'top_violators': top_violators,
            'current_stats': current_stats,
            'generated_at': datetime.now().isoformat()
        }
    
    def cleanup_old_logs(self, days_to_keep: int = 90):
        """Remove logs antigos"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                DELETE FROM moderation_logs 
                WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            
            # Limpar cache antigo também
            cursor = conn.execute('''
                DELETE FROM content_cache 
                WHERE last_checked < ?
            ''', (cutoff_date.isoformat(),))
            
            cache_deleted = cursor.rowcount
        
        self.logger.info(f"Limpeza: {deleted_count} logs e {cache_deleted} entradas de cache removidos")
        return {'logs_deleted': deleted_count, 'cache_deleted': cache_deleted}


# Instância global do moderador
moderator = AdultContentModerator()


def analyze_content(content: str, user_id: str = None) -> Dict[str, Any]:
    """Função conveniente para análise de conteúdo"""
    return moderator.analyze_content(content, user_id)


def get_user_feedback_message(result: Dict[str, Any]) -> str:
    """Função conveniente para obter mensagem de feedback"""
    return moderator.get_user_feedback_message(result)


def is_user_blocked(user_id: str) -> bool:
    """Verifica se usuário está bloqueado"""
    status = moderator._get_user_status(user_id)
    if status['status'] in ['blocked', 'banned']:
        return True
    
    # Verificar se quarentena/bloqueio expirou
    if status['quarantine_until']:
        quarantine_until = datetime.fromisoformat(status['quarantine_until'])
        if datetime.now() < quarantine_until:
            return True
    
    if status['ban_until']:
        ban_until = datetime.fromisoformat(status['ban_until'])
        if datetime.now() < ban_until:
            return True
    
    return False


def get_moderation_stats(days: int = 7) -> Dict[str, Any]:
    """Função conveniente para obter estatísticas"""
    return moderator.get_moderation_stats(days)


# Exemplo de uso
if __name__ == "__main__":
    print("🔒 TESTANDO SISTEMA DE MODERAÇÃO DE CONTEÚDO")
    print("=" * 60)
    
    # Testes básicos
    test_messages = [
        "Olá, como você está?",  # Limpo
        "Que droga de dia!",     # Mild
        "Isso é muito sexual",   # Moderate  
        "Conteúdo muito explícito aqui",  # Severe
    ]
    
    for msg in test_messages:
        print(f"\n📝 Testando: '{msg}'")
        result = analyze_content(msg, user_id="test_user")
        print(f"   Severidade: {result['severity']}")
        print(f"   Ação: {result['action']}")
        print(f"   Confiança: {result['confidence']:.2f}")
        
        feedback = get_user_feedback_message(result)
        if feedback:
            print(f"   Feedback: {feedback}")
    
    # Estatísticas
    print(f"\n📊 ESTATÍSTICAS:")
    stats = get_moderation_stats(7)
    print(f"   Verificações hoje: {stats['current_stats']['total_checks_today']}")
    print(f"   Bloqueios hoje: {stats['current_stats']['blocks_today']}")
    print(f"   Avisos hoje: {stats['current_stats']['warnings_today']}")
    
    print("\n✅ Teste do sistema de moderação concluído!")