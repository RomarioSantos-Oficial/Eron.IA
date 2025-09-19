import threading
import os
import sys
import webbrowser
import argparse
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

# Adiciona a pasta raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa a aplicação web e a função do bot
from app import app
from telegram_bot import main as telegram_bot_main
from src.user_profile_db import UserProfileDB

# Carrega as variáveis de ambiente
load_dotenv()

# Instância única do banco de dados de perfil
user_profile_db = UserProfileDB()

def run_flask_app():
    print("Iniciando o servidor web do Eron...")
    # Passa a instância do banco de dados para o app.py
    app.user_profile_db = user_profile_db
    app.run(debug=True, use_reloader=False)

def run_telegram_bot_safe(application):
    try:
        print("Iniciando o bot do Telegram...")
        # Passa a instância do banco de dados para o telegram_bot.py
        application.user_profile_db = user_profile_db
        application.run_polling()
    except KeyboardInterrupt:
        print("\nSinal de interrupção recebido. Desligando...")

def start_app():
    parser = argparse.ArgumentParser(description="Inicia o Eron, seu assistente de IA.")
    parser.add_argument('--no-browser', action='store_true', help='Não abrir o navegador automaticamente.')
    args = parser.parse_args()

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_BOT_TOKEN:
        print("Erro: O token do bot do Telegram não foi encontrado.")
        return

    # Inicializa o bot
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Chama a função que adiciona os handlers ao bot, passando a instância do banco de dados
    telegram_bot_main(application, user_profile_db)

    # Inicia o servidor Flask em uma thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    if not args.no_browser:
        flask_url = "http://127.0.0.1:5000"
        print(f"Abrindo navegador para {flask_url}...")
        webbrowser.open_new(flask_url)

    # Inicia o bot do Telegram
    run_telegram_bot_safe(application)

if __name__ == "__main__":
    start_app()