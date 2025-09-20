import sqlite3
from cryptography.fernet import Fernet
import os

class SensitiveMemory:
    def __init__(self, db_path=None, key_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'database', 'sensitive_memory.db')
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()
        # Gerar ou carregar chave de criptografia
        if key_path is None:
            key_path = os.path.join(os.path.dirname(db_path), 'sensitive.key')
        if not os.path.exists(key_path):
            key = Fernet.generate_key()
            with open(key_path, 'wb') as f:
                f.write(key)
        else:
            with open(key_path, 'rb') as f:
                key = f.read()
        self.fernet = Fernet(key)

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS sensitive_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    data BLOB
                )
            ''')

    def save_sensitive(self, user_id, data_dict):
        import json
        data_json = json.dumps(data_dict)
        encrypted = self.fernet.encrypt(data_json.encode('utf-8'))
        with self.conn:
            self.conn.execute(
                'INSERT INTO sensitive_data (user_id, data) VALUES (?, ?)',
                (user_id, encrypted)
            )

    def get_sensitive(self, user_id):
        cur = self.conn.cursor()
        cur.execute('SELECT data FROM sensitive_data WHERE user_id = ? ORDER BY id DESC LIMIT 1', (user_id,))
        row = cur.fetchone()
        if row:
            decrypted = self.fernet.decrypt(row[0]).decode('utf-8')
            import json
            return json.loads(decrypted)
        return None
