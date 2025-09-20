"""
Sistema de formatação rica para Telegram
Melhora a apresentação das mensagens usando recursos avançados do Telegram
"""

from telegram.constants import ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import html
import re

class TelegramFormatter:
    """Classe para formatação avançada de mensagens no Telegram"""
    
    @staticmethod
    def format_message(text, style='markdown'):
        """
        Formata texto para apresentação rica no Telegram
        
        Args:
            text: Texto a ser formatado
            style: Estilo de formatação ('markdown', 'html')
        """
        if style == 'html':
            # Formatação HTML
            text = text.replace('**', '<b>').replace('**', '</b>')
            text = text.replace('*', '<i>').replace('*', '</i>')
            text = text.replace('`', '<code>').replace('`', '</code>')
            text = text.replace('```', '<pre>').replace('```', '</pre>')
            return text
        else:
            # Formatação Markdown (padrão)
            return text
    
    @staticmethod
    def create_status_message(bot_name, user_name, personality, language):
        """Cria mensagem de status formatada"""
        
        status_message = f"""
🤖 *Status do Sistema*

┌─────────────────────┐
│ 👤 *Usuário:* `{user_name}`
│ 🎭 *Assistente:* `{bot_name}`
│ 🎨 *Personalidade:* `{personality}`
│ 🗣️ *Linguagem:* `{language}`
└─────────────────────┘

✅ Sistema operacional e personalizado!
        """
        return status_message.strip()
    
    @staticmethod
    def create_personalization_summary(profile):
        """Cria resumo da personalização em formato visual"""
        
        summary = f"""
🎨 *Resumo da Personalização*

╔═══════════════════════════╗
║ 📋 *PERFIL CONFIGURADO*   ║
╠═══════════════════════════╣
║ 👤 Nome: `{profile.get('user_name', 'N/A')}`
║ 🤖 Assistente: `{profile.get('bot_name', 'N/A')}`
║ ⚧️ Gênero: `{profile.get('bot_gender', 'N/A')}`
║ 🎭 Personalidade: `{profile.get('bot_personality', 'N/A')}`
║ 🗣️ Linguagem: `{profile.get('bot_language', 'N/A')}`
║ 🎯 Tópicos: `{profile.get('preferred_topics', 'N/A')}`
╚═══════════════════════════╝

✨ Tudo configurado! Vamos conversar?
        """
        return summary.strip()
    
    @staticmethod
    def create_welcome_card(user_name=None):
        """Cria cartão de boas-vindas estilizado"""
        
        name_part = f" {user_name}" if user_name else ""
        
        welcome = f"""
🚀 *Bem-vindo ao Eron.IA{name_part}!*

┌─ ⭐ RECURSOS DISPONÍVEIS ─┐
│                           │
│ 🎨 Personalização total   │
│ 💬 Conversas inteligentes │
│ 😊 Sistema de emoções     │
│ ⚙️ Preferências detalhadas│
│ 🔄 Reset quando precisar  │
│                           │
└───────────────────────────┘

Digite qualquer coisa para começar!
        """
        return welcome.strip()
    
    @staticmethod
    def create_help_menu():
        """Cria menu de ajuda formatado"""
        
        help_text = f"""
📚 *Central de Ajuda - Eron.IA*

┌─ 🎮 COMANDOS PRINCIPAIS ─┐
│ /start - Iniciar sistema  │
│ /personalize - Configurar │
│ /clear - Resetar tudo     │
│ /preferences - Preferências│
│ /emotions - Ver emoções   │
│ /status - Status atual    │
│ /help - Esta mensagem     │
└───────────────────────────┘

┌─ 💡 DICAS ÚTEIS ──────────┐
│ • Digite normalmente      │
│ • Mude preferências sempre│
│ • Use /clear para resetar │
│ • Personalize à vontade   │
└───────────────────────────┘

❓ *Dúvidas?* Apenas pergunte!
        """
        return help_text.strip()
    
    @staticmethod
    def create_preferences_menu(preferences=None):
        """Cria menu de preferências visual"""
        
        if not preferences:
            preferences = {
                'message_style': 'casual',
                'response_length': 'medium', 
                'include_emojis': True
            }
            
        style_emoji = {'casual': '😊', 'formal': '🎩', 'friendly': '🤗'}.get(preferences.get('message_style'), '😊')
        length_emoji = {'short': '📏', 'medium': '📐', 'long': '📊'}.get(preferences.get('response_length'), '📐')
        emoji_status = '✅' if preferences.get('include_emojis') else '❌'
        
        prefs_menu = f"""
⚙️ *Preferências Atuais*

┌─ 🎨 ESTILO DE CONVERSA ─┐
│ {style_emoji} Estilo: `{preferences.get('message_style', 'casual')}`
│ {length_emoji} Tamanho: `{preferences.get('response_length', 'medium')}`
│ {emoji_status} Emojis: `{'Sim' if preferences.get('include_emojis') else 'Não'}`
└─────────────────────────┘

Para alterar, use os botões abaixo:
        """
        return prefs_menu.strip()
    
    @staticmethod
    def create_emotion_display(user_emotion=None, bot_emotion=None):
        """Cria display visual de emoções"""
        
        user_emoji = {
            'feliz': '😊', 'triste': '😢', 'raiva': '😠',
            'surpresa': '😮', 'medo': '😨', 'neutro': '😐'
        }.get(user_emotion, '😐')
        
        bot_emoji = {
            'empático': '🤗', 'entusiasmado': '🤩', 'calmo': '😌',
            'curioso': '🤔', 'prestativo': '😊', 'neutro': '🤖'
        }.get(bot_emotion, '🤖')
        
        emotion_display = f"""
💭 *Estado Emocional*

┌─ 👤 USUÁRIO ──────────────┐
│ {user_emoji} Emoção: `{user_emotion or 'neutro'}`
└───────────────────────────┘

┌─ 🤖 ASSISTENTE ───────────┐
│ {bot_emoji} Estado: `{bot_emotion or 'neutro'}`
└───────────────────────────┘

🎭 As emoções influenciam minhas respostas!
        """
        return emotion_display.strip()
    
    @staticmethod
    def create_keyboard_menu(buttons_config):
        """
        Cria teclado inline personalizado
        
        Args:
            buttons_config: Lista de botões no formato:
            [
                [{'text': 'Botão 1', 'callback': 'callback_1'}],
                [{'text': 'Botão 2', 'callback': 'callback_2'}]
            ]
        """
        keyboard = []
        
        for row in buttons_config:
            button_row = []
            for button in row:
                button_row.append(
                    InlineKeyboardButton(
                        text=button['text'],
                        callback_data=button['callback']
                    )
                )
            keyboard.append(button_row)
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_progress_bar(current, total, width=20):
        """Cria barra de progresso visual"""
        
        progress = int((current / total) * width)
        bar = '█' * progress + '░' * (width - progress)
        percentage = int((current / total) * 100)
        
        return f"`{bar}` {percentage}% ({current}/{total})"
    
    @staticmethod
    def escape_markdown(text):
        """Escapa caracteres especiais do Markdown"""
        
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    @staticmethod
    def wrap_code_block(code, language=''):
        """Envolve código em bloco formatado"""
        
        return f"```{language}\n{code}\n```"
    
    @staticmethod
    def create_divider(char='─', length=25):
        """Cria divisor visual"""
        
        return char * length

# Atalhos para uso comum
def format_bold(text):
    """Texto em negrito"""
    return f"*{text}*"

def format_italic(text):
    """Texto em itálico"""
    return f"_{text}_"

def format_code(text):
    """Texto como código"""
    return f"`{text}`"

def format_link(text, url):
    """Cria link formatado"""
    return f"[{text}]({url})"
