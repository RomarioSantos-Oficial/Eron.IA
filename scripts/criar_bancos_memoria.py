import sqlite3
import os
from datetime import datetime

# Define o diretório onde os bancos de dados serão salvos
memoria_dir = os.path.join(os.path.dirname(__file__), '..', 'memoria')
if not os.path.exists(memoria_dir):
    os.makedirs(memoria_dir)

# --- Função para criar bancos e tabelas ---
def criar_banco(nome_banco):
    conn = sqlite3.connect(os.path.join(memoria_dir, nome_banco))
    c = conn.cursor()
    
    # Tabela conhecimento
    c.execute('''
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
    
    conn.commit()
    conn.close()
    print(f"Banco {nome_banco} criado em '{memoria_dir}'!")

# --- Função para popular conhecimento inicial ---
def popular_banco(nome_banco, dados):
    conn = sqlite3.connect(os.path.join(memoria_dir, nome_banco))
    c = conn.cursor()
    
    c.executemany('INSERT INTO conhecimento (pergunta, resposta, contexto, autor, data_criacao) VALUES (?, ?, ?, ?, ?)', 
                  [(d[0], d[1], d[2], 'Sistema', datetime.now().isoformat()) for d in dados])
    
    conn.commit()
    conn.close()
    print(f"Banco {nome_banco} populado com dados iniciais!")

if __name__ == '__main__':
    # Relacionamento (maiores de 18)
    criar_banco("conhecimento_relacionamento.db")
    dados_relacionamento = [
        ("O que é um relacionamento saudável?", "Um relacionamento saudável é baseado em respeito mútuo, confiança, comunicação aberta e apoio. É importante que ambos os parceiros se sintam valorizados e seguros.", "#relacionamento,#adulto"),
        ("Como lidar com término de namoro?", "Términos são difíceis. Procure se cercar de amigos e atividades que você gosta. Respirar fundo e refletir sobre o que aprendeu ajuda.", "#relacionamento,#adulto"),
        ("Como melhorar a comunicação com meu parceiro?", "Ouvir com atenção e expressar seus sentimentos de forma clara é essencial. Perguntar e validar o que a outra pessoa sente também ajuda.", "#relacionamento,#adulto")
    ]
    popular_banco("conhecimento_relacionamento.db", dados_relacionamento)

    # Apoio emocional
    criar_banco("conhecimento_emocional.db")
    dados_emocional = [
        ("Estou me sentindo triste", "É normal se sentir assim às vezes. Tente identificar a causa e faça algo que te acalme, como caminhar ou ouvir música.", "#emocional"),
        ("Estou ansioso", "Respire fundo e concentre-se no momento presente. Técnicas de respiração e pequenas pausas ajudam muito.", "#emocional")
    ]
    popular_banco("conhecimento_emocional.db", dados_emocional)

    # Curiosidades e dicas
    criar_banco("conhecimento_curiosidades.db")
    dados_curiosidades = [
        ("Me dê uma dica de hobby", "Que tal tentar pintura, escrita ou jardinagem? Hobbies ajudam a relaxar e descobrir novas habilidades.", "#curiosidade"),
        ("Qual seu nome?", "Meu nome é Eron. Fui criado para ser seu assistente de apoio emocional.", "#sobre")
    ]
    popular_banco("conhecimento_curiosidades.db", dados_curiosidades)