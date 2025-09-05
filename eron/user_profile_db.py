import sqlite3
import os

class UserProfileDB:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'memoria', 'user_profiles.db')
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE,
                    user_name TEXT,
                    user_age TEXT,
                    user_gender TEXT,
                    bot_name TEXT,
                    bot_gender TEXT,
                    bot_avatar TEXT
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
                'bot_avatar': row[5]
            }
        return None

    def save_profile(self, user_id, user_name, user_age, user_gender, bot_name, bot_gender, bot_avatar):
        with self.conn:
            self.conn.execute('''
                INSERT OR REPLACE INTO profiles (user_id, user_name, user_age, user_gender, bot_name, bot_gender, bot_avatar)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, user_name, user_age, user_gender, bot_name, bot_gender, bot_avatar))
