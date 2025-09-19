import os
import sqlite3

def atualizar_banco_usuarios():
    """Atualiza a estrutura do banco de dados de usuários"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'memoria', 'user_profiles.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Recriando tabela com nova estrutura...")

    # Criar tabela temporária com nova estrutura
    cursor.execute('''
    CREATE TABLE profiles_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE,
        username TEXT UNIQUE,
        password_hash TEXT,
        email TEXT UNIQUE,
        user_name TEXT,
        user_age TEXT,
        user_gender TEXT,
        bot_name TEXT,
        bot_gender TEXT,
        bot_avatar TEXT,
        has_mature_access BOOLEAN DEFAULT 0,
        email_confirmed BOOLEAN DEFAULT 0,
        confirmation_token TEXT,
        reset_token TEXT,
        reset_token_expiry TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Tentar transferir dados da tabela antiga, ignorando erros de constraint
    try:
        cursor.execute('''
        INSERT INTO profiles_new (
            id, user_id, username, password_hash, email, user_name, user_age, user_gender,
            bot_name, bot_gender, bot_avatar, has_mature_access, email_confirmed,
            confirmation_token, reset_token, reset_token_expiry, created_at
        )
        SELECT 
            id, user_id, username, password_hash, email, user_name, user_age, user_gender,
            bot_name, bot_gender, bot_avatar, has_mature_access, email_confirmed,
            confirmation_token, reset_token, reset_token_expiry, created_at 
        FROM profiles
        ''')
    except sqlite3.Error as e:
        print(f"Erro ao transferir dados: {e}")
        
    # Remover tabela antiga
    cursor.execute('DROP TABLE profiles')
    
    # Renomear nova tabela
    cursor.execute('ALTER TABLE profiles_new RENAME TO profiles')

    conn.commit()
    conn.close()
    print("Banco de dados atualizado com sucesso!")

    conn.commit()
    conn.close()
    print("Banco de dados atualizado com sucesso!")

if __name__ == '__main__':
    atualizar_banco_usuarios()