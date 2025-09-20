import threading
import os
import sys
import webbrowser
import argparse
from dotenv import load_dotenv
import atexit

# Adiciona a pasta raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa a aplicação web e a função do bot
from web.app import app
from telegram_bot.bot_main import create_telegram_bot
from core.user_profile_db import UserProfileDB as DatabaseManager

# Carrega as variáveis de ambiente
load_dotenv()

# Caminho para o arquivo de trava
LOCK_FILE = ".eron.lock"

def cleanup_lock_file():
    """Remove o arquivo de trava se ele existir."""
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
            print("\nArquivo de trava removido.")
        except OSError as e:
            print(f"Erro ao remover arquivo de trava: {e}")

# Garante que o arquivo de trava seja removido ao sair do programa
atexit.register(cleanup_lock_file)

# Instância única do gerenciador de banco
database_manager = DatabaseManager()

def run_flask_app():
    print("Iniciando o servidor web do Eron...")
    # Passa a instância do banco de dados para o app.py
    app.database_manager = database_manager
    app.run(debug=True, use_reloader=False)

def run_telegram_bot_safe():
    try:
        print("Iniciando o bot do Telegram...")
        bot = create_telegram_bot()
        bot.run()
    except Exception as e:
        print(f"Erro inesperado no bot do Telegram: {e}")
    finally:
        print("Encerrando o bot do Telegram.")

def start_app():
    # Verifica se o arquivo de trava existe
    if os.path.exists(LOCK_FILE):
        print("Erro: Outra instância do Eron já está em execução.")
        try:
            with open(LOCK_FILE, "r") as f:
                pid = f.read()
                print(f"Processo existente (PID: {pid}).")
            print("Se isso for um erro, remova o arquivo '.eron.lock' e tente novamente.")
        except Exception as e:
            print(f"Não foi possível ler o arquivo de trava: {e}")
        sys.exit(1)

    # Cria o arquivo de trava
    try:
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))
        print("Arquivo de trava criado.")
    except IOError as e:
        print(f"Erro ao criar arquivo de trava: {e}")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Inicia o Eron, seu assistente de IA.")
    parser.add_argument('--no-browser', action='store_true', help='Não abrir o navegador automaticamente.')
    args = parser.parse_args()

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_BOT_TOKEN:
        print("Erro: O token do bot do Telegram não foi encontrado.")
        return

    # Inicia o servidor Flask em uma thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    if not args.no_browser:
        flask_url = "http://127.0.0.1:5000"
        print(f"Abrindo navegador para {flask_url}...")
        webbrowser.open_new(flask_url)

    # Inicia o bot do Telegram
    run_telegram_bot_safe()

if __name__ == "__main__":
    start_app()