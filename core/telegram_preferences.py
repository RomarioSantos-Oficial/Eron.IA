"""
Sistema de preferências unificado para Telegram
Permite configuração detalhada similar à versão web
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from core.telegram_formatter import TelegramFormatter, format_bold
from core.unified_messages import UnifiedMessages

class TelegramPreferences:
    """Gerenciador de preferências para o Telegram"""
    
    @staticmethod
    def create_main_preferences_menu():
        """Cria menu principal de preferências"""
        
        keyboard = [
            [
                InlineKeyboardButton("🎨 Estilo de Conversa", callback_data="prefs_style"),
                InlineKeyboardButton("📏 Tamanho das Respostas", callback_data="prefs_length")
            ],
            [
                InlineKeyboardButton("😊 Usar Emojis", callback_data="prefs_emojis"),
                InlineKeyboardButton("🎭 Personalidade", callback_data="prefs_personality")
            ],
            [
                InlineKeyboardButton("🎯 Tópicos Preferidos", callback_data="prefs_topics"),
                InlineKeyboardButton("🗣️ Linguagem", callback_data="prefs_language")
            ],
            [
                InlineKeyboardButton("💾 Salvar Configurações", callback_data="prefs_save"),
                InlineKeyboardButton("🔙 Voltar", callback_data="prefs_back")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_style_menu(current_style='casual'):
        """Menu para escolha de estilo de conversa"""
        
        styles = [
            ('casual', '😊 Casual', 'Conversa descontraída e amigável'),
            ('formal', '🎩 Formal', 'Linguagem mais profissional'),
            ('friendly', '🤗 Amigável', 'Muito acolhedor e carinhoso')
        ]
        
        keyboard = []
        for style_id, style_name, description in styles:
            marker = "✅ " if style_id == current_style else ""
            keyboard.append([
                InlineKeyboardButton(
                    f"{marker}{style_name}",
                    callback_data=f"set_style_{style_id}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Voltar", callback_data="prefs_main")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_length_menu(current_length='medium'):
        """Menu para escolha do tamanho das respostas"""
        
        lengths = [
            ('short', '📏 Curtas', 'Respostas concisas e diretas'),
            ('medium', '📐 Médias', 'Nível moderado de detalhes'),
            ('long', '📊 Longas', 'Respostas detalhadas e abrangentes')
        ]
        
        keyboard = []
        for length_id, length_name, description in lengths:
            marker = "✅ " if length_id == current_length else ""
            keyboard.append([
                InlineKeyboardButton(
                    f"{marker}{length_name}",
                    callback_data=f"set_length_{length_id}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Voltar", callback_data="prefs_main")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_emojis_menu(current_emojis=True):
        """Menu para configuração de emojis"""
        
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{'✅' if current_emojis else '⬜'} 😊 Usar Emojis",
                    callback_data="toggle_emojis"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'⬜' if current_emojis else '✅'} 📝 Sem Emojis",
                    callback_data="toggle_emojis"
                )
            ],
            [
                InlineKeyboardButton("🔙 Voltar", callback_data="prefs_main")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_personality_menu(current_personality='amigável'):
        """Menu para escolha de personalidade"""
        
        personalities = [
            ('amigável', '🤗 Amigável', 'Caloroso e acolhedor'),
            ('profissional', '💼 Profissional', 'Formal e objetivo'),
            ('casual', '😊 Casual', 'Descontraído e relaxado'),
            ('entusiasta', '🤩 Entusiasta', 'Energético e animado'),
            ('sábio', '🧠 Sábio', 'Reflexivo e ponderado'),
            ('humorado', '😄 Humorado', 'Divertido e bem-humorado')
        ]
        
        keyboard = []
        for pers_id, pers_name, description in personalities:
            marker = "✅ " if pers_id == current_personality else ""
            keyboard.append([
                InlineKeyboardButton(
                    f"{marker}{pers_name}",
                    callback_data=f"set_personality_{pers_id}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Voltar", callback_data="prefs_main")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_language_menu(current_language='informal'):
        """Menu para escolha de linguagem"""
        
        languages = [
            ('informal', '😊 Informal', 'Linguagem descontraída'),
            ('formal', '🎩 Formal', 'Linguagem rebuscada'),
            ('técnico', '🔧 Técnico', 'Termos mais específicos'),
            ('simples', '🌱 Simples', 'Linguagem acessível')
        ]
        
        keyboard = []
        for lang_id, lang_name, description in languages:
            marker = "✅ " if lang_id == current_language else ""
            keyboard.append([
                InlineKeyboardButton(
                    f"{marker}{lang_name}",
                    callback_data=f"set_language_{lang_id}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Voltar", callback_data="prefs_main")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_topics_keyboard():
        """Teclado para configuração de tópicos preferidos"""
        
        topics = [
            ('tecnologia', '💻 Tecnologia'),
            ('ciência', '🔬 Ciência'),
            ('arte', '🎨 Arte'),
            ('música', '🎵 Música'),
            ('esportes', '⚽ Esportes'),
            ('cinema', '🎬 Cinema'),
            ('literatura', '📚 Literatura'),
            ('filosofia', '🤔 Filosofia'),
            ('história', '📜 História'),
            ('culinária', '🍳 Culinária'),
            ('viagens', '✈️ Viagens'),
            ('games', '🎮 Games')
        ]
        
        # Criar teclado com 2 tópicos por linha
        keyboard = []
        for i in range(0, len(topics), 2):
            row = []
            for j in range(2):
                if i + j < len(topics):
                    topic_id, topic_name = topics[i + j]
                    row.append(
                        InlineKeyboardButton(
                            topic_name,
                            callback_data=f"toggle_topic_{topic_id}"
                        )
                    )
            keyboard.append(row)
        
        keyboard.extend([
            [InlineKeyboardButton("✅ Confirmar Seleção", callback_data="topics_confirm")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="prefs_main")]
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_preferences_summary(preferences):
        """Cria resumo das preferências atuais"""
        
        chat_prefs = preferences.get('chat', {})
        
        style_emoji = {'casual': '😊', 'formal': '🎩', 'friendly': '🤗'}.get(
            chat_prefs.get('message_style', 'casual'), '😊'
        )
        
        length_emoji = {'short': '📏', 'medium': '📐', 'long': '📊'}.get(
            chat_prefs.get('response_length', 'medium'), '📐'
        )
        
        emoji_status = '✅' if chat_prefs.get('include_emojis', True) else '❌'
        
        summary = f"""
⚙️ *Configurações Atuais*

┌─ 🎨 ESTILO DE CONVERSA ─┐
│ {style_emoji} Estilo: `{chat_prefs.get('message_style', 'casual')}`
│ {length_emoji} Tamanho: `{chat_prefs.get('response_length', 'medium')}`
│ {emoji_status} Emojis: `{'Habilitados' if chat_prefs.get('include_emojis', True) else 'Desabilitados'}`
└─────────────────────────┘

┌─ 🎭 PERSONALIDADE ──────┐
│ 🤗 Tipo: `{preferences.get('personality', 'amigável')}`
│ 🗣️ Linguagem: `{preferences.get('language', 'informal')}`
└─────────────────────────┘

Para modificar, use os botões abaixo:
        """.strip()
        
        return summary
    
    @staticmethod
    def get_confirmation_message():
        """Mensagem de confirmação ao salvar preferências"""
        
        return """
💾 *Preferências Salvas!*

Suas configurações foram atualizadas com sucesso. 

✅ As mudanças já estão ativas!

Continue conversando normalmente e note a diferença no meu comportamento.
        """.strip()
    
    @staticmethod
    def create_quick_settings_keyboard():
        """Teclado de configurações rápidas"""
        
        keyboard = [
            [
                InlineKeyboardButton("😊 Casual", callback_data="quick_casual"),
                InlineKeyboardButton("🎩 Formal", callback_data="quick_formal")
            ],
            [
                InlineKeyboardButton("📏 Respostas Curtas", callback_data="quick_short"),
                InlineKeyboardButton("📊 Respostas Longas", callback_data="quick_long")
            ],
            [
                InlineKeyboardButton("😊 Mais Emojis", callback_data="quick_emojis_on"),
                InlineKeyboardButton("📝 Sem Emojis", callback_data="quick_emojis_off")
            ],
            [
                InlineKeyboardButton("⚙️ Configurações Avançadas", callback_data="prefs_main")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

# Funções auxiliares para uso nos handlers
def apply_preferences_to_response(response, preferences):
    """Aplica preferências à resposta do bot"""
    
    if not preferences:
        return response
    
    chat_prefs = preferences.get('chat', {})
    
    # Adicionar ou remover emojis
    if not chat_prefs.get('include_emojis', True):
        # Remover emojis da resposta
        import re
        response = re.sub(r'[^\w\s\.,!?;:()[\]{}"\'`~@#$%^&*+=|\\<>/\-]', '', response)
    
    # Ajustar comprimento da resposta
    length = chat_prefs.get('response_length', 'medium')
    if length == 'short' and len(response) > 200:
        # Truncar resposta longa
        sentences = response.split('.')
        if len(sentences) > 2:
            response = '. '.join(sentences[:2]) + '.'
    
    return response
