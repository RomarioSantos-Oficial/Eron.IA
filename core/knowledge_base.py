import os
import sqlite3

class KnowledgeBase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.initialize_db()
    
    def initialize_db(self):
        conn = sqlite3.connect(os.path.join(self.db_path, 'knowledge.db'))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                response TEXT,
                feedback TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_all_feedback(self):
        conn = sqlite3.connect(os.path.join(self.db_path, 'knowledge.db'))
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM feedback ORDER BY timestamp DESC')
        feedbacks = cursor.fetchall()
        
        conn.close()
        return feedbacks
