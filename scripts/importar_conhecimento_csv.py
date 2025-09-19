import sqlite3
import csv
import os
import sys

def importar_csv_para_banco(csv_path, db_path):
    if not os.path.exists(csv_path):
        print(f"Arquivo CSV não encontrado: {csv_path}")
        return
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
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                conn.execute(
                    'INSERT INTO conhecimento (pergunta, resposta, contexto, data_criacao, autor, midia) VALUES (?, ?, ?, datetime("now"), ?, ?)',
                    (
                        row['pergunta'],
                        row['resposta'],
                        row.get('contexto', ''),
                        row.get('autor', ''),
                        row.get('midia', '')
                    )
                )
    print(f"Importação concluída para {db_path}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python importar_conhecimento_csv.py <arquivo_csv> <banco_destino.db>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    db_file = sys.argv[2]
    memoria_dir = os.path.join(os.path.dirname(__file__), '..', 'memoria')
    db_path = os.path.join(memoria_dir, db_file)
    
    importar_csv_para_banco(csv_file, db_path)