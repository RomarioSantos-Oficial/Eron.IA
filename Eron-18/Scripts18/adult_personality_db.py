import sqlite3
import os
from datetime import datetime, timedelta
import hashlib
import secrets

class AdultPersonalityDB:
    """
    Banco de dados específico para personalidade adulta com sistemas de segurança.
    ATENÇÃO: Conteúdo destinado exclusivamente para maiores de 18 anos.
    """
    
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'database18', 'adult_personality.db')
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
        self.cleanup_expired_sessions()

    def create_tables(self):
        """Cria as tabelas necessárias para o sistema adulto"""
        with self.conn:
            # Dropar tabela existente e recriar com estrutura completa
            self.conn.execute('DROP TABLE IF EXISTS age_verifications')
            
            # Tabela para verificações de idade (estrutura completa)
            self.conn.execute('''
                CREATE TABLE age_verifications (
                    user_id TEXT,
                    verification_token TEXT,
                    age_provided INTEGER,
                    age_confirmed BOOLEAN DEFAULT 0,
                    session_token TEXT,
                    verification_method TEXT DEFAULT 'interactive',
                    platform TEXT DEFAULT 'telegram',
                    verification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela para sessões adultas ativas (corrigir estrutura)
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS adult_sessions (
                    user_id TEXT,
                    session_token TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    platform TEXT DEFAULT 'telegram',
                    deactivation_reason TEXT
                )
            ''')
            
            # Tabela para personalização da personalidade "devassa"
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS devassa_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE,
                    intensity_level INTEGER DEFAULT 3,
                    gender_preference TEXT DEFAULT 'feminino',
                    relationship_stage TEXT DEFAULT 'inicial',
                    preferred_topics TEXT,
                    language_style TEXT DEFAULT 'sedutora',
                    custom_triggers TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela para frases e conteúdo por categoria
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS content_database (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    subcategory TEXT,
                    gender_context TEXT,
                    intensity INTEGER,
                    content_text TEXT,
                    triggers TEXT,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela para logs de segurança
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS security_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    action TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_hash TEXT,
                    platform TEXT,
                    success BOOLEAN
                )
            ''')

    def verify_age_consent(self, user_id, age, platform='telegram'):
        """Verifica e registra consentimento de idade"""
        if age < 18:
            self.log_security_event(user_id, 'AGE_VERIFICATION_FAILED', platform, False)
            return False
            
        consent_token = secrets.token_urlsafe(32)
        
        with self.conn:
            self.conn.execute('''
                INSERT OR REPLACE INTO age_verifications 
                (user_id, age_confirmed, consent_token, last_access, access_count)
                VALUES (?, 1, ?, datetime('now'), 1)
            ''', (user_id, consent_token))
            
        self.log_security_event(user_id, 'AGE_VERIFIED', platform, True)
        return consent_token

    def create_adult_session(self, user_id, platform='telegram'):
        """Cria uma sessão adulta temporária"""
        if not self.is_age_verified(user_id):
            return None
            
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=2)  # 2 horas de sessão
        
        with self.conn:
            self.conn.execute('''
                INSERT INTO adult_sessions 
                (user_id, session_token, expires_at, platform)
                VALUES (?, ?, ?, ?)
            ''', (user_id, session_token, expires_at, platform))
            
        self.log_security_event(user_id, 'ADULT_SESSION_CREATED', platform, True)
        return session_token

    def is_age_verified(self, user_id):
        """Verifica se o usuário tem idade confirmada"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT age_confirmed FROM age_verifications 
            WHERE user_id = ? AND age_confirmed = 1
        ''', (user_id,))
        return cursor.fetchone() is not None

    def is_session_active(self, user_id, session_token=None):
        """Verifica se a sessão adulta está ativa"""
        cursor = self.conn.cursor()
        if session_token:
            cursor.execute('''
                SELECT id FROM adult_sessions 
                WHERE user_id = ? AND session_token = ? 
                AND is_active = 1 AND expires_at > datetime('now')
            ''', (user_id, session_token))
        else:
            cursor.execute('''
                SELECT id FROM adult_sessions 
                WHERE user_id = ? AND is_active = 1 AND expires_at > datetime('now')
            ''', (user_id,))
        return cursor.fetchone() is not None

    def get_devassa_profile(self, user_id):
        """Obtém perfil da personalidade devassa"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM devassa_profiles WHERE user_id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        
        if row:
            return {
                'user_id': row[1],
                'intensity_level': row[2],
                'gender_preference': row[3],
                'relationship_stage': row[4],
                'preferred_topics': row[5],
                'language_style': row[6],
                'custom_triggers': row[7]
            }
        return None

    def save_devassa_profile(self, user_id, **kwargs):
        """Salva perfil da personalidade devassa"""
        profile = self.get_devassa_profile(user_id)
        
        if profile:
            # Atualizar perfil existente
            update_fields = []
            values = []
            for key, value in kwargs.items():
                if key in ['intensity_level', 'gender_preference', 'relationship_stage', 
                          'preferred_topics', 'language_style', 'custom_triggers']:
                    update_fields.append(f"{key} = ?")
                    values.append(value)
            
            if update_fields:
                values.append(user_id)
                query = f"UPDATE devassa_profiles SET {', '.join(update_fields)}, updated_at = datetime('now') WHERE user_id = ?"
                with self.conn:
                    self.conn.execute(query, values)
        else:
            # Criar novo perfil
            with self.conn:
                self.conn.execute('''
                    INSERT INTO devassa_profiles 
                    (user_id, intensity_level, gender_preference, relationship_stage, 
                     preferred_topics, language_style, custom_triggers)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    kwargs.get('intensity_level', 3),
                    kwargs.get('gender_preference', 'feminino'),
                    kwargs.get('relationship_stage', 'inicial'),
                    kwargs.get('preferred_topics', ''),
                    kwargs.get('language_style', 'sedutora'),
                    kwargs.get('custom_triggers', '')
                ))

    def get_content_by_context(self, category, gender_context, intensity_level=3):
        """Obtém conteúdo baseado no contexto"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT content_text FROM content_database 
            WHERE category = ? AND gender_context = ? AND intensity <= ?
            ORDER BY RANDOM() LIMIT 1
        ''', (category, gender_context, intensity_level))
        
        result = cursor.fetchone()
        if result:
            # Incrementar contador de uso
            with self.conn:
                self.conn.execute('''
                    UPDATE content_database 
                    SET usage_count = usage_count + 1 
                    WHERE content_text = ?
                ''', (result[0],))
            return result[0]
        return None

    def add_content(self, category, gender_context, intensity, content_text, triggers=""):
        """Adiciona novo conteúdo ao banco"""
        with self.conn:
            self.conn.execute('''
                INSERT INTO content_database 
                (category, gender_context, intensity, content_text, triggers)
                VALUES (?, ?, ?, ?, ?)
            ''', (category, gender_context, intensity, content_text, triggers))

    def log_security_event(self, user_id, action, platform, success, ip_hash=None):
        """Registra eventos de segurança"""
        with self.conn:
            self.conn.execute('''
                INSERT INTO security_logs (user_id, action, platform, success, ip_hash)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, action, platform, success, ip_hash))

    def cleanup_expired_sessions(self):
        """Remove sessões expiradas"""
        with self.conn:
            self.conn.execute('''
                UPDATE adult_sessions 
                SET is_active = 0 
                WHERE expires_at < datetime('now')
            ''')

    def revoke_access(self, user_id):
        """Remove completamente o acesso adulto de um usuário"""
        with self.conn:
            # Remove verificação de idade
            self.conn.execute('DELETE FROM age_verifications WHERE user_id = ?', (user_id,))
            # Desativa todas as sessões
            self.conn.execute('UPDATE adult_sessions SET is_active = 0 WHERE user_id = ?', (user_id,))
            # Remove perfil devassa
            self.conn.execute('DELETE FROM devassa_profiles WHERE user_id = ?', (user_id,))
            
        self.log_security_event(user_id, 'ACCESS_REVOKED', 'system', True)

    def get_security_stats(self):
        """Obtém estatísticas de segurança"""
        cursor = self.conn.cursor()
        
        # Total de usuários verificados
        cursor.execute('SELECT COUNT(*) FROM age_verifications WHERE age_confirmed = 1')
        verified_users = cursor.fetchone()[0]
        
        # Sessões ativas
        cursor.execute('SELECT COUNT(*) FROM adult_sessions WHERE is_active = 1 AND expires_at > datetime("now")')
        active_sessions = cursor.fetchone()[0]
        
        # Tentativas de acesso negadas nas últimas 24h
        cursor.execute('''
            SELECT COUNT(*) FROM security_logs 
            WHERE action LIKE '%FAILED%' AND timestamp > datetime('now', '-1 day')
        ''')
        failed_attempts = cursor.fetchone()[0]
        
        return {
            'verified_users': verified_users,
            'active_sessions': active_sessions,
            'failed_attempts_24h': failed_attempts
        }

    # ===== MÉTODOS PARA ADULT_COMMANDS =====
    
    def get_active_adult_session(self, user_id):
        """Obtém sessão adulta ativa do usuário"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM adult_sessions 
            WHERE user_id = ? AND is_active = 1 
            AND (expires_at IS NULL OR expires_at > datetime('now'))
            ORDER BY created_at DESC LIMIT 1
        ''', (user_id,))
        
        result = cursor.fetchone()
        if result:
            return {
                'user_id': result[0],
                'session_token': result[1],
                'created_at': result[2],
                'expires_at': result[3],
                'is_active': result[4],
                'last_activity': result[5]
            }
        return None

    def get_recent_verification(self, user_id, hours=24):
        """Verifica se houve tentativa de verificação recente"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM age_verifications 
            WHERE user_id = ? AND verification_date > datetime('now', '-{} hours')
            ORDER BY verification_date DESC LIMIT 1
        '''.format(hours), (user_id,))
        
        result = cursor.fetchone()
        if result:
            return {
                'user_id': result[0],
                'verification_token': result[1],
                'verified': result[2],  # age_confirmed
                'created_at': result[3]  # verification_date
            }
        return None

    def log_verification_attempt(self, user_id, verification_token, platform='telegram'):
        """Registra tentativa de verificação"""
        with self.conn:
            self.conn.execute('''
                INSERT INTO age_verifications 
                (user_id, verification_token, age_provided, age_confirmed, verification_method, platform)
                VALUES (?, ?, 0, 0, 'interactive', ?)
            ''', (user_id, verification_token, platform))

    def validate_verification_token(self, user_id, verification_token):
        """Valida token de verificação"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM age_verifications 
            WHERE user_id = ? AND verification_token = ?
            AND verification_date > datetime('now', '-1 hour')
        ''', (user_id, verification_token))
        
        return cursor.fetchone()[0] > 0

    def update_verification_stage(self, user_id, verification_token, stage):
        """Atualiza estágio da verificação"""
        with self.conn:
            self.conn.execute('''
                UPDATE age_verifications 
                SET verification_method = ?
                WHERE user_id = ? AND verification_token = ?
            ''', (stage, user_id, verification_token))

    def cancel_verification(self, user_id, verification_token, reason):
        """Cancela verificação em andamento"""
        with self.conn:
            self.conn.execute('''
                UPDATE age_verifications 
                SET age_confirmed = 0, verification_method = ?
                WHERE user_id = ? AND verification_token = ?
            ''', (f'cancelled_{reason}', user_id, verification_token))
        
        self.log_security_event(user_id, 'VERIFICATION_CANCELLED', 'telegram', True)

    def complete_age_verification(self, user_id, verification_token, calculated_age, 
                                  verified, session_token=None, failure_reason=None):
        """Completa processo de verificação de idade"""
        with self.conn:
            self.conn.execute('''
                UPDATE age_verifications 
                SET age_provided = ?, age_confirmed = ?, session_token = ?, verification_method = ?
                WHERE user_id = ? AND verification_token = ?
            ''', (calculated_age, int(verified), session_token, 
                  'completed' if verified else f'failed_{failure_reason}',
                  user_id, verification_token))
        
        action = 'AGE_VERIFICATION_SUCCESS' if verified else 'AGE_VERIFICATION_FAILED'
        self.log_security_event(user_id, action, 'telegram', verified)

    def create_adult_session(self, user_id, session_token, expires_hours=720):  # 30 dias
        """Cria sessão adulta ativa"""
        from datetime import datetime, timedelta
        
        expires_at = datetime.now() + timedelta(hours=expires_hours)
        
        with self.conn:
            self.conn.execute('''
                INSERT INTO adult_sessions 
                (user_id, session_token, expires_at, is_active)
                VALUES (?, ?, ?, 1)
            ''', (user_id, session_token, expires_at.isoformat()))

    def deactivate_adult_session(self, user_id, reason='user_request'):
        """Desativa sessão adulta do usuário"""
        with self.conn:
            self.conn.execute('''
                UPDATE adult_sessions 
                SET is_active = 0
                WHERE user_id = ? AND is_active = 1
            ''', (user_id,))
        
        self.log_security_event(user_id, f'SESSION_DEACTIVATED_{reason}', 'system', True)

    def get_latest_verification(self, user_id):
        """Obtém última verificação de idade do usuário"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM age_verifications 
            WHERE user_id = ? 
            ORDER BY verification_date DESC LIMIT 1
        ''', (user_id,))
        
        result = cursor.fetchone()
        if result:
            return {
                'user_id': result[0],
                'verification_token': result[1],
                'age_provided': result[2],
                'age_confirmed': result[3],
                'session_token': result[4],
                'verification_method': result[5],
                'platform': result[6],
                'created_at': result[7]  # verification_date
            }
        return None