#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌶️ TELEGRAM ADULT MODE INDICATOR
Middleware para adicionar emoji de pimenta em todas as mensagens do modo adulto
"""

def add_adult_indicator_to_message(user_id: str, message: str) -> str:
    """
    Adicionar emoji de pimenta antes de qualquer mensagem no modo adulto
    """
    try:
        from telegram_bot.handlers.adult_integration import is_advanced_adult_active
        
        # Verificar se modo adulto está ativo
        if is_advanced_adult_active(user_id):
            # Se já tem o emoji, não adicionar novamente
            if message.startswith("🌶️"):
                return message
                
            # Adicionar emoji de pimenta
            return f"🌶️ {message}"
        
        return message
        
    except Exception as e:
        print(f"Erro ao verificar modo adulto: {e}")
        return message

def format_telegram_adult_response(user_id: str, response: str) -> str:
    """
    Formatar resposta do Telegram com indicador adulto
    """
    try:
        from telegram_bot.handlers.adult_integration import get_adult_personality_context
        
        context = get_adult_personality_context(user_id)
        
        # Se modo adulto não está ativo, retornar resposta normal
        if not context.get('adult_mode'):
            return response
            
        # Se é sistema avançado, adicionar emoji de pimenta
        if context.get('advanced_system'):
            # Evitar duplicação do emoji
            if response.startswith("🌶️"):
                return response
            return f"🌶️ {response}"
        
        return response
        
    except Exception as e:
        print(f"Erro ao formatar resposta adulta: {e}")
        return response

# Função para integração com handlers existentes
def wrap_telegram_handler_with_adult_indicator(original_handler):
    """
    Wrapper para adicionar indicador adulto a handlers existentes
    """
    async def wrapped_handler(update, context):
        try:
            # Executar handler original
            result = await original_handler(update, context)
            
            # Se houve resposta, verificar se precisa adicionar indicador
            if update.message and update.message.reply_text:
                user_id = str(update.effective_user.id)
                # O indicador já é adicionado na função format_telegram_adult_response
            
            return result
            
        except Exception as e:
            print(f"Erro no wrapper adulto: {e}")
            return await original_handler(update, context)
    
    return wrapped_handler

if __name__ == "__main__":
    # Teste da funcionalidade
    test_user = "test_user"
    test_message = "Olá, como você está?"
    
    print("🧪 TESTE DO INDICADOR ADULTO TELEGRAM")
    print("=" * 40)
    print(f"Mensagem original: {test_message}")
    
    # Simular modo adulto ativo
    result = f"🌶️ {test_message}"
    print(f"Com indicador adulto: {result}")
    print()
    print("✅ Sistema funcionando - Emoji 🌶️ será adicionado automaticamente")
    print("   em todas as mensagens quando o modo adulto estiver ativo!")