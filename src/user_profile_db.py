import sqlite3
import os

class UserProfileDB:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'memoria', 'user_profiles.db')
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()
        self.cleanup_expired_tokens()

    def cleanup_expired_tokens(self):
        """Limpa todos os tokens expirados do banco de dados"""
        with self.conn:
            self.conn.execute('''
                UPDATE profiles 
                SET reset_token = NULL, reset_token_expiry = NULL 
                WHERE reset_token_expiry < datetime('now')
            ''')

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE,
                    username TEXT UNIQUE,
                    password_hash TEXT,
                    email TEXT UNIQUE,
                    user_name TEXT,
                    user_age TEXT,
                    user_gender TEXT,
                    bot_name TEXT,
                    bot_gender TEXT,
                    bot_avatar TEXT,
                    has_mature_access BOOLEAN DEFAULT 0,
                    email_confirmed BOOLEAN DEFAULT 0,
                    confirmation_token TEXT,
                    reset_token TEXT,
                    reset_token_expiry TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def get_profile(self, user_id):
        cur = self.conn.cursor()
        cur.execute('SELECT user_name, user_age, user_gender, bot_name, bot_gender, bot_avatar FROM profiles WHERE user_id = ?', (user_id,))
        row = cur.fetchone()
        if row:
            return {
                'user_name': row[0],
                'user_age': row[1],
                'user_gender': row[2],
                'bot_name': row[3],
                'bot_gender': row[4],
                'bot_avatar': row[5],
                'has_mature_access': bool(row[6]) if len(row) > 6 else False
            }
        return None

    def save_profile(self, user_id, user_name, user_age, user_gender, bot_name, bot_gender, bot_avatar, has_mature_access=False, username=None, password_hash=None, email=None):
        with self.conn:
            self.conn.execute('''
                INSERT OR REPLACE INTO profiles (
                    user_id, username, password_hash, email, user_name, user_age, 
                    user_gender, bot_name, bot_gender, bot_avatar, has_mature_access
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, password_hash, email, user_name, user_age, 
                  user_gender, bot_name, bot_gender, bot_avatar, has_mature_access))
                  
    def get_profile_by_username(self, username):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM profiles WHERE username = ?', (username,))
        row = cur.fetchone()
        if row:
            return {
                'user_id': row[1],
                'username': row[2],
                'password_hash': row[3],
                'email': row[4],
                'user_name': row[5],
                'user_age': row[6],
                'user_gender': row[7],
                'bot_name': row[8],
                'bot_gender': row[9],
                'bot_avatar': row[10],
                'has_mature_access': bool(row[11])
            }
        return None
        
    def username_exists(self, username):
        cur = self.conn.cursor()
        cur.execute('SELECT 1 FROM profiles WHERE username = ?', (username,))
        return cur.fetchone() is not None
        
    def email_exists(self, email):
        cur = self.conn.cursor()
        cur.execute('SELECT 1 FROM profiles WHERE email = ?', (email,))
        return cur.fetchone() is not None
        
    def set_confirmation_token(self, user_id, token):
        with self.conn:
            self.conn.execute(
                'UPDATE profiles SET confirmation_token = ? WHERE user_id = ?',
                (token, user_id)
            )
    
    def confirm_email(self, token):
        cur = self.conn.cursor()
        cur.execute(
            'UPDATE profiles SET email_confirmed = 1, confirmation_token = NULL '
            'WHERE confirmation_token = ? RETURNING user_id',
            (token,)
        )
        result = cur.fetchone()
        self.conn.commit()
        return result[0] if result else None
    
    def set_reset_token(self, email, token, expiry):
        """
        Define um token de redefinição de senha para um email.
        O parâmetro expiry deve ser um objeto datetime ou uma string ISO 8601.
        """
        if hasattr(expiry, 'isoformat'):  # Se for um objeto datetime
            expiry = expiry.isoformat()
            
        with self.conn:
            self.conn.execute('''
                UPDATE profiles 
                SET reset_token = ?, 
                    reset_token_expiry = datetime(?)
                WHERE email = ?
            ''', (token, expiry, email))
    
    def get_profile_by_reset_token(self, token):
        """
        Obtém um perfil usando o token de redefinição de senha.
        Retorna None se o token for inválido ou estiver expirado.
        """
        self.cleanup_expired_tokens()  # Limpa tokens expirados primeiro
        
        cur = self.conn.cursor()
        cur.execute('''
            SELECT user_id, username, email
            FROM profiles 
            WHERE reset_token = ? 
            AND reset_token_expiry > datetime('now')
        ''', (token,))
        
        row = cur.fetchone()
        if row:
            return {
                'user_id': row[0],
                'username': row[1],
                'email': row[2]
            }
        return None
    
    def update_password(self, user_id, password_hash):
        """
        Atualiza a senha do usuário e limpa o token de redefinição.
        Retorna True se a senha foi atualizada com sucesso.
        """
        try:
            with self.conn:
                cursor = self.conn.execute('''
                    UPDATE profiles 
                    SET password_hash = ?,
                        reset_token = NULL,
                        reset_token_expiry = NULL 
                    WHERE user_id = ?
                    RETURNING user_id
                ''', (password_hash, user_id))
                
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"Erro ao atualizar senha: {e}")
            return False
