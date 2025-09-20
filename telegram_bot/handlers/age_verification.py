"""
Handlers para verificação de idade e controle de acesso adulto no Telegram
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.check import AdultAccessSystem
from src.user_profile_db import UserProfileDB

adult_system = AdultAccessSystem()
user_db = UserProfileDB()

async def age_verification_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para verificação de idade inicial"""
    user_id = str(update.effective_user.id)
    
    # Verificar status atual
    user_status = adult_system.check_age(user_id)
    
    if user_status['user_age'] is None:
        # Primeira verificação
        keyboard = [
            [InlineKeyboardButton("✅ Tenho 18+ anos", callback_data="age_confirm_18")],
            [InlineKeyboardButton("❌ Tenho menos de 18 anos", callback_data="age_confirm_under18")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔞 **Verificação de Idade Obrigatória**\n\n"
            "Para acessar algumas funcionalidades avançadas, preciso verificar sua idade.\n\n"
            "⚠️ **ATENÇÃO:** Algumas funcionalidades do bot são direcionadas apenas para usuários maiores de 18 anos.\n\n"
            "Por favor, confirme sua idade:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        # Já verificado
        status_emoji = "🔞" if user_status['is_adult'] else "👶"
        adult_status = "Ativado" if user_status['adult_mode_active'] else "Inativo"
        
        message = f"{status_emoji} **Status da Conta**\n\n"
        message += f"📅 Idade: {user_status['user_age']} anos\n"
        message += f"🔞 Modo Adulto: {adult_status}\n"
        
        if user_status['is_adult']:
            message += f"⚡ Nível de Intensidade: {user_status['adult_intensity_level']}/5\n"
            message += f"💫 Estilo: {user_status['interaction_style']}\n"
            
            keyboard = [
                [InlineKeyboardButton("⚙️ Configurar Modo Adulto", callback_data="adult_config_menu")],
                [InlineKeyboardButton("🔄 Alterar Idade", callback_data="age_change")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            keyboard = [
                [InlineKeyboardButton("🔄 Alterar Idade", callback_data="age_change")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def age_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para callbacks de verificação de idade"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    data = query.data
    
    if data == "age_confirm_18":
        # Usuário confirma ter 18+
        # Atualizar idade no banco
        user_db.update_user_profile(user_id, user_age="18+")
        
        # Mostrar menu de ativação do modo adulto
        keyboard = [
            [InlineKeyboardButton("🔞 Ativar Modo Adulto", callback_data="adult_activate")],
            [InlineKeyboardButton("🚫 Manter Modo Padrão", callback_data="adult_skip")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "✅ **Idade Verificada (18+)**\n\n"
            "🔞 **Modo Adulto Disponível**\n"
            "O modo adulto oferece interações mais íntimas e personalizadas.\n\n"
            "⚠️ **Aviso:** O conteúdo adulto pode incluir:\n"
            "• Conversas românticas intensas\n"
            "• Linguagem mais ousada\n"
            "• Temas para maiores de idade\n\n"
            "**Você gostaria de ativar o modo adulto?**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "age_confirm_under18":
        # Usuário confirma ser menor de idade
        user_db.update_user_profile(user_id, user_age="<18")
        
        await query.edit_message_text(
            "✅ **Idade Registrada**\n\n"
            "👶 Você foi registrado como menor de 18 anos.\n\n"
            "🎯 **Funcionalidades Disponíveis:**\n"
            "• Conversas amigáveis\n"
            "• Suporte emocional\n"
            "• Entretenimento adequado\n"
            "• Ajuda com estudos\n\n"
            "💡 Quando completar 18 anos, use /idade para atualizar e acessar mais funcionalidades!",
            parse_mode='Markdown'
        )
    
    elif data == "adult_activate":
        # Ativar modo adulto
        success = adult_system.activate_adult_mode(user_id)
        if success:
            keyboard = [
                [InlineKeyboardButton("⚙️ Configurar Intensidade", callback_data="adult_config_intensity")],
                [InlineKeyboardButton("💫 Escolher Estilo", callback_data="adult_config_style")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🔞 **Modo Adulto Ativado!**\n\n"
                "✨ Agora você tem acesso a:\n"
                "• Interações mais íntimas\n"
                "• Personalização avançada\n"
                "• Conteúdo para maiores de idade\n\n"
                "⚡ **Configuração Inicial:**\n"
                "• Intensidade: 1/5 (Suave)\n"
                "• Estilo: Romântico\n\n"
                "Você pode personalizar essas configurações:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "❌ **Erro ao Ativar**\n\n"
                "Não foi possível ativar o modo adulto. Verifique sua idade e tente novamente.",
                parse_mode='Markdown'
            )
    
    elif data == "adult_skip":
        await query.edit_message_text(
            "✅ **Modo Padrão Mantido**\n\n"
            "🎯 Você optou por manter o modo padrão.\n\n"
            "💡 **Lembre-se:** Você pode ativar o modo adulto a qualquer momento usando /adulto",
            parse_mode='Markdown'
        )
    
    elif data == "age_change":
        # Permitir mudança de idade
        keyboard = [
            [InlineKeyboardButton("✅ Confirmo ter 18+ anos", callback_data="age_confirm_18")],
            [InlineKeyboardButton("❌ Tenho menos de 18 anos", callback_data="age_confirm_under18")],
            [InlineKeyboardButton("🚫 Cancelar", callback_data="age_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🔄 **Alterar Idade**\n\n"
            "⚠️ **IMPORTANTE:** A alteração da idade é permanente e afeta suas funcionalidades.\n\n"
            "Confirme sua idade:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "age_cancel":
        await query.edit_message_text(
            "🚫 **Operação Cancelada**\n\n"
            "Nenhuma alteração foi feita em sua conta.",
            parse_mode='Markdown'
        )

async def adult_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para verificar status do modo adulto"""
    user_id = str(update.effective_user.id)
    user_status = adult_system.check_age(user_id)
    
    if not user_status['is_adult']:
        await update.message.reply_text(
            "🚫 **Acesso Negado**\n\n"
            "Esta funcionalidade é apenas para maiores de 18 anos.\n"
            "Use /idade para verificar sua idade.",
            parse_mode='Markdown'
        )
        return
    
    # Status detalhado para adultos
    status_emoji = "🔞" if user_status['adult_mode_active'] else "😴"
    adult_status = "**ATIVO**" if user_status['adult_mode_active'] else "**INATIVO**"
    
    message = f"{status_emoji} **Status do Modo Adulto**\n\n"
    message += f"🔞 Modo Adulto: {adult_status}\n"
    
    if user_status['adult_mode_active']:
        # Obter preferências detalhadas
        prefs = adult_system.get_adult_preferences(user_id)
        if prefs:
            intensity_desc = {
                1: "🟢 Suave (romântico leve)",
                2: "🟡 Moderado (romance intenso)",
                3: "🟠 Médio (sensual)",
                4: "🔴 Intenso (apaixonado)",
                5: "🟣 Máximo (muito íntimo)"
            }
            
            style_desc = {
                "romantic": "💕 Romântico",
                "playful": "😄 Brincalhão",
                "seductive": "😏 Sedutor",
                "intimate": "💖 Íntimo",
                "passionate": "🔥 Apaixonado"
            }
            
            message += f"⚡ Intensidade: {intensity_desc.get(prefs['intensity_level'], 'Desconhecido')}\n"
            message += f"💫 Estilo: {style_desc.get(prefs['interaction_style'], 'Desconhecido')}\n"
            
            if prefs['content_preferences']:
                message += f"🎯 Preferências: {', '.join(prefs['content_preferences'])}\n"
            
            if prefs['boundaries']:
                message += f"🚧 Limites: {', '.join(prefs['boundaries'])}\n"
        
        keyboard = [
            [InlineKeyboardButton("⚙️ Configurar", callback_data="adult_config_menu")],
            [InlineKeyboardButton("🔴 Desativar", callback_data="adult_deactivate")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        message += "\n💡 **Para ativar:**\n"
        message += "Use /adulto ou clique no botão abaixo"
        
        keyboard = [
            [InlineKeyboardButton("🔞 Ativar Modo Adulto", callback_data="adult_activate")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')