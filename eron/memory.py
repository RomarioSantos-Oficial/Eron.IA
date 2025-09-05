import sqlite3

import os

class EronMemory:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'memoria', 'eron_memory.db')
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_message TEXT,
                    eron_response TEXT
                )
            ''')

    def save_message(self, user_message, eron_response):
        with self.conn:
            self.conn.execute(
                'INSERT INTO messages (user_message, eron_response) VALUES (?, ?)',
                (user_message, eron_response)
            )

    def get_all_messages(self):
        with self.conn:
            return self.conn.execute('SELECT * FROM messages').fetchall()