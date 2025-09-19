import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters
from src.memory import EronMemory
from app import get_llm_response
import re

# Estados da conversa
GET_NAME = 1
GET_AGE = 2
GET_GENDER = 3

# Configurar o logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Instância da memória de conversa (mantém-se local)
memory = EronMemory()

# Funções de conversação para /definir_perfil
async def definir_perfil_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Vamos definir seu perfil! Qual é o seu nome?")
    return GET_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_name = update.message.text
    user_profile_db = context.application.user_profile_db
    
    profile = user_profile_db.get_profile(user_id) or {}
    profile['user_name'] = user_name
    
    user_profile_db.save_profile(user_id=user_id, **profile)
    await update.message.reply_text(f"Obrigado, {user_name}! E qual a sua idade?")
    return GET_AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_age_str = update.message.text.strip()
    user_profile_db = context.application.user_profile_db
    try:
        user_age = int(user_age_str)
        if user_age < 18:
            await update.message.reply_text("Você deve ter 18 anos ou mais para usar este bot. A conversa será cancelada.")
            return ConversationHandler.END
        
        profile = user_profile_db.get_profile(user_id) or {}
        profile['user_age'] = user_age_str
        
        user_profile_db.save_profile(user_id=user_id, **profile)
        await update.message.reply_text("Ótimo! E qual o seu gênero? (Masculino, Feminino, Outro)")
        return GET_GENDER
    except ValueError:
        await update.message.reply_text("Idade inválida. Por favor, digite um número.")
        return GET_AGE
        
async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_gender = update.message.text
    user_profile_db = context.application.user_profile_db
    
    profile = user_profile_db.get_profile(user_id) or {}
    profile['user_gender'] = user_gender
    
    user_profile_db.save_profile(user_id=user_id, **profile)
    await update.message.reply_text("Tudo pronto! Seu perfil foi salvo. Você pode começar a conversar.")
    return ConversationHandler.END
    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("A definição do perfil foi cancelada.")
    return ConversationHandler.END

# Função para o comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Olá, {user_name}! Eu sou o Eron, seu assistente pessoal. O que posso fazer por você? Diga "meu nome é [seu nome]" para eu me lembrar de você!'
    )

# Função para o comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Olá! Sou um assistente de apoio emocional. Estou aqui para conversar e ajudar com o que precisar. Use os seguintes comandos:\n'
             '/definir_perfil - Para eu me lembrar do seu nome, idade e gênero.\n'
             '/cancelar - Para cancelar a definição do perfil.\n'
             '/chat - Para iniciar uma conversa normal.\n'
             '/personalizar - Para mudar meu nome, gênero e outras configurações.\n\n'
             'Fique à vontade para desabafar ou fazer qualquer pergunta.'
    )

# Função de chat
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = str(update.effective_user.id)
    user_profile_db = context.application.user_profile_db
    
    profile = user_profile_db.get_profile(user_id)
    if profile:
        user_name = profile.get('user_name', update.effective_user.first_name)
        bot_name = profile.get('bot_name', 'Eron')
    else:
        user_name = update.effective_user.first_name
        bot_name = 'Eron'

    response = get_llm_response(user_message, user_profile=profile)
    if not response:
        response = "Desculpe, não consegui me conectar com a IA no momento. Por favor, verifique se o servidor do LM Studio está rodando."
    
    memory.save_message(user_message, response)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response
    )

def main(application, user_profile_db):
    logging.info("Adicionando handlers...")
    
    # Adiciona a instância do banco de dados ao objeto de aplicação
    application.user_profile_db = user_profile_db
    
    # ConversationHandler para definir o perfil
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('definir_perfil', definir_perfil_start)],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            GET_GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
        },
        fallbacks=[CommandHandler('cancelar', cancel)]
    )
    
    # Adicionar os handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))