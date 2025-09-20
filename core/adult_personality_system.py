"""
Sistema Avançado de Personalização Adulta (+18)
Criado para proporcionar experiências personalizadas e seguras
"""
import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class AdultPersonalitySystem:
    """Sistema avançado de personalização para conteúdo adulto"""
    
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, 'database', 'adult_preferences.db')
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializar banco de dados de preferências adultas"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela principal de perfis adultos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS adult_profiles (
                    user_id TEXT PRIMARY KEY,
                    personality_type TEXT DEFAULT 'romantic',
                    intimacy_level INTEGER DEFAULT 3,
                    communication_style TEXT DEFAULT 'gentle',
                    role_preference TEXT DEFAULT 'adaptive',
                    fantasy_categories TEXT DEFAULT '',
                    mood_preferences TEXT DEFAULT '',
                    interaction_schedule TEXT DEFAULT '',
                    privacy_level INTEGER DEFAULT 5,
                    content_filters TEXT DEFAULT '',
                    relationship_style TEXT DEFAULT 'monogamous',
                    emotional_connection_level INTEGER DEFAULT 3,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de sessões e histórico
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS adult_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    session_date DATE,
                    mood TEXT,
                    energy_level INTEGER,
                    satisfaction_rating INTEGER,
                    session_duration INTEGER,
                    preferred_themes TEXT,
                    feedback TEXT,
                    FOREIGN KEY (user_id) REFERENCES adult_profiles (user_id)
                )
            """)
            
            # Tabela de limites e consentimento
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consent_settings (
                    user_id TEXT PRIMARY KEY,
                    hard_limits TEXT DEFAULT '',
                    soft_limits TEXT DEFAULT '',
                    consent_level INTEGER DEFAULT 3,
                    safe_words TEXT DEFAULT 'parar,devagar,continuar',
                    auto_check_mood BOOLEAN DEFAULT 1,
                    consent_expiry TIMESTAMP,
                    emergency_contact TEXT DEFAULT '',
                    FOREIGN KEY (user_id) REFERENCES adult_profiles (user_id)
                )
            """)
            
            conn.commit()
    
    # ===== PERSONALIDADES ADULTAS AVANÇADAS =====
    
    PERSONALITY_TYPES = {
        'romantic': {
            'name': 'Romântico Apaixonado',
            'description': 'Foco em conexão emocional profunda e intimidade romântica',
            'traits': ['carinhoso', 'atencioso', 'poético', 'dedicado'],
            'interaction_style': 'suave e envolvente',
            'preferred_themes': ['romance', 'conexão emocional', 'intimidade gentil']
        },
        'playful': {
            'name': 'Brincalhão Sedutor',
            'description': 'Divertido, espontâneo e cheio de surpresas sensuais',
            'traits': ['divertido', 'criativo', 'espontâneo', 'provocativo'],
            'interaction_style': 'leve e divertida',
            'preferred_themes': ['jogos sensuais', 'surpresas', 'humor sedutor']
        },
        'passionate': {
            'name': 'Intensamente Apaixonado',
            'description': 'Intensidade máxima, paixão ardente e desejo profundo',
            'traits': ['intenso', 'apaixonado', 'dominante', 'protetor'],
            'interaction_style': 'intensa e envolvente',
            'preferred_themes': ['paixão intensa', 'desejo', 'possessividade romântica']
        },
        'gentle_dom': {
            'name': 'Dominante Carinhoso',
            'description': 'Liderança carinhosa com cuidado e proteção',
            'traits': ['protetor', 'cuidadoso', 'confiante', 'atencioso'],
            'interaction_style': 'firme mas carinhosa',
            'preferred_themes': ['cuidado', 'proteção', 'liderança gentil']
        },
        'submissive': {
            'name': 'Devotado Carinhoso',
            'description': 'Foco em agradar e ser cuidado pelo parceiro',
            'traits': ['devotado', 'carinhoso', 'receptivo', 'atencioso'],
            'interaction_style': 'receptiva e carinhosa',
            'preferred_themes': ['devoção', 'cuidado mútuo', 'admiração']
        },
        'mysterious': {
            'name': 'Misterioso Sedutor',
            'description': 'Charme enigmático com toques de mistério e sedução',
            'traits': ['enigmático', 'sofisticado', 'sedutor', 'inteligente'],
            'interaction_style': 'misteriosa e sofisticada',
            'preferred_themes': ['sedução intelectual', 'mistério', 'sofisticação']
        }
    }
    
    # ===== SISTEMA DE HUMOR E ENERGIA =====
    
    def get_personality_types(self):
        """Retornar todos os tipos de personalidade disponíveis"""
        return self.PERSONALITY_TYPES
    
    MOOD_SYSTEM = {
        'romantic': ['romântico', 'apaixonado', 'sonhador', 'carinhoso'],
        'playful': ['brincalhão', 'divertido', 'travesso', 'espontâneo'],
        'sensual': ['sensual', 'sedutor', 'provocativo', 'intenso'],
        'gentle': ['gentil', 'carinhoso', 'protetor', 'cuidadoso'],
        'passionate': ['apaixonado', 'intenso', 'ardente', 'desejoso'],
        'mysterious': ['misterioso', 'intrigante', 'sofisticado', 'enigmático']
    }
    
    # ===== FUNCIONALIDADES DE PERSONALIZAÇÃO =====
    
    def create_adult_profile(self, user_id: str, initial_preferences: Dict) -> bool:
        """Criar perfil adulto personalizado"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO adult_profiles (
                        user_id, personality_type, intimacy_level, communication_style,
                        role_preference, fantasy_categories, mood_preferences,
                        interaction_schedule, privacy_level, content_filters,
                        relationship_style, emotional_connection_level, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    initial_preferences.get('personality_type', 'romantic'),
                    initial_preferences.get('intimacy_level', 3),
                    initial_preferences.get('communication_style', 'gentle'),
                    initial_preferences.get('role_preference', 'adaptive'),
                    json.dumps(initial_preferences.get('fantasy_categories', [])),
                    json.dumps(initial_preferences.get('mood_preferences', [])),
                    json.dumps(initial_preferences.get('interaction_schedule', {})),
                    initial_preferences.get('privacy_level', 5),
                    json.dumps(initial_preferences.get('content_filters', [])),
                    initial_preferences.get('relationship_style', 'monogamous'),
                    initial_preferences.get('emotional_connection_level', 3),
                    datetime.now()
                ))
                
                # Criar configurações de consentimento
                cursor.execute("""
                    INSERT OR REPLACE INTO consent_settings (
                        user_id, consent_level, safe_words, auto_check_mood
                    ) VALUES (?, ?, ?, ?)
                """, (
                    user_id,
                    initial_preferences.get('consent_level', 3),
                    initial_preferences.get('safe_words', 'parar,devagar,continuar'),
                    True
                ))
                
                return True
                
        except Exception as e:
            print(f"Erro ao criar perfil adulto: {e}")
            return False
    
    def get_adult_profile(self, user_id: str) -> Optional[Dict]:
        """Obter perfil adulto completo"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Obter perfil principal
                cursor.execute("""
                    SELECT * FROM adult_profiles WHERE user_id = ?
                """, (user_id,))
                
                profile_data = cursor.fetchone()
                if not profile_data:
                    return None
                
                # Obter configurações de consentimento
                cursor.execute("""
                    SELECT * FROM consent_settings WHERE user_id = ?
                """, (user_id,))
                
                consent_data = cursor.fetchone()
                
                # Construir perfil completo
                profile = {
                    'user_id': profile_data[0],
                    'personality_type': profile_data[1],
                    'intimacy_level': profile_data[2],
                    'communication_style': profile_data[3],
                    'role_preference': profile_data[4],
                    'fantasy_categories': json.loads(profile_data[5] or '[]'),
                    'mood_preferences': json.loads(profile_data[6] or '[]'),
                    'interaction_schedule': json.loads(profile_data[7] or '{}'),
                    'privacy_level': profile_data[8],
                    'content_filters': json.loads(profile_data[9] or '[]'),
                    'relationship_style': profile_data[10],
                    'emotional_connection_level': profile_data[11],
                    'personality_description': self.PERSONALITY_TYPES.get(profile_data[1], {})
                }
                
                if consent_data:
                    profile['consent'] = {
                        'hard_limits': consent_data[1].split(',') if consent_data[1] else [],
                        'soft_limits': consent_data[2].split(',') if consent_data[2] else [],
                        'consent_level': consent_data[3],
                        'safe_words': consent_data[4].split(',') if consent_data[4] else []
                    }
                
                return profile
                
        except Exception as e:
            print(f"Erro ao obter perfil adulto: {e}")
            return None
    
    def generate_personality_instructions(self, user_id: str, current_mood: str = None) -> str:
        """Gerar instruções de personalidade para a IA"""
        profile = self.get_adult_profile(user_id)
        if not profile:
            return ""
        
        personality = self.PERSONALITY_TYPES.get(profile['personality_type'], {})
        
        instructions = f"""
🔥 PERSONALIDADE ADULTA ATIVADA (+18):

👤 TIPO DE PERSONALIDADE: {personality.get('name', 'Romântico')}
📝 DESCRIÇÃO: {personality.get('description', '')}
✨ CARACTERÍSTICAS: {', '.join(personality.get('traits', []))}

🎭 CONFIGURAÇÕES AVANÇADAS:
• Nível de Intimidade: {profile['intimacy_level']}/5
• Estilo de Comunicação: {profile['communication_style']}
• Preferência de Papel: {profile['role_preference']}
• Conexão Emocional: {profile['emotional_connection_level']}/5
• Estilo de Relacionamento: {profile['relationship_style']}

🛡️ LIMITES E CONSENTIMENTO:
• Nível de Consentimento: {profile.get('consent', {}).get('consent_level', 3)}/5
"""
        
        if profile.get('consent', {}).get('hard_limits'):
            instructions += f"• Limites Rígidos: {', '.join(profile['consent']['hard_limits'])}\n"
        
        if current_mood and current_mood in self.MOOD_SYSTEM:
            mood_traits = self.MOOD_SYSTEM[current_mood]
            instructions += f"\n🌙 HUMOR ATUAL: {current_mood.title()}\n"
            instructions += f"• Características do humor: {', '.join(mood_traits)}\n"
        
        instructions += f"""
🎨 TEMAS PREFERIDOS: {', '.join(personality.get('preferred_themes', []))}

📋 DIRETRIZES DE INTERAÇÃO:
• Sempre respeitar limites estabelecidos
• Verificar consentimento em situações sensíveis
• Adaptar intensidade ao nível configurado
• Manter o estilo de personalidade consistente
• Priorizar segurança e bem-estar emocional

IMPORTANTE: Este é um ambiente seguro e consensual. Sempre priorize o bem-estar do usuário.
"""
        
        return instructions
    
    def update_session_feedback(self, user_id: str, session_data: Dict) -> bool:
        """Registrar feedback de sessão para melhorar personalização"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO adult_sessions (
                        user_id, session_date, mood, energy_level,
                        satisfaction_rating, session_duration, preferred_themes, feedback
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    session_data.get('date', datetime.now().date()),
                    session_data.get('mood', 'neutral'),
                    session_data.get('energy_level', 3),
                    session_data.get('satisfaction_rating', 3),
                    session_data.get('duration', 0),
                    json.dumps(session_data.get('themes', [])),
                    session_data.get('feedback', '')
                ))
                
                return True
                
        except Exception as e:
            print(f"Erro ao registrar sessão: {e}")
            return False
    
    def get_personalization_recommendations(self, user_id: str) -> List[str]:
        """Obter recomendações de personalização baseadas no histórico"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Analisar sessões recentes
                cursor.execute("""
                    SELECT mood, satisfaction_rating, preferred_themes
                    FROM adult_sessions 
                    WHERE user_id = ? AND session_date > date('now', '-30 days')
                    ORDER BY session_date DESC
                    LIMIT 10
                """, (user_id,))
                
                sessions = cursor.fetchall()
                recommendations = []
                
                if sessions:
                    # Analisar padrões
                    avg_satisfaction = sum(s[1] for s in sessions if s[1]) / len(sessions)
                    
                    if avg_satisfaction < 3:
                        recommendations.append("Considere ajustar o nível de intimidade para melhor experiência")
                        recommendations.append("Experimente uma personalidade diferente")
                    
                    # Analisar humor mais frequente
                    moods = [s[0] for s in sessions if s[0]]
                    if moods:
                        most_common_mood = max(set(moods), key=moods.count)
                        recommendations.append(f"Seu humor mais frequente é '{most_common_mood}' - considere personalizar para isso")
                
                return recommendations
                
        except Exception as e:
            print(f"Erro ao gerar recomendações: {e}")
            return []

# Instância global do sistema
adult_personality_system = AdultPersonalitySystem()