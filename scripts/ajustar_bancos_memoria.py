import sqlite3
import os

def ajustar_banco(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("PRAGMA table_info(conhecimento)")
    cols = [col[1] for col in c.fetchall()]
    
    # Exemplo: Renomeia colunas para o novo padrão, se necessário
    if 'entrada' in cols:
        print(f"    - Renomeando colunas no banco '{os.path.basename(db_path)}'...")
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
        print(f"    - Ajuste concluído para '{os.path.basename(db_path)}'.")
    else:
        print(f"    - O banco '{os.path.basename(db_path)}' já está atualizado. Nenhum ajuste necessário.")
    conn.close()

if __name__ == '__main__':
    memoria_dir = os.path.join(os.path.dirname(__file__), '..', 'memoria')
    print('Iniciando ajuste dos bancos de dados...')
    for fname in os.listdir(memoria_dir):
        if fname.endswith('.db') and 'conhecimento' in fname:
            ajustar_banco(os.path.join(memoria_dir, fname))
    print('Ajuste concluído.')