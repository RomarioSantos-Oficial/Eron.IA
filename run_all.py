#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 ERON.IA - SISTEMA UNIFICADO WEB + TELEGRAM
Launcher principal unificado para iniciar ambos os sistemas
"""


import threading
import os
import sys
import argparse
import time
from datetime import datetime
from dotenv import load_dotenv
import atexit

# Banner visual
def print_banner():
    print("=" * 80)
    print("🤖 ERON.IA - SISTEMA UNIFICADO")
    print("🌐 Web Interface + 📱 Telegram Bot")
    print("=" * 80)
    print(f"⏰ Iniciando às {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)

# Adiciona a pasta raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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


# Detectar arquivos de app e bot
def detect_app_file():
    app_files = ["web/app.py", "app.py"]
    for file in app_files:
        if os.path.exists(file):
            return file
    return None

def detect_bot_file():
    bot_files = ["simple_telegram_bot.py", "telegram_bot/bot_main.py", "telegram_bot.py"]
    for file in bot_files:
        if os.path.exists(file):
            return file
    return None

# Funções para rodar sistemas
def run_web_app(app_file):
    print("🔄 Iniciando Web App...")
    time.sleep(2)
    os.system(f'python "{app_file}"')

def run_telegram_bot(bot_file):
    print("🔄 Iniciando Telegram Bot...")
    os.system(f'python "{bot_file}"')


def start_app():
    print_banner()
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
    parser.add_argument('--open-browser', action='store_true', help='Abrir o navegador automaticamente.')
    args = parser.parse_args()

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_BOT_TOKEN:
        print("Erro: O token do bot do Telegram não foi encontrado.")
        return

    app_file = detect_app_file()
    bot_file = detect_bot_file()
    if not app_file:
        print("❌ Erro: app.py não encontrado!")
        sys.exit(1)
    if not bot_file:
        print("❌ Erro: Nenhum arquivo do bot Telegram encontrado!")
        sys.exit(1)

    print(f"✅ Usando app: {app_file}")
    print(f"✅ Usando bot: {bot_file}")

    print("🎯 FUNCIONALIDADES DISPONÍVEIS:")
    print("  WEB (http://localhost:5000):")
    print("    - 🏠 Dashboard principal (/)")
    print("    - 👤 Sistema de usuários (/login, /register)")
    print("    - 🔞 Sistema adulto (/adult/*)")
    print("    - ⚙️  Configurações (/preferences)")
    print("    - 📧 Sistema de email (/reset_password)")
    print()
    print("  TELEGRAM:")
    print("    - 💬 Chat normal (para menores)")
    print("    - 🔞 /adult_mode (sistema adulto)")
    print("    - ⚙️  /adult_config (configurações)")
    print("    - 📚 /adult_train (treinamento)")
    print("    - 📊 /adult_status (status)")
    print()
    print("🔄 Iniciando ambos os sistemas...")
    print()

    # Criar threads para executar ambos os sistemas
    telegram_thread = threading.Thread(target=lambda: run_telegram_bot(bot_file), daemon=True)
    web_thread = threading.Thread(target=lambda: run_web_app(app_file), daemon=True)

    telegram_thread.start()
    web_thread.start()

    # Abrir navegador apenas se o usuário pedir
    if args.open_browser:
        flask_url = "http://127.0.0.1:5000"
        print(f"Abrindo navegador para {flask_url}...")
        import webbrowser
        webbrowser.open_new(flask_url)

    try:
        telegram_thread.join()
        web_thread.join()
    except KeyboardInterrupt:
        print("\n🛑 Encerrando sistema...")
        print("✅ Sistema encerrado com sucesso!")

if __name__ == "__main__":
    start_app()