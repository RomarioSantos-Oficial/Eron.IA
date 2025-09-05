import sqlite3
from datetime import datetime

# --- Função para criar bancos e tabelas ---
def criar_banco(nome_banco):
    conn = sqlite3.connect(nome_banco)
    c = conn.cursor()
    
    # Tabela conhecimento
    c.execute('''
    CREATE TABLE IF NOT EXISTS conhecimento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entrada TEXT,
        resposta TEXT,
        tags TEXT
    )
    ''')
    
    # Tabela conversas
    c.execute('''
    CREATE TABLE IF NOT EXISTS conversas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        entrada TEXT,
        resposta TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Banco {nome_banco} criado!")

# --- Função para popular conhecimento inicial ---
def popular_banco(nome_banco, dados):
    conn = sqlite3.connect(nome_banco)
    c = conn.cursor()
    
    c.executemany('INSERT INTO conhecimento (entrada, resposta, tags) VALUES (?, ?, ?)', dados)
    
    conn.commit()
    conn.close()
    print(f"Banco {nome_banco} populado com dados iniciais!")

# --- Criar e popular bancos ---
# Relacionamento (maiores de 18)
criar_banco("conhecimento_relacionamento.db")
dados_relacionamento = [
    ("Como posso lidar com término de namoro?", 
     "Términos são difíceis. Procure se cercar de amigos e atividades que você gosta. Respirar fundo e refletir sobre o que aprendeu ajuda.", 
     "#relacionamento,#adulto"),
    ("Como melhorar a comunicação com meu parceiro?", 
     "Ouvir com atenção e expressar seus sentimentos de forma clara é essencial. Perguntar e validar o que a outra pessoa sente também ajuda.", 
     "#relacionamento,#adulto")
]
popular_banco("conhecimento_relacionamento.db", dados_relacionamento)

# Apoio emocional (todos)
criar_banco("conhecimento_emocional.db")
dados_emocional = [
    ("Estou me sentindo triste", 
     "É normal se sentir assim às vezes. Tente identificar a causa e faça algo que te acalme, como caminhar ou ouvir música.", 
     "#emocional"),
    ("Estou ansioso", 
     "Respire fundo e concentre-se no momento presente. Técnicas de respiração e pequenas pausas ajudam muito.", 
     "#emocional")
]
popular_banco("conhecimento_emocional.db", dados_emocional)

# Curiosidades e dicas (todos)
criar_banco("conhecimento_curiosidades.db")
dados_curiosidades = [
    ("Me dê uma dica de hobby", 
     "Que tal tentar pintura, escrita ou jardinagem? Hobbies ajudam a relaxar e descobrir novas habilidades.", 
     "#curiosidade"),
    ("Sugestão de livro ou filme", 
     "Livros como 'O Pequeno Príncipe' ou filmes como 'A Vida é Bela' podem ser inspiradores.", 
     "#curiosidade")
]
popular_banco("conhecimento_curiosidades.db", dados_curiosidades)
