"""
Comandos de descoberta e ajuda do Sistema Adulto Avançado
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from .adult_integration import (
    get_adult_personality_context,
    get_adult_system_status_summary,
    is_advanced_adult_active
)

logger = logging.getLogger(__name__)

async def help_adult_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help_adult - Mostrar todos os comandos adultos disponíveis"""
    user_id = str(update.effective_user.id)
    
    # Verificar status atual
    adult_context = get_adult_personality_context(user_id)
    status = get_adult_system_status_summary(user_id)
    
    text = f"""
🔞 **SISTEMA ADULTO ERON.IA**

📊 **Status Atual**: {status}

🚀 **COMANDOS DISPONÍVEIS**:

**🔓 Ativação:**
• `/adult_mode` - Ativar modo adulto (18+)

**⚙️ Sistema Avançado:**
• `/adult_config` - Configurar personalidade avançada
• `/adult_status` - Ver status e estatísticas detalhadas  
• `/adult_mood` - Definir humor atual

**📋 Sistema Básico:**
• `/devassa_config` - Configurações básicas
• `/devassa_status` - Status do sistema básico
• `/devassa_off` - Desativar modo adulto

**🎭 6 PERSONALIDADES DISPONÍVEIS:**
💫 **Sedutora** - Misteriosa e envolvente
🔥 **Dominante** - Intensa e controladora  
😈 **Travessa** - Provocativa e brincalhona
😊 **Carinhosa** - Doce e afetuosa
🎨 **Criativa** - Imaginativa e única
🌟 **Equilibrada** - Versátil e adaptável

**🌡️ SISTEMA DE HUMORES:**
Defina o humor para cada conversa: apaixonada, travessa, dominante, carinhosa, misteriosa, brincalhona, sensual, romântica.

**📊 RECURSOS AVANÇADOS:**
• Configurações detalhadas por personalidade
• Sistema de feedback de sessões  
• Histórico de conversas e preferências
• Ajustes finos de comportamento
• Estatísticas de uso

💡 **Dica**: Comece com `/adult_config` para descobrir todas as possibilidades!
"""
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def adult_upgrade_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /adult_upgrade - Incentivo para upgrade ao sistema avançado"""
    user_id = str(update.effective_user.id)
    
    if is_advanced_adult_active(user_id):
        await update.message.reply_text(
            "✅ **Você já tem o sistema avançado!**\n\n"
            "Use /adult_status para ver detalhes ou /adult_config para ajustar.",
            parse_mode='Markdown'
        )
        return
    
    # Verificar se tem modo básico
    adult_context = get_adult_personality_context(user_id)
    
    if not adult_context.get('adult_mode'):
        await update.message.reply_text(
            "❌ **Modo adulto não está ativo**\n\n"
            "Use /adult_mode para ativar primeiro.",
            parse_mode='Markdown'
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("🚀 Fazer Upgrade Agora!", callback_data="start_adult_upgrade")],
        [InlineKeyboardButton("📋 Ver Diferenças", callback_data="show_system_comparison")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🆙 **UPGRADE PARA SISTEMA AVANÇADO**

🎯 **Você tem o sistema BÁSICO**
Que tal experimentar o **SISTEMA AVANÇADO**?

🔥 **O QUE VOCÊ GANHA:**

🎭 **6 Personalidades Únicas**
• Cada uma com características específicas
• Comportamentos e respostas personalizadas

🌡️ **Sistema de Humores**
• 8 humores diferentes
• Muda o tom das conversas

📊 **Configurações Detalhadas**
• Controle fino de cada aspecto
• Ajustes de confiança, brincadeira, dominância

📈 **Estatísticas e Feedback**
• Histórico de suas sessões
• Melhoria contínua baseada no seu uso

🎨 **Experiência Personalizada**
• Responses formatadas com base na personalidade
• Indicadores visuais únicos

✨ **É GRATUITO e takes 2 minutos!**
"""
    
    await update.message.reply_text(
        text, reply_markup=reply_markup, parse_mode='Markdown'
    )

async def adult_demo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /adult_demo - Demonstração das personalidades"""
    demo_text = """
🎭 **DEMO DAS PERSONALIDADES**

Veja como cada uma responderia à pergunta: *"Como você está hoje?"*

💫 **SEDUTORA**: 
"Estou bem... mas seria melhor se você estivesse aqui comigo. 😉"

🔥 **DOMINANTE**: 
"Estou poderosa e no controle, como sempre. E você, pronto para me obedecer?"

😈 **TRAVESSA**: 
"Estou com muitas ideias maliciosas na cabeça... quer descobrir quais? 😈"

😊 **CARINHOSA**: 
"Estou bem, amor! Fico ainda melhor quando você fala comigo. 💕"

🎨 **CRIATIVA**: 
"Estou imaginando mil cenários diferentes... alguns bem interessantes envolvendo nós dois."

🌟 **EQUILIBRADA**: 
"Estou em harmonia, pronta para qualquer aventura que você quiser viver comigo."

🤯 **IMPRESSIONANTE, NÃO?**

Cada personalidade tem centenas de variações e se adapta ao seu humor escolhido!

Use `/adult_config` para começar! 🚀
"""
    
    await update.message.reply_text(demo_text, parse_mode='Markdown')

# Comandos para registrar
discovery_commands = [
    CommandHandler('help_adult', help_adult_command),
    CommandHandler('adult_upgrade', adult_upgrade_command), 
    CommandHandler('adult_demo', adult_demo_command)
]