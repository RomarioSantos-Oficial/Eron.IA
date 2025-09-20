import sqlite3
import os

class EronMemory:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'database', 'eron_memory.db')
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        with self.conn:
            # Criar tabela atualizada com user_id
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    user_message TEXT,
                    eron_response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Verificar se coluna user_id existe (para compatibilidade com banco antigo)
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(messages)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'user_id' not in columns:
                self.conn.execute('ALTER TABLE messages ADD COLUMN user_id TEXT')
            if 'timestamp' not in columns:
                self.conn.execute('ALTER TABLE messages ADD COLUMN timestamp DATETIME')

    def save_message(self, user_message, eron_response, user_id=None):
        with self.conn:
            self.conn.execute(
                'INSERT INTO messages (user_id, user_message, eron_response, timestamp) VALUES (?, ?, ?, CURRENT_TIMESTAMP)',
                (user_id, user_message, eron_response)
            )

    def get_all_messages(self, user_id=None):
        with self.conn:
            if user_id:
                return self.conn.execute(
                    'SELECT * FROM messages WHERE user_id = ? OR user_id IS NULL ORDER BY timestamp', 
                    (user_id,)
                ).fetchall()
            else:
                # Compatibilidade com código antigo
                return self.conn.execute('SELECT * FROM messages ORDER BY timestamp').fetchall()
    
    def get_recent_context(self, user_id, limit=5):
        """Obtém contexto recente das conversas do usuário para melhorar respostas"""
        with self.conn:
            messages = self.conn.execute(
                'SELECT user_message, eron_response FROM messages WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?',
                (user_id, limit)
            ).fetchall()
            
            context = []
            for msg in reversed(messages):  # Mais antigas primeiro
                context.append(f"Usuário: {msg[0]}")
                context.append(f"Assistente: {msg[1]}")
            
            return "\n".join(context) if context else ""
