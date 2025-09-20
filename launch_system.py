#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 ERON.IA - SISTEMA UNIFICADO WEB + TELEGRAM
Launcher principal para iniciar ambos os sistemas
"""

import os
import sys
import threading
import time
from datetime import datetime

def print_banner():
    """Banner de inicialização"""
    print("=" * 80)
    print("🤖 ERON.IA - SISTEMA UNIFICADO")
    print("🌐 Web Interface + 📱 Telegram Bot")
    print("=" * 80)
    print(f"⏰ Iniciando às {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)

def run_telegram_bot():
    """Executar bot do Telegram"""
    try:
        print("🔄 Iniciando Telegram Bot...")
        os.system('python telegram_bot.py')
    except Exception as e:
        print(f"❌ Erro no Telegram Bot: {e}")

def run_web_app():
    """Executar aplicação web"""
    try:
        print("🔄 Iniciando Web App...")
        time.sleep(2)  # Dar tempo para o telegram inicializar
        os.system('python app.py')
    except Exception as e:
        print(f"❌ Erro na Web App: {e}")

def main():
    """Função principal"""
    print_banner()
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('app.py') or not os.path.exists('telegram_bot.py'):
        print("❌ Erro: Execute este script no diretório raiz do projeto!")
        sys.exit(1)
    
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
    telegram_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    web_thread = threading.Thread(target=run_web_app, daemon=True)
    
    # Iniciar threads
    telegram_thread.start()
    web_thread.start()
    
    try:
        # Aguardar as threads
        telegram_thread.join()
        web_thread.join()
    except KeyboardInterrupt:
        print("\n🛑 Encerrando sistema...")
        print("✅ Sistema encerrado com sucesso!")

if __name__ == "__main__":
    main()