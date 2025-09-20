"""
Handlers de mensagens do bot Telegram
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler principal para mensagens de texto"""
    if not update.message or not update.message.text:
        return
    
    user_id = str(update.effective_user.id)
    user_message = update.message.text
    
    try:
        # Verificar se está no fluxo de personalização completa
        personalization_step = context.user_data.get('personalization_step')
        print(f"[DEBUG] personalization_step: {personalization_step}")
        print(f"[DEBUG] context.user_data: {context.user_data}")
        
        if personalization_step:
            print(f"[DEBUG] Processando personalização - step: {personalization_step}")
            await process_full_personalization_input(update, context, user_message)
            return
        
        # Verificar se está aguardando entrada de personalização
        waiting_for = context.user_data.get('waiting_for')
        if waiting_for:
            await process_personalization_input(update, context, waiting_for, user_message)
            return
        
        # Importar função de resposta da aplicação principal
        import sys
        import os
        # Adicionar o path para importar web.app
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from web.app import get_llm_response
        
        # Log da mensagem recebida
        logger.info(f"Mensagem recebida de {user_id}: {user_message}")
        
        # Obter resposta do sistema de IA
        response = get_llm_response(user_message, user_id=user_id)
        
        # Enviar resposta
        if response:
            # Dividir respostas longas se necessário
            if len(response) > 4096:  # Limite do Telegram
                chunks = [response[i:i+4096] for i in range(0, len(response), 4096)]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(response)
        else:
            await update.message.reply_text("Desculpe, não consegui processar sua mensagem. Tente novamente!")
    
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        await update.message.reply_text(
            "Oops! Algo deu errado. Por favor, tente novamente em alguns instantes. 😔"
        )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para documentos enviados"""
    await update.message.reply_text(
        "📄 Obrigado pelo documento! No momento não posso processar arquivos, "
        "mas você pode me descrever o conteúdo que eu posso ajudar com informações sobre ele."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para fotos enviadas"""
    await update.message.reply_text(
        "📷 Que foto interessante! Infelizmente não posso analisar imagens ainda, "
        "mas você pode me descrever o que há na foto que posso conversar sobre isso!"
    )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para áudios enviados"""
    await update.message.reply_text(
        "🎤 Recebi seu áudio! No momento não posso processar mensagens de voz, "
        "mas você pode escrever sua mensagem que respondo rapidamente!"
    )

async def process_personalization_input(update: Update, context: ContextTypes.DEFAULT_TYPE, waiting_for: str, user_input: str):
    """Processar entrada de personalização"""
    user_id = str(update.effective_user.id)
    
    try:
        # Importar funções necessárias
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from core.user_profile_db import UserProfileDB as UserService
        from telegram_bot.handlers.personalization_handlers import start_personalization_menu
        
        user_service = UserService()
        
        if waiting_for == 'user_name':
            user_service.update_profile(user_id, user_name=user_input)
            await update.message.reply_text(f"✅ Nome salvo: {user_input}")
            
        elif waiting_for == 'user_age':
            try:
                age = int(user_input)
                if age < 0 or age > 120:
                    raise ValueError("Idade inválida")
                age_category = "18+" if age >= 18 else "<18"
                user_service.update_profile(user_id, user_age=age_category)
                await update.message.reply_text(f"✅ Idade salva: {age} anos")
            except ValueError:
                await update.message.reply_text("❌ Por favor, digite uma idade válida (número)")
                return
                
        elif waiting_for == 'bot_name':
            user_service.update_profile(user_id, bot_name=user_input)
            await update.message.reply_text(f"✅ Agora me chamo: {user_input}")
        
        # Limpar estado de espera
        context.user_data.pop('waiting_for', None)
        
        # Voltar ao menu de personalização
        await start_personalization_menu(update, context)
        
    except Exception as e:
        logger.error(f"Erro ao processar entrada de personalização: {e}")
        await update.message.reply_text("❌ Erro ao salvar. Tente novamente.")
        context.user_data.pop('waiting_for', None)

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para vídeos enviados"""
    await update.message.reply_text(
        "🎥 Obrigado pelo vídeo! Não posso assistir vídeos ainda, "
        "mas você pode me contar sobre o que se trata que posso ajudar!"
    )

async def process_full_personalization_input(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str):
    """Processar fluxo completo de personalização pós-reset"""
    user_id = str(update.effective_user.id)
    step = context.user_data.get('personalization_step', 'user_name')
    
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from core.user_profile_db import UserProfileDB as UserService
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        user_service = UserService()
        
        # Processar cada passo da personalização
        if step == 'user_name':
            user_service.update_profile(user_id, user_name=user_input)
            context.user_data['personalization_step'] = 'user_gender'
            
            keyboard = [
                [InlineKeyboardButton("👨 Masculino", callback_data="set_user_gender_masculino")],
                [InlineKeyboardButton("👩 Feminino", callback_data="set_user_gender_feminino")],
                [InlineKeyboardButton("🌟 Outro", callback_data="set_user_gender_outro")],
                [InlineKeyboardButton("🤐 Prefiro não dizer", callback_data="set_user_gender_prefiro_nao_dizer")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ Nome salvo: **{user_input}**\n\n"
                "**Passo 2/8: Seu Gênero**\n\n"
                "👤 Como você se identifica?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        elif step == 'birth_date':
            # Validar formato de data
            try:
                from datetime import datetime
                birth_date = datetime.strptime(user_input, "%d/%m/%Y")
                today = datetime.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                
                if age < 0 or age > 120:
                    raise ValueError("Idade inválida")
                
                # Salvar data de nascimento e calcular idade
                user_service.update_profile(user_id, birth_date=birth_date.strftime("%Y-%m-%d"))
                context.user_data['user_age'] = age
                context.user_data['personalization_step'] = 'bot_gender'
                
                age_status = "🔞 Acesso completo" if age >= 18 else "👶 Acesso limitado (menu permite acesso total)"
                
                keyboard = [
                    [InlineKeyboardButton("👨 Masculino", callback_data="set_bot_gender_masculino")],
                    [InlineKeyboardButton("👩 Feminino", callback_data="set_bot_gender_feminino")],
                    [InlineKeyboardButton("⚖️ Neutro", callback_data="set_bot_gender_neutro")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    f"✅ Data de nascimento salva!\n"
                    f"📊 **Idade calculada:** {age} anos\n"
                    f"🎯 **Status:** {age_status}\n\n"
                    "**Passo 4/8: Gênero do Bot**\n\n"
                    "🤖 Que gênero você prefere para seu assistente?",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                
            except ValueError:
                await update.message.reply_text(
                    "❌ **Formato de data inválido!**\n\n"
                    "Por favor, digite sua data de nascimento no formato:\n"
                    "**DD/MM/AAAA**\n\n"
                    "Exemplo: 15/03/1995"
                )
                return
        
        elif step == 'bot_name':
            user_service.update_profile(user_id, bot_name=user_input)
            context.user_data['personalization_step'] = 'bot_gender'
            
            keyboard = [
                [InlineKeyboardButton("👨 Masculino", callback_data="set_bot_gender_masculino")],
                [InlineKeyboardButton("👩 Feminino", callback_data="set_bot_gender_feminino")],
                [InlineKeyboardButton("⚖️ Neutro", callback_data="set_bot_gender_neutro")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ Agora me chamo: **{user_input}**\n\n"
                "**Passo 5/8: Gênero do Bot**\n\n"
                "🤖 Qual gênero você prefere para mim?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        elif step == 'bot_name_custom':
            user_service.update_profile(user_id, bot_name=user_input)
            context.user_data['personalization_step'] = 'bot_personality'
            
            # Verificar se é maior de idade para mostrar opções adultas
            user_age = context.user_data.get('user_age', 0)
            
            keyboard = [
                [InlineKeyboardButton("😊 Amigável", callback_data="set_personality_amigavel")],
                [InlineKeyboardButton("💼 Profissional", callback_data="set_personality_profissional")],
                [InlineKeyboardButton("🎉 Divertido", callback_data="set_personality_divertido")],
                [InlineKeyboardButton("🎭 Formal", callback_data="set_personality_formal")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ Nome personalizado salvo: **{user_input}**\n\n"
                "**Passo 6/8: Personalidade do Bot**\n\n"
                "🎭 Que personalidade você prefere para mim?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        else:
            await update.message.reply_text("❌ Erro no fluxo de personalização.")
    
    except Exception as e:
        logger.error(f"Erro no fluxo de personalização: {e}")
        await update.message.reply_text("❌ Erro ao processar. Tente novamente.")
