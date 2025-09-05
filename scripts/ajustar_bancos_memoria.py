import sqlite3
import os

def ajustar_banco(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Verifica se precisa renomear colunas
    c.execute("PRAGMA table_info(conhecimento)")
    cols = [col[1] for col in c.fetchall()]
    if 'entrada' in cols:
        # Renomeia entrada -> pergunta, resposta -> resposta, tags -> contexto
        c.execute('''ALTER TABLE conhecimento RENAME TO conhecimento_old''')
        c.execute('''
            CREATE TABLE conhecimento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pergunta TEXT,
                resposta TEXT,
                contexto TEXT,
                data_criacao DATETIME,
                autor TEXT,
                midia TEXT
            )
        ''')
        c.execute('''INSERT INTO conhecimento (pergunta, resposta, contexto) SELECT entrada, resposta, tags FROM conhecimento_old''')
        c.execute('DROP TABLE conhecimento_old')
        conn.commit()
    conn.close()

if __name__ == '__main__':
    memoria_dir = os.path.join(os.path.dirname(__file__), '..', 'memoria')
    for fname in os.listdir(memoria_dir):
        if fname.endswith('.db'):
            print(f'Ajustando {fname}...')
            ajustar_banco(os.path.join(memoria_dir, fname))
    print('Ajuste concluído!')
