"""
Script para limpar webhook do bot Telegram e resolver conflitos
"""
import asyncio
import os
from telegram import Bot

# Token do bot
TELEGRAM_TOKEN = "8219164464:AAEqhMd1Cc7B03LdemrbEsTSZXcddo7V1aQ"

async def clear_webhook():
    """Limpa webhook e resolve conflitos"""
    bot = Bot(token=TELEGRAM_TOKEN)
    
    try:
        print("Removendo webhook...")
        await bot.delete_webhook()
        print("✅ Webhook removido com sucesso!")
        
        print("Testando conexão...")
        bot_info = await bot.get_me()
        print(f"✅ Bot conectado: {bot_info.first_name} (@{bot_info.username})")
        
        print("Limpando updates pendentes...")
        updates = await bot.get_updates(limit=100)
        if updates:
            print(f"📥 Encontrados {len(updates)} updates pendentes")
            # Marcar como lidos pegando o último offset
            if updates:
                last_update_id = updates[-1].update_id
                await bot.get_updates(offset=last_update_id + 1, limit=1)
                print("✅ Updates pendentes limpos!")
        else:
            print("✅ Nenhum update pendente")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n🔄 Bot pronto para iniciar sem conflitos!")

if __name__ == "__main__":
    asyncio.run(clear_webhook())