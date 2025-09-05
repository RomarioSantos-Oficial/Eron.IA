import os
import sqlite3
from datetime import datetime

def get_db_paths(memoria_dir):
    return [
        os.path.join(memoria_dir, f)
        for f in os.listdir(memoria_dir)
        if f.endswith('.db')
    ]

class KnowledgeBase:
    def save_feedback(self, pergunta, resposta, usuario, feedback, tema=None):
        # Cria tabela de feedback se não existir
        now = datetime.now().isoformat(sep=' ', timespec='seconds')
        if tema:
            db_path = os.path.join(self.memoria_dir, f'{tema}.db')
            if not os.path.exists(db_path):
                self._ensure_table(db_path)
                self.db_paths.append(db_path)
            conn = sqlite3.connect(db_path)
            with conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pergunta TEXT,
                        resposta TEXT,
                        usuario TEXT,
                        feedback TEXT,
                        data DATETIME
                    )
                ''')
                conn.execute(
                    'INSERT INTO feedback (pergunta, resposta, usuario, feedback, data) VALUES (?, ?, ?, ?, ?)',
                    (pergunta, resposta, usuario, feedback, now)
                )
            conn.close()
        else:
            for db_path in self.db_paths:
                conn = sqlite3.connect(db_path)
                with conn:
                    conn.execute('''
                        CREATE TABLE IF NOT EXISTS feedback (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            pergunta TEXT,
                            resposta TEXT,
                            usuario TEXT,
                            feedback TEXT,
                            data DATETIME
                        )
                    ''')
                    conn.execute(
                        'INSERT INTO feedback (pergunta, resposta, usuario, feedback, data) VALUES (?, ?, ?, ?, ?)',
                        (pergunta, resposta, usuario, feedback, now)
                    )
                conn.close()
    def search_by_tag(self, tag, tema=None, limit=5):
        dbs = self.db_paths
        if tema:
            themed_db = os.path.join(self.memoria_dir, f'{tema}.db')
            if os.path.exists(themed_db):
                dbs = [themed_db]
        results = []
        tag_like = f'%{tag}%'
        for db_path in dbs:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            try:
                cur.execute('SELECT pergunta, resposta, contexto, midia FROM conhecimento WHERE contexto LIKE ? OR tags LIKE ? LIMIT ?', (tag_like, tag_like, limit))
                results.extend(cur.fetchall())
            except Exception:
                pass
            conn.close()
        return results
    def save_conversa(self, usuario, entrada, resposta, tema=None):
        now = datetime.now().isoformat(sep=' ', timespec='seconds')
        if tema:
            db_path = os.path.join(self.memoria_dir, f'{tema}.db')
            if not os.path.exists(db_path):
                self._ensure_table(db_path)
                self.db_paths.append(db_path)
            conn = sqlite3.connect(db_path)
            with conn:
                conn.execute(
                    'CREATE TABLE IF NOT EXISTS conversas (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, entrada TEXT, resposta TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)'
                )
                conn.execute(
                    'INSERT INTO conversas (usuario, entrada, resposta, timestamp) VALUES (?, ?, ?, ?)',
                    (usuario, entrada, resposta, now)
                )
            conn.close()
        else:
            for db_path in self.db_paths:
                conn = sqlite3.connect(db_path)
                with conn:
                    conn.execute(
                        'CREATE TABLE IF NOT EXISTS conversas (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, entrada TEXT, resposta TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)'
                    )
                    conn.execute(
                        'INSERT INTO conversas (usuario, entrada, resposta, timestamp) VALUES (?, ?, ?, ?)',
                        (usuario, entrada, resposta, now)
                    )
                conn.close()

    def get_user_history(self, usuario, tema=None, limit=10):
        # Retorna as últimas interações do usuário
        dbs = self.db_paths
        if tema:
            themed_db = os.path.join(self.memoria_dir, f'{tema}.db')
            if os.path.exists(themed_db):
                dbs = [themed_db]
        history = []
        for db_path in dbs:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute('SELECT entrada, resposta, timestamp FROM conversas WHERE usuario = ? ORDER BY timestamp DESC LIMIT ?', (usuario, limit))
            history.extend(cur.fetchall())
            conn.close()
        return history
    def __init__(self, memoria_dir):
        self.memoria_dir = memoria_dir
        self.db_paths = get_db_paths(memoria_dir)
        self.ensure_tables()

    def ensure_tables(self):
        for db_path in self.db_paths:
            self._ensure_table(db_path)

    def _ensure_table(self, db_path):
        conn = sqlite3.connect(db_path)
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conhecimento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pergunta TEXT,
                    resposta TEXT,
                    contexto TEXT,
                    data_criacao DATETIME,
                    autor TEXT,
                    midia TEXT
                )
            ''')
        conn.close()

    def search_answer(self, pergunta, tema=None):
        pergunta = pergunta.strip().lower()
        dbs = self.db_paths
        if tema:
            themed_db = os.path.join(self.memoria_dir, f'{tema}.db')
            if os.path.exists(themed_db):
                dbs = [themed_db]
        # Busca exata
        for db_path in dbs:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute('SELECT resposta FROM conhecimento WHERE lower(pergunta) = ?', (pergunta,))
            row = cur.fetchone()
            if row:
                conn.close()
                return row[0]
            # Busca por similaridade (LIKE)
            cur.execute('SELECT resposta FROM conhecimento WHERE lower(pergunta) LIKE ?', (f'%{pergunta}%',))
            row2 = cur.fetchone()
            if row2:
                conn.close()
                return row2[0]
            # Busca por tags/contexto
            cur.execute('SELECT resposta FROM conhecimento WHERE contexto LIKE ?', (f'%{tema}%',))
            row3 = cur.fetchone()
            if row3:
                conn.close()
                return row3[0]
            conn.close()
        return None

    def save_qa(self, pergunta, resposta, contexto=None, autor=None, tema=None):
        now = datetime.now().isoformat(sep=' ', timespec='seconds')
        if tema:
            db_path = os.path.join(self.memoria_dir, f'{tema}.db')
            if not os.path.exists(db_path):
                # Só cria o arquivo se for necessário
                self._ensure_table(db_path)
                self.db_paths.append(db_path)
            conn = sqlite3.connect(db_path)
            with conn:
                conn.execute(
                    'INSERT INTO conhecimento (pergunta, resposta, contexto, data_criacao, autor) VALUES (?, ?, ?, ?, ?)',
                    (pergunta, resposta, contexto, now, autor)
                )
            conn.close()
        else:
            for db_path in self.db_paths:
                conn = sqlite3.connect(db_path)
                with conn:
                    conn.execute(
                        'INSERT INTO conhecimento (pergunta, resposta, contexto, data_criacao, autor) VALUES (?, ?, ?, ?, ?)',
                        (pergunta, resposta, contexto, now, autor)
                    )
                conn.close()

    def refresh(self):
        self.db_paths = get_db_paths(self.memoria_dir)
