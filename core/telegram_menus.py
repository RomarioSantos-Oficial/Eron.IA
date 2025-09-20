"""
Sistema de menus interativos para Telegram
Simula navegação da versão web usando keyboards elaborados
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from core.telegram_formatter import TelegramFormatter

class TelegramMenus:
    """Sistema de menus interativos avançados"""
    
    @staticmethod
    def create_main_menu():
        """Menu principal - página inicial"""
        
        keyboard = [
            [
                InlineKeyboardButton("🎨 Personalizar", callback_data="menu_personalize"),
                InlineKeyboardButton("💬 Conversar", callback_data="menu_chat")
            ],
            [
                InlineKeyboardButton("⚙️ Preferências", callback_data="menu_preferences"),
                InlineKeyboardButton("😊 Emoções", callback_data="menu_emotions")
            ],
            [
                InlineKeyboardButton("📊 Estatísticas", callback_data="menu_stats"),
                InlineKeyboardButton("💾 Backup", callback_data="menu_backup")
            ],
            [
                InlineKeyboardButton("❓ Ajuda", callback_data="menu_help"),
                InlineKeyboardButton("ℹ️ Sobre", callback_data="menu_about")
            ]
        ]
        
        menu_text = TelegramFormatter.create_welcome_card()
        
        return menu_text, InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_personalization_menu():
        """Menu de personalização - equivalente à página de personalização web"""
        
        keyboard = [
            [
                InlineKeyboardButton("👤 Nome do Usuário", callback_data="pers_user_name"),
                InlineKeyboardButton("🤖 Nome do Bot", callback_data="pers_bot_name")
            ],
            [
                InlineKeyboardButton("⚧️ Gênero do Bot", callback_data="pers_bot_gender"),
                InlineKeyboardButton("🎭 Personalidade", callback_data="pers_personality")
            ],
            [
                InlineKeyboardButton("🗣️ Estilo de Linguagem", callback_data="pers_language"),
                InlineKeyboardButton("🎯 Tópicos Preferidos", callback_data="pers_topics")
            ],
            [
                InlineKeyboardButton("👶 Idade do Usuário", callback_data="pers_age"),
                InlineKeyboardButton("🎂 Data de Nascimento", callback_data="pers_birth")
            ],
            [
                InlineKeyboardButton("💾 Salvar Tudo", callback_data="pers_save_all"),
                InlineKeyboardButton("🔄 Reset Completo", callback_data="pers_reset")
            ],
            [
                InlineKeyboardButton("🔙 Menu Principal", callback_data="menu_main")
            ]
        ]
        
        menu_text = """
🎨 *Central de Personalização*

┌─ 🛠️ CONFIGURAÇÕES ───────┐
│ Configure todos os       │
│ aspectos do seu          │
│ assistente personalizado │
└───────────────────────────┘

Escolha uma opção abaixo para começar:
        """.strip()
        
        return menu_text, InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_advanced_preferences_menu():
        """Menu avançado de preferências - similar à interface web"""
        
        keyboard = [
            [
                InlineKeyboardButton("🎨 Estilo Visual", callback_data="adv_prefs_visual"),
                InlineKeyboardButton("💬 Estilo de Conversa", callback_data="adv_prefs_chat")
            ],
            [
                InlineKeyboardButton("📏 Comprimento das Respostas", callback_data="adv_prefs_length"),
                InlineKeyboardButton("😊 Uso de Emojis", callback_data="adv_prefs_emojis")
            ],
            [
                InlineKeyboardButton("🔊 Tom de Voz", callback_data="adv_prefs_tone"),
                InlineKeyboardButton("⚡ Velocidade", callback_data="adv_prefs_speed")
            ],
            [
                InlineKeyboardButton("🎯 Nível de Detalhes", callback_data="adv_prefs_detail"),
                InlineKeyboardButton("🧠 Complexidade", callback_data="adv_prefs_complexity")
            ],
            [
                InlineKeyboardButton("🌐 Idioma Principal", callback_data="adv_prefs_language"),
                InlineKeyboardButton("🕰️ Fuso Horário", callback_data="adv_prefs_timezone")
            ],
            [
                InlineKeyboardButton("💾 Salvar Preferências", callback_data="adv_prefs_save"),
                InlineKeyboardButton("🔄 Restaurar Padrões", callback_data="adv_prefs_reset")
            ],
            [
                InlineKeyboardButton("🔙 Voltar", callback_data="menu_main")
            ]
        ]
        
        menu_text = """
⚙️ *Preferências Avançadas*

┌─ 🎛️ CONTROLES DETALHADOS ┐
│ Configure cada aspecto   │
│ da sua experiência de    │
│ conversação com precisão │
└───────────────────────────┘

*Personalize tudo ao seu gosto:*
        """.strip()
        
        return menu_text, InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_emotions_dashboard():
        """Dashboard de emoções - equivalente à página web de emoções"""
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Estado Atual", callback_data="emotion_current"),
                InlineKeyboardButton("📈 Histórico", callback_data="emotion_history")
            ],
            [
                InlineKeyboardButton("🎭 Influenciar Bot", callback_data="emotion_influence"),
                InlineKeyboardButton("🧠 Análise Detalhada", callback_data="emotion_analysis")
            ],
            [
                InlineKeyboardButton("⚖️ Calibrar Sistema", callback_data="emotion_calibrate"),
                InlineKeyboardButton("📝 Relatório", callback_data="emotion_report")
            ],
            [
                InlineKeyboardButton("🔄 Atualizar", callback_data="emotion_refresh"),
                InlineKeyboardButton("💾 Salvar Estado", callback_data="emotion_save")
            ],
            [
                InlineKeyboardButton("🔙 Menu Principal", callback_data="menu_main")
            ]
        ]
        
        menu_text = """
😊 *Dashboard de Emoções*

┌─ 🎭 SISTEMA EMOCIONAL ───┐
│ Monitore e influencie    │
│ as emoções do bot para   │
│ uma experiência única    │
└───────────────────────────┘

*Recursos disponíveis:*
        """.strip()
        
        return menu_text, InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_chat_interface():
        """Interface de chat - simula a experiência web"""
        
        keyboard = [
            [
                InlineKeyboardButton("💬 Iniciar Conversa", callback_data="chat_start"),
                InlineKeyboardButton("📜 Ver Histórico", callback_data="chat_history")
            ],
            [
                InlineKeyboardButton("🎨 Mudar Tema", callback_data="chat_theme"),
                InlineKeyboardButton("⚙️ Config. do Chat", callback_data="chat_config")
            ],
            [
                InlineKeyboardButton("💾 Salvar Conversa", callback_data="chat_save"),
                InlineKeyboardButton("🗑️ Limpar Histórico", callback_data="chat_clear")
            ],
            [
                InlineKeyboardButton("🔙 Menu Principal", callback_data="menu_main")
            ]
        ]
        
        menu_text = """
💬 *Interface de Chat*

┌─ 🗨️ CENTRO DE CONVERSAS ─┐
│ Sua central para todas   │
│ as conversas e interações│
│ com o assistente         │
└───────────────────────────┘

*O que você gostaria de fazer?*
        """.strip()
        
        return menu_text, InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_statistics_panel():
        """Painel de estatísticas detalhadas"""
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Uso Geral", callback_data="stats_general"),
                InlineKeyboardButton("💬 Conversas", callback_data="stats_conversations")
            ],
            [
                InlineKeyboardButton("🎨 Personalizações", callback_data="stats_personalizations"),
                InlineKeyboardButton("😊 Emoções", callback_data="stats_emotions")
            ],
            [
                InlineKeyboardButton("⚙️ Preferências", callback_data="stats_preferences"),
                InlineKeyboardButton("🕰️ Tempo de Uso", callback_data="stats_time")
            ],
            [
                InlineKeyboardButton("📈 Gráficos", callback_data="stats_charts"),
                InlineKeyboardButton("📋 Relatório", callback_data="stats_report")
            ],
            [
                InlineKeyboardButton("📤 Exportar Dados", callback_data="stats_export"),
                InlineKeyboardButton("🔙 Voltar", callback_data="menu_main")
            ]
        ]
        
        menu_text = """
📊 *Painel de Estatísticas*

┌─ 📈 ANÁLISE DE USO ──────┐
│ Visualize padrões de     │
│ uso, estatísticas        │
│ detalhadas e insights    │
└───────────────────────────┘

*Escolha o tipo de análise:*
        """.strip()
        
        return menu_text, InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_backup_center():
        """Centro de backup e restauração"""
        
        keyboard = [
            [
                InlineKeyboardButton("💾 Criar Backup", callback_data="backup_create"),
                InlineKeyboardButton("📥 Restaurar", callback_data="backup_restore")
            ],
            [
                InlineKeyboardButton("📋 Listar Backups", callback_data="backup_list"),
                InlineKeyboardButton("🗑️ Deletar Backup", callback_data="backup_delete")
            ],
            [
                InlineKeyboardButton("⚙️ Config. Auto", callback_data="backup_auto_config"),
                InlineKeyboardButton("📤 Exportar", callback_data="backup_export")
            ],
            [
                InlineKeyboardButton("📥 Importar", callback_data="backup_import"),
                InlineKeyboardButton("🔄 Sincronizar", callback_data="backup_sync")
            ],
            [
                InlineKeyboardButton("🔙 Menu Principal", callback_data="menu_main")
            ]
        ]
        
        menu_text = """
💾 *Centro de Backup*

┌─ 🛡️ PROTEÇÃO DE DADOS ──┐
│ Mantenha suas            │
│ configurações e dados    │
│ sempre seguros           │
└───────────────────────────┘

*Opções de backup disponíveis:*
        """.strip()
        
        return menu_text, InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_help_center():
        """Central de ajuda completa"""
        
        keyboard = [
            [
                InlineKeyboardButton("📚 Guia Rápido", callback_data="help_quick"),
                InlineKeyboardButton("📖 Manual Completo", callback_data="help_manual")
            ],
            [
                InlineKeyboardButton("❓ FAQ", callback_data="help_faq"),
                InlineKeyboardButton("🛠️ Solução de Problemas", callback_data="help_troubleshoot")
            ],
            [
                InlineKeyboardButton("🎬 Tutoriais", callback_data="help_tutorials"),
                InlineKeyboardButton("💡 Dicas", callback_data="help_tips")
            ],
            [
                InlineKeyboardButton("🎮 Comandos", callback_data="help_commands"),
                InlineKeyboardButton("⌨️ Atalhos", callback_data="help_shortcuts")
            ],
            [
                InlineKeyboardButton("📞 Contato", callback_data="help_contact"),
                InlineKeyboardButton("🔙 Voltar", callback_data="menu_main")
            ]
        ]
        
        menu_text = TelegramFormatter.create_help_menu()
        
        return menu_text, InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_breadcrumb_navigation(current_menu, history=[]):
        """Cria navegação estilo breadcrumb"""
        
        breadcrumb_map = {
            'main': '🏠 Início',
            'personalize': '🎨 Personalizar',
            'preferences': '⚙️ Preferências', 
            'emotions': '😊 Emoções',
            'chat': '💬 Chat',
            'stats': '📊 Estatísticas',
            'backup': '💾 Backup',
            'help': '❓ Ajuda'
        }
        
        breadcrumb = " > ".join([breadcrumb_map.get(menu, menu) for menu in history + [current_menu]])
        
        return f"📍 *Navegação:* {breadcrumb}\n\n"
    
    @staticmethod
    def get_menu_by_callback(callback_data):
        """Retorna o menu apropriado baseado no callback"""
        
        menu_mapping = {
            'menu_main': TelegramMenus.create_main_menu,
            'menu_personalize': TelegramMenus.create_personalization_menu,
            'menu_preferences': TelegramMenus.create_advanced_preferences_menu,
            'menu_emotions': TelegramMenus.create_emotions_dashboard,
            'menu_chat': TelegramMenus.create_chat_interface,
            'menu_stats': TelegramMenus.create_statistics_panel,
            'menu_backup': TelegramMenus.create_backup_center,
            'menu_help': TelegramMenus.create_help_center,
        }
        
        return menu_mapping.get(callback_data, TelegramMenus.create_main_menu)

# Classe para gerenciar navegação entre menus
class MenuNavigator:
    """Gerenciador de navegação entre menus"""
    
    def __init__(self):
        self.menu_history = {}
    
    def add_to_history(self, user_id, menu_name):
        """Adiciona menu ao histórico de navegação"""
        if user_id not in self.menu_history:
            self.menu_history[user_id] = []
        
        # Evitar duplicatas consecutivas
        if not self.menu_history[user_id] or self.menu_history[user_id][-1] != menu_name:
            self.menu_history[user_id].append(menu_name)
        
        # Limitar histórico a 10 itens
        if len(self.menu_history[user_id]) > 10:
            self.menu_history[user_id] = self.menu_history[user_id][-10:]
    
    def get_history(self, user_id):
        """Retorna histórico de navegação do usuário"""
        return self.menu_history.get(user_id, [])
    
    def get_previous_menu(self, user_id):
        """Retorna o menu anterior"""
        history = self.get_history(user_id)
        return history[-2] if len(history) > 1 else 'main'
    
    def clear_history(self, user_id):
        """Limpa histórico de navegação"""
        self.menu_history[user_id] = []

# Instância global do navegador
menu_navigator = MenuNavigator()
