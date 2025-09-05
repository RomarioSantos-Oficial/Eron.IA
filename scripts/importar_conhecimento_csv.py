import sqlite3
import csv
import os
import sys

 # Uso: python importar_conhecimento_csv.py <arquivo_csv> <banco_destino.db>
 # O CSV pode ter colunas: pergunta,resposta,contexto,autor,midia

def importar_csv_para_banco(csv_path, db_path):
    # Uso: python importar_conhecimento_csv.py <arquivo_csv> <banco_destino.db>
    # O CSV pode ter colunas: pergunta,resposta,contexto,autor,midia
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
    importar_csv_para_banco(sys.argv[1], sys.argv[2])
