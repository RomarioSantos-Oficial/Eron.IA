import sqlite3
import json
import os
from datetime import datetime

class PreferencesManager:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'memoria', 'preferences.db')
            
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
        
    def create_tables(self):
        with self.conn:
            # Tabela principal de preferências
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    chat_preferences TEXT,
                    visual_preferences TEXT,
                    notification_preferences TEXT,
                    privacy_preferences TEXT,
                    language_preferences TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
    def get_default_preferences(self):
        """Retorna as preferências padrão para um novo usuário"""
        return {
            'chat': {
                'message_style': 'casual',  # casual, formal, empático
                'response_length': 'medium',  # short, medium, long
                'include_emojis': True,
                'show_typing_indicator': True,
                'auto_scroll': True,
                'message_grouping': True,
                'timestamp_format': '24h',  # 12h, 24h
                'message_font_size': 'medium'  # small, medium, large
            },
            'visual': {
                'theme': 'light',  # light, dark, system
                'color_scheme': 'blue',  # blue, green, purple, custom
                'custom_colors': None,
                'font_family': 'Segoe UI',
                'bot_avatar_style': 'default',
                'user_avatar_style': 'initials',
                'layout_density': 'comfortable',  # compact, comfortable, spacious
                'animation_level': 'medium'  # none, minimal, medium, full
            },
            'notifications': {
                'enable_notifications': True,
                'sound_enabled': True,
                'notification_position': 'top-right',
                'show_previews': True,
                'quiet_hours': {
                    'enabled': False,
                    'start': '22:00',
                    'end': '07:00'
                }
            },
            'privacy': {
                'save_chat_history': True,
                'history_retention_days': 30,
                'share_usage_data': False,
                'personalization_level': 'balanced',  # minimal, balanced, full
                'data_export_format': 'json',  # json, csv, txt
                'auto_delete_inactive': False
            },
            'language': {
                'interface_language': 'pt-BR',
                'content_language': 'pt-BR',
                'date_format': 'dd/MM/yyyy',
                'time_format': '24h',
                'first_day_of_week': 'sunday',
                'number_format': 'BR'
            }
        }
        
    def get_preferences(self, user_id):
        """Obtém as preferências do usuário, usando padrões onde não definidas"""
        cur = self.conn.cursor()
        cur.execute(
            'SELECT chat_preferences, visual_preferences, notification_preferences, '
            'privacy_preferences, language_preferences FROM user_preferences WHERE user_id = ?',
            (user_id,)
        )
        row = cur.fetchone()
        
        defaults = self.get_default_preferences()
        
        if not row:
            return defaults
            
        # Converter strings JSON para dicionários
        try:
            preferences = {
                'chat': json.loads(row[0]) if row[0] else defaults['chat'],
                'visual': json.loads(row[1]) if row[1] else defaults['visual'],
                'notifications': json.loads(row[2]) if row[2] else defaults['notifications'],
                'privacy': json.loads(row[3]) if row[3] else defaults['privacy'],
                'language': json.loads(row[4]) if row[4] else defaults['language']
            }
            
            # Mesclar com padrões para garantir que todas as chaves existam
            for category in defaults:
                if category not in preferences:
                    preferences[category] = {}
                for key, value in defaults[category].items():
                    if key not in preferences[category]:
                        preferences[category][key] = value
                        
            return preferences
            
        except json.JSONDecodeError:
            return defaults
            
    def update_preferences(self, user_id, preferences, category=None):
        """
        Atualiza as preferências do usuário.
        Se category for especificada, atualiza apenas aquela categoria.
        """
        cur = self.conn.cursor()
        cur.execute('SELECT 1 FROM user_preferences WHERE user_id = ?', (user_id,))
        exists = cur.fetchone() is not None
        
        if category:
            # Atualizar apenas uma categoria
            if exists:
                column = f'{category}_preferences'
                with self.conn:
                    self.conn.execute(f'''
                        UPDATE user_preferences 
                        SET {column} = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', (json.dumps(preferences), user_id))
            else:
                defaults = self.get_default_preferences()
                prefs = defaults.copy()
                prefs[category] = preferences
                
                columns = ['chat', 'visual', 'notification', 'privacy', 'language']
                values = [json.dumps(prefs.get(c, defaults[c])) for c in columns]
                
                with self.conn:
                    self.conn.execute('''
                        INSERT INTO user_preferences (
                            user_id, chat_preferences, visual_preferences,
                            notification_preferences, privacy_preferences,
                            language_preferences
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', [user_id] + values)
        else:
            # Atualizar todas as categorias
            if exists:
                with self.conn:
                    self.conn.execute('''
                        UPDATE user_preferences SET
                            chat_preferences = ?,
                            visual_preferences = ?,
                            notification_preferences = ?,
                            privacy_preferences = ?,
                            language_preferences = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', (
                        json.dumps(preferences.get('chat')),
                        json.dumps(preferences.get('visual')),
                        json.dumps(preferences.get('notifications')),
                        json.dumps(preferences.get('privacy')),
                        json.dumps(preferences.get('language')),
                        user_id
                    ))
            else:
                with self.conn:
                    self.conn.execute('''
                        INSERT INTO user_preferences (
                            user_id, chat_preferences, visual_preferences,
                            notification_preferences, privacy_preferences,
                            language_preferences
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        user_id,
                        json.dumps(preferences.get('chat')),
                        json.dumps(preferences.get('visual')),
                        json.dumps(preferences.get('notifications')),
                        json.dumps(preferences.get('privacy')),
                        json.dumps(preferences.get('language'))
                    ))
                    
    def get_theme_colors(self, theme_name):
        """Retorna as cores para um tema específico"""
        themes = {
            'light': {
                'background': '#ffffff',
                'text': '#000000',
                'primary': '#1a73e8',
                'secondary': '#5f6368',
                'accent': '#25d366',
                'error': '#d93025',
                'success': '#188038',
                'warning': '#f4b400',
                'surface': '#f8f9fa',
                'border': '#dadce0'
            },
            'dark': {
                'background': '#202124',
                'text': '#ffffff',
                'primary': '#8ab4f8',
                'secondary': '#9aa0a6',
                'accent': '#25d366',
                'error': '#f28b82',
                'success': '#81c995',
                'warning': '#fdd663',
                'surface': '#303134',
                'border': '#5f6368'
            }
        }
        return themes.get(theme_name, themes['light'])
        
    def apply_visual_preferences(self, prefs):
        """Gera CSS baseado nas preferências visuais"""
        theme = prefs['visual']['theme']
        colors = self.get_theme_colors(theme)
        
        css = f"""
        :root {{
            --background: {colors['background']};
            --text: {colors['text']};
            --primary: {colors['primary']};
            --secondary: {colors['secondary']};
            --accent: {colors['accent']};
            --error: {colors['error']};
            --success: {colors['success']};
            --warning: {colors['warning']};
            --surface: {colors['surface']};
            --border: {colors['border']};
            
            --font-family: {prefs['visual']['font_family']};
            --font-size-base: {
                '14px' if prefs['visual']['layout_density'] == 'compact'
                else '16px' if prefs['visual']['layout_density'] == 'comfortable'
                else '18px'
            };
            
            --spacing-unit: {
                '0.5rem' if prefs['visual']['layout_density'] == 'compact'
                else '1rem' if prefs['visual']['layout_density'] == 'comfortable'
                else '1.5rem'
            };
            
            --animation-duration: {
                '0s' if prefs['visual']['animation_level'] == 'none'
                else '0.2s' if prefs['visual']['animation_level'] == 'minimal'
                else '0.3s' if prefs['visual']['animation_level'] == 'medium'
                else '0.5s'
            };
        }}
        """
        
        return css