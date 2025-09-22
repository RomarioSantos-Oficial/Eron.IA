import sqlite3
import os

class UserProfileDB:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'database', 'user_profiles.db')
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()
        self._ensure_columns_exist()  # Garante que as colunas mais recentes existam
        self.cleanup_expired_tokens()

    def delete_profile(self, user_id):
        """Apaga completamente um perfil do banco de dados"""
        try:
            with self.conn:
                result = self.conn.execute(
                    "DELETE FROM profiles WHERE user_id = ?", 
                    (user_id,)
                )
                if result.rowcount > 0:
                    print(f"[DEBUG] Perfil {user_id} apagado com sucesso")
                    return True
                else:
                    print(f"[DEBUG] Perfil {user_id} não encontrado para apagar")
                    return False
        except Exception as e:
            print(f"[ERROR] Erro ao apagar perfil {user_id}: {e}")
            return False

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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    bot_personality TEXT,
                    bot_language TEXT,
                    preferred_topics TEXT
                )
            ''')

    def _ensure_columns_exist(self):
        """Garante que as colunas mais recentes existam na tabela."""
        columns_to_add = {
            'bot_personality': 'TEXT',
            'bot_language': 'TEXT',
            'preferred_topics': 'TEXT',
            'birth_date': 'TEXT',  # Data de nascimento real
            'adult_intensity_level': 'INTEGER DEFAULT 1',
            'adult_content_preferences': 'TEXT',
            'adult_interaction_style': 'TEXT DEFAULT "romantic"',
            'adult_boundaries': 'TEXT'
        }
        
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(profiles)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        with self.conn:
            for col, col_type in columns_to_add.items():
                if col not in existing_columns:
                    self.conn.execute(f"ALTER TABLE profiles ADD COLUMN {col} {col_type}")

    def get_profile(self, user_id):
        if not user_id:
            return None
            
        self._ensure_columns_exist() # Garante que as colunas existem antes de ler
        cur = self.conn.cursor()
        cur.execute('''
            SELECT user_id, username, password_hash, email, user_name, 
                   user_age, user_gender, bot_name, bot_gender, bot_avatar, 
                   has_mature_access, bot_personality, bot_language, preferred_topics,
                   birth_date, adult_intensity_level, adult_content_preferences, 
                   adult_interaction_style, adult_boundaries
            FROM profiles WHERE user_id = ?
        ''', (user_id,))
        row = cur.fetchone()
        if row:
            fields = [
                'user_id', 'username', 'password_hash', 'email', 'user_name',
                'user_age', 'user_gender', 'bot_name', 'bot_gender', 'bot_avatar',
                'has_mature_access', 'bot_personality', 'bot_language', 'preferred_topics',
                'birth_date', 'adult_intensity_level', 'adult_content_preferences', 
                'adult_interaction_style', 'adult_boundaries'
            ]
            profile = {}
            for i, field in enumerate(fields):
                if field == 'has_mature_access':
                    profile[field] = bool(row[i])
                else:
                    profile[field] = row[i]
            return profile
        return None

    def save_profile(self, **kwargs):
        """
        Salva um perfil de usuário. Se o perfil já existe, atualiza os campos fornecidos.
        Se não existe, cria um novo.
        """
        print("Salvando perfil com dados:", kwargs)  # Debug
        
        user_id = kwargs.get('user_id')
        if not user_id:
            raise ValueError('O campo user_id é obrigatório.')

        self._ensure_columns_exist() # Garante que as colunas existem

        try:
            with self.conn:
                # Verifica se o perfil já existe
                cur = self.conn.cursor()
                cur.execute("SELECT 1 FROM profiles WHERE user_id = ?", (user_id,))
                exists = cur.fetchone()

                if exists:
                    # Atualiza o perfil existente
                    update_fields = []
                    update_values = []
                    for key, value in kwargs.items():
                        if key != 'user_id':
                            update_fields.append(f"{key} = ?")
                            update_values.append(value)
                    
                    if not update_fields:
                        print("Nenhum campo para atualizar.")
                        return

                    update_values.append(user_id)
                    query = f"UPDATE profiles SET {', '.join(update_fields)} WHERE user_id = ?"
                    
                    print("Executando query de UPDATE:", query, update_values) # Debug
                    self.conn.execute(query, update_values)

                else:
                    # Insere um novo perfil
                    fields = list(kwargs.keys())
                    placeholders = ', '.join(['?' for _ in fields])
                    values = [kwargs.get(f) for f in fields]
                    
                    query = f"INSERT INTO profiles ({', '.join(fields)}) VALUES ({placeholders})"
                    
                    print("Executando query de INSERT:", query, values) # Debug
                    self.conn.execute(query, values)

                self.conn.commit()
                print("Perfil salvo com sucesso!")  # Debug
        except Exception as e:
            print(f"Erro ao salvar perfil: {e}")  # Debug
            raise
                  
    def get_profile_by_username(self, username):
        if not username:
            return None
            
        self._ensure_columns_exist() # Garante que as colunas existem antes de ler
        cur = self.conn.cursor()
        cur.execute('''
            SELECT user_id, username, password_hash, email, user_name, 
                   user_age, user_gender, bot_name, bot_gender, bot_avatar, 
                   has_mature_access, bot_personality, bot_language, preferred_topics,
                   birth_date, adult_intensity_level, adult_content_preferences, 
                   adult_interaction_style, adult_boundaries
            FROM profiles WHERE username = ?
        ''', (username,))
        row = cur.fetchone()
        if row:
            fields = [
                'user_id', 'username', 'password_hash', 'email', 'user_name',
                'user_age', 'user_gender', 'bot_name', 'bot_gender', 'bot_avatar',
                'has_mature_access', 'bot_personality', 'bot_language', 'preferred_topics',
                'birth_date', 'adult_intensity_level', 'adult_content_preferences', 
                'adult_interaction_style', 'adult_boundaries'
            ]
            profile = {}
            for i, field in enumerate(fields):
                if field == 'has_mature_access':
                    profile[field] = bool(row[i])
                else:
                    profile[field] = row[i]
            return profile
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

    def update_profile(self, user_id, **kwargs):
        """
        Atualiza campos específicos de um perfil existente.
        Aceita campos individuais como parâmetros nomeados.
        """
        if not user_id:
            return False
            
        # Campos válidos para atualização
        valid_fields = {
            'user_name': 'user_name',
            'user_age': 'user_age', 
            'user_gender': 'user_gender',
            'bot_name': 'bot_name',
            'bot_gender': 'bot_gender',
            'bot_personality': 'bot_personality',
            'bot_language': 'bot_language',
            'preferred_topics': 'preferred_topics',
            'bot_avatar': 'bot_avatar',
            'has_mature_access': 'has_mature_access',
            'adult_intensity_level': 'adult_intensity_level',
            'adult_content_preferences': 'adult_content_preferences',
            'adult_interaction_style': 'adult_interaction_style',
            'adult_boundaries': 'adult_boundaries'
        }
        
        # Filtrar apenas campos válidos que foram fornecidos
        update_fields = {}
        for key, value in kwargs.items():
            if key in valid_fields and value is not None:
                update_fields[valid_fields[key]] = value
        
        if not update_fields:
            return False
            
        try:
            # Construir query dinâmica
            set_clauses = [f"{field} = ?" for field in update_fields.keys()]
            query = f"UPDATE profiles SET {', '.join(set_clauses)} WHERE user_id = ?"
            values = list(update_fields.values()) + [user_id]
            
            with self.conn:
                cursor = self.conn.execute(query, values)
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Erro ao atualizar perfil {user_id}: {e}")
            return False

    def reset_user_profile(self, user_id):
        """
        Resetar/apagar completamente o perfil de um usuário
        Remove todos os dados de personalização
        """
        try:
            with self.conn:
                # Verificar se usuário existe
                cursor = self.conn.cursor()
                cursor.execute('SELECT 1 FROM profiles WHERE user_id = ?', (user_id,))
                if not cursor.fetchone():
                    return False
                
                # Resetar todos os campos de personalização para valores padrão
                self.conn.execute('''
                    UPDATE profiles SET
                        user_name = NULL,
                        user_age = NULL,
                        birth_date = NULL,
                        user_gender = NULL,
                        bot_name = 'Eron',
                        bot_gender = 'neutro',
                        bot_personality = 'amigável',
                        bot_language = 'português',
                        preferred_topics = NULL,
                        bot_avatar = NULL,
                        has_mature_access = 0,
                        adult_intensity_level = 1,
                        adult_content_preferences = NULL,
                        adult_interaction_style = 'romantic',
                        adult_boundaries = NULL
                    WHERE user_id = ?
                ''', (user_id,))
                
                return True
                
        except Exception as e:
            print(f"Erro ao resetar perfil {user_id}: {e}")
            return False
