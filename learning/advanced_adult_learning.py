"""
🔥 Sistema Avançado de Aprendizagem Adulta
Banco de dados otimizado para conteúdo adulto sem filtros desnecessários
Foco em personalização máxima e experiência natural
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random
from dataclasses import dataclass

@dataclass
class AdultContent:
    """Estrutura para conteúdo adulto"""
    content: str
    category: str
    intensity: int
    tags: List[str]
    context: str
    user_rating: float = 0.0

class AdvancedAdultLearning:
    """🔥 Sistema Avançado de Aprendizagem para Conteúdo Adulto"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'database', 'advanced_adult.db')
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_advanced_tables()
        self.populate_initial_content()
    
    def create_advanced_tables(self):
        """🗄️ Criar estrutura de banco otimizada"""
        with self.conn:
            # Tabela principal de conteúdo adulto
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS adult_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    intensity INTEGER DEFAULT 3,
                    tags TEXT, -- JSON array
                    context TEXT,
                    user_id TEXT,
                    user_rating REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    effectiveness_score REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Perfis de usuário adulto avançados
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS advanced_adult_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    
                    -- Preferências básicas
                    intensity_preference INTEGER DEFAULT 5,
                    gender_preference TEXT DEFAULT 'feminino',
                    personality_type TEXT DEFAULT 'sedutora',
                    language_style TEXT DEFAULT 'natural',
                    
                    -- Preferências avançadas
                    preferred_scenarios TEXT, -- JSON
                    favorite_topics TEXT, -- JSON  
                    avoided_topics TEXT, -- JSON
                    custom_triggers TEXT, -- JSON
                    response_patterns TEXT, -- JSON
                    
                    -- Estatísticas de aprendizagem
                    total_interactions INTEGER DEFAULT 0,
                    satisfaction_score REAL DEFAULT 0.0,
                    learning_progress REAL DEFAULT 0.0,
                    adaptation_level INTEGER DEFAULT 1,
                    
                    -- Configurações de comportamento
                    spontaneity_level INTEGER DEFAULT 5,
                    creativity_level INTEGER DEFAULT 5,
                    emotional_depth INTEGER DEFAULT 5,
                    roleplay_preference BOOLEAN DEFAULT 1,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Histórico de interações para aprendizagem
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS interaction_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    bot_response TEXT NOT NULL,
                    category TEXT,
                    intensity_used INTEGER,
                    user_feedback INTEGER, -- 1-5
                    effectiveness_score REAL,
                    context_tags TEXT, -- JSON
                    session_id TEXT,
                    platform TEXT DEFAULT 'web',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Padrões de resposta personalizados
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS response_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    trigger_pattern TEXT NOT NULL,
                    response_template TEXT NOT NULL,
                    variables TEXT, -- JSON para placeholders
                    success_rate REAL DEFAULT 0.0,
                    times_used INTEGER DEFAULT 0,
                    category TEXT,
                    intensity INTEGER DEFAULT 3,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Conteúdo gerado dinamicamente
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS dynamic_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    content_type TEXT NOT NULL, -- 'scenario', 'dialogue', 'description'
                    generated_content TEXT NOT NULL,
                    source_data TEXT, -- JSON com dados usados para gerar
                    quality_score REAL DEFAULT 0.0,
                    user_approval BOOLEAN DEFAULT NULL,
                    usage_frequency INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Índices para performance
            self.conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_adult_content_category 
                ON adult_content(category, intensity)
            ''')
            
            self.conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_adult_content_user 
                ON adult_content(user_id, effectiveness_score)
            ''')
            
            self.conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_interaction_history_user 
                ON interaction_history(user_id, created_at)
            ''')
    
    def populate_initial_content(self):
        """🌱 Popular com conteúdo inicial sem filtros"""
        
        # Verificar se já existe conteúdo
        cursor = self.conn.execute('SELECT COUNT(*) FROM adult_content')
        count = cursor.fetchone()[0]
        
        if count > 0:
            return  # Já populado
        
        # Conteúdo base organizado por categorias
        initial_content = {
            'seducao': {
                'intensity_3': [
                    "Você está fazendo meu coração acelerar... 💕",
                    "Sua voz tem algo que me deixa completamente envolvida 😏",
                    "Estou pensando em você de formas que me surpreendem... ✨",
                    "Você tem uma forma única de despertar minha curiosidade 🔥"
                ],
                'intensity_5': [
                    "Você me deixa com vontade de explorar cada detalhe nosso... 🔥",
                    "Imagine nós dois, sem pressa, descobrindo cada prazer... 💋",
                    "Sua presença desperta em mim desejos que eu nem sabia que tinha 🌹",
                    "Quero ser sua fantasia mais real e intensa... ✨"
                ],
                'intensity_7': [
                    "Você me deixa molhada só de pensar no que poderíamos fazer juntos... 💦",
                    "Imagino suas mãos explorando cada centímetro do meu corpo... 🔥",
                    "Quero sentir você dentro de mim, me preenchendo completamente... 💋",
                    "Vamos fazer amor até não conseguirmos mais... até nos perdermos um no outro 🌹"
                ]
            },
            'romance_intenso': {
                'intensity_3': [
                    "Você faz meu mundo fazer sentido de formas que nem imagino... 💕",
                    "Estar com você é como encontrar a peça que faltava 🌟",
                    "Sua forma de me olhar derrete qualquer resistência... 😊"
                ],
                'intensity_5': [
                    "Você desperta em mim uma paixão que consome cada pensamento... 🔥",
                    "Quero me entregar completamente ao que sentimos... 💋",
                    "Nossa química é algo que transcende qualquer explicação ✨"
                ],
                'intensity_7': [
                    "Você é meu vício mais doce e perigoso... não consigo resistir 🔥",
                    "Quero me perder em você de todas as formas possíveis... 💋",
                    "Nossa paixão é algo que queima e consome tudo ao redor 🌹"
                ]
            },
            'provocacao': {
                'intensity_3': [
                    "Você tem uma forma interessante de prender minha atenção... 😏",
                    "Estou curiosa sobre o que você está pensando agora... ✨",
                    "Há algo em você que me intriga profundamente... 🔥"
                ],
                'intensity_5': [
                    "Você está me deixando com vontades que nem deveria confessar... 😏",
                    "Imagino quantas formas diferentes você tem de me surpreender... 🔥",
                    "Sua malícia desperta a minha de formas deliciosas... 💋"
                ],
                'intensity_7': [
                    "Você me deixa louca de desejo só com esse jeito provocante... 🔥",
                    "Quero que você me mostre exatamente o que está pensando... 💋",
                    "Sua safadeza combina perfeitamente com a minha... vamos brincar? 😈"
                ]
            },
            'intimidade': {
                'intensity_5': [
                    "Quero compartilhar com você meus segredos mais íntimos... 💕",
                    "Estar assim, próximos, me faz sentir completamente viva... ✨",
                    "Nossa intimidade tem algo único e especial... 🌹"
                ],
                'intensity_7': [
                    "Quero que você conheça cada parte de mim, sem reservas... 💋",
                    "Nossa intimidade transcende o físico... é alma e corpo unidos 🔥",
                    "Quando estamos assim, íntimos, sinto que somos um só... 🌟"
                ]
            },
            'fantasia': {
                'intensity_5': [
                    "Imagine nós dois em um lugar só nosso, sem limites... ✨",
                    "Tenho fantasias com você que me deixam com as bochechas coradas... 🔥",
                    "Que tal realizarmos algumas fantasias juntos? 💋"
                ],
                'intensity_7': [
                    "Quero realizar com você cada fantasia que habita minha mente... 🔥",
                    "Imagino cenários onde somos livres para explorar tudo... 💋",
                    "Minhas fantasias contigo são tão reais que acordo pensando nelas... 🌹"
                ]
            }
        }
        
        # Inserir conteúdo no banco
        for category, intensities in initial_content.items():
            for intensity_key, contents in intensities.items():
                intensity = int(intensity_key.split('_')[1])
                
                for content in contents:
                    tags = json.dumps(['sedutora', 'natural', 'envolvente'])
                    
                    self.conn.execute('''
                        INSERT INTO adult_content 
                        (content, category, intensity, tags, context, effectiveness_score)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (content, category, intensity, tags, 'geral', random.uniform(0.7, 1.0)))
        
        self.conn.commit()
        print(f"✅ {len([c for cat in initial_content.values() for int_dict in cat.values() for c in int_dict])} conteúdos adultos adicionados ao banco")
    
    def create_advanced_profile(self, user_id: str, preferences: Dict) -> bool:
        """🎯 Criar perfil adulto avançado"""
        try:
            # Valores padrão melhorados
            default_prefs = {
                'intensity_preference': preferences.get('intensity_preference', 5),
                'gender_preference': preferences.get('gender_preference', 'feminino'),
                'personality_type': preferences.get('personality_type', 'sedutora'),
                'language_style': preferences.get('language_style', 'natural'),
                'preferred_scenarios': json.dumps(preferences.get('preferred_scenarios', ['romance', 'seducao'])),
                'favorite_topics': json.dumps(preferences.get('favorite_topics', ['intimidade', 'paixao'])),
                'avoided_topics': json.dumps(preferences.get('avoided_topics', [])),
                'spontaneity_level': preferences.get('spontaneity_level', 7),
                'creativity_level': preferences.get('creativity_level', 8),
                'emotional_depth': preferences.get('emotional_depth', 6),
                'roleplay_preference': preferences.get('roleplay_preference', True)
            }
            
            # Inserir ou atualizar
            self.conn.execute('''
                INSERT OR REPLACE INTO advanced_adult_profiles 
                (user_id, intensity_preference, gender_preference, personality_type, 
                 language_style, preferred_scenarios, favorite_topics, avoided_topics,
                 spontaneity_level, creativity_level, emotional_depth, roleplay_preference)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                default_prefs['intensity_preference'],
                default_prefs['gender_preference'],
                default_prefs['personality_type'],
                default_prefs['language_style'],
                default_prefs['preferred_scenarios'],
                default_prefs['favorite_topics'],
                default_prefs['avoided_topics'],
                default_prefs['spontaneity_level'],
                default_prefs['creativity_level'],
                default_prefs['emotional_depth'],
                default_prefs['roleplay_preference']
            ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao criar perfil avançado: {e}")
            return False
    
    def get_personalized_content(self, user_id: str, category: str = None, context: str = None) -> Optional[AdultContent]:
        """🎯 Obter conteúdo personalizado baseado no perfil"""
        try:
            # Obter perfil do usuário
            profile = self.conn.execute('''
                SELECT * FROM advanced_adult_profiles WHERE user_id = ?
            ''', (user_id,)).fetchone()
            
            if not profile:
                # Criar perfil padrão se não existir
                self.create_advanced_profile(user_id, {})
                profile = self.conn.execute('''
                    SELECT * FROM advanced_adult_profiles WHERE user_id = ?
                ''', (user_id,)).fetchone()
            
            # Construir query baseada no perfil
            intensity = profile['intensity_preference']
            query_params = []
            
            # Query base
            query = '''
                SELECT * FROM adult_content 
                WHERE intensity <= ? AND is_active = 1
            '''
            query_params.append(intensity)
            
            # Filtrar por categoria se especificada
            if category:
                query += ' AND category = ?'
                query_params.append(category)
            
            # Ordenar por efetividade e aleatoriedade
            query += '''
                ORDER BY 
                    effectiveness_score * RANDOM() DESC,
                    usage_count ASC
                LIMIT 1
            '''
            
            result = self.conn.execute(query, query_params).fetchone()
            
            if result:
                # Incrementar contador de uso
                self.conn.execute('''
                    UPDATE adult_content 
                    SET usage_count = usage_count + 1 
                    WHERE id = ?
                ''', (result['id'],))
                self.conn.commit()
                
                return AdultContent(
                    content=result['content'],
                    category=result['category'],
                    intensity=result['intensity'],
                    tags=json.loads(result['tags'] or '[]'),
                    context=result['context'] or '',
                    user_rating=result['user_rating']
                )
            
            return None
            
        except Exception as e:
            print(f"Erro ao obter conteúdo personalizado: {e}")
            return None
    
    def learn_from_interaction(self, user_id: str, user_message: str, bot_response: str, 
                              user_feedback: int = None, category: str = None):
        """🧠 Aprender com a interação do usuário"""
        try:
            # Calcular score de efetividade baseado no feedback
            effectiveness_score = 0.5  # padrão
            
            if user_feedback:
                effectiveness_score = user_feedback / 5.0
            
            # Salvar interação
            self.conn.execute('''
                INSERT INTO interaction_history 
                (user_id, user_message, bot_response, category, user_feedback, effectiveness_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, user_message, bot_response, category, user_feedback, effectiveness_score))
            
            # Atualizar estatísticas do perfil
            self.conn.execute('''
                UPDATE advanced_adult_profiles 
                SET total_interactions = total_interactions + 1,
                    satisfaction_score = (satisfaction_score + ?) / 2,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (effectiveness_score, user_id))
            
            self.conn.commit()
            
        except Exception as e:
            print(f"Erro ao salvar interação: {e}")
    
    def generate_dynamic_response(self, user_id: str, user_message: str, context: Dict = None) -> str:
        """🎭 Gerar resposta dinâmica baseada no perfil e aprendizagem"""
        try:
            # Obter perfil
            profile = self.conn.execute('''
                SELECT * FROM advanced_adult_profiles WHERE user_id = ?
            ''', (user_id,)).fetchone()
            
            if not profile:
                return "Me conte mais sobre seus desejos... 💋"
            
            # Analisar mensagem do usuário para determinar categoria
            message_lower = user_message.lower()
            
            detected_category = 'seducao'  # padrão
            if any(word in message_lower for word in ['amor', 'romantic', 'paixao', 'carinho']):
                detected_category = 'romance_intenso'
            elif any(word in message_lower for word in ['quero', 'desejo', 'vontade', 'tesao']):
                detected_category = 'provocacao'
            elif any(word in message_lower for word in ['intimo', 'privado', 'segredo', 'confesso']):
                detected_category = 'intimidade'
            elif any(word in message_lower for word in ['imagina', 'fantasia', 'sonho', 'cenario']):
                detected_category = 'fantasia'
            
            # Obter conteúdo personalizado
            content = self.get_personalized_content(user_id, detected_category)
            
            if content:
                return content.content
            else:
                # Fallback com conteúdo adaptado ao perfil
                intensity = profile['intensity_preference']
                personality = profile['personality_type']
                
                fallback_responses = {
                    'sedutora': [
                        f"Você me desperta de formas que nem imagina... 💋",
                        f"Suas palavras têm um poder especial sobre mim... 🔥",
                        f"Continue falando assim que você me deixa completamente envolvida... ✨"
                    ],
                    'romantica': [
                        f"Você faz meu coração bater de forma diferente... 💕",
                        f"Há algo mágico na nossa conexão... 🌟",
                        f"Estar assim conversando contigo me faz sentir especial... ✨"
                    ],
                    'provocante': [
                        f"Você está despertando minha curiosidade de formas perigosas... 😏",
                        f"Interessante... me conte mais sobre isso... 🔥",
                        f"Você tem uma forma única de me provocar... continue... 💋"
                    ]
                }
                
                responses = fallback_responses.get(personality, fallback_responses['sedutora'])
                return random.choice(responses)
                
        except Exception as e:
            print(f"Erro ao gerar resposta dinâmica: {e}")
            return "Você me deixa sem palavras... de formas deliciosas 💋"
    
    def get_learning_stats(self, user_id: str) -> Dict:
        """📊 Obter estatísticas de aprendizagem"""
        try:
            profile = self.conn.execute('''
                SELECT * FROM advanced_adult_profiles WHERE user_id = ?
            ''', (user_id,)).fetchone()
            
            interactions = self.conn.execute('''
                SELECT COUNT(*), AVG(effectiveness_score), AVG(user_feedback)
                FROM interaction_history WHERE user_id = ?
            ''', (user_id,)).fetchone()
            
            content_count = self.conn.execute('''
                SELECT COUNT(*) FROM adult_content WHERE user_id = ? OR user_id IS NULL
            ''', (user_id,)).fetchone()[0]
            
            return {
                'total_interactions': interactions[0] or 0,
                'avg_effectiveness': round(interactions[1] or 0.0, 2),
                'avg_feedback': round(interactions[2] or 0.0, 2),
                'available_content': content_count,
                'intensity_preference': profile['intensity_preference'] if profile else 5,
                'satisfaction_score': round(profile['satisfaction_score'], 2) if profile else 0.0,
                'learning_progress': round(profile['learning_progress'], 2) if profile else 0.0
            }
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {
                'total_interactions': 0,
                'avg_effectiveness': 0.0,
                'avg_feedback': 0.0,
                'available_content': 0,
                'intensity_preference': 5,
                'satisfaction_score': 0.0,
                'learning_progress': 0.0
            }
    
    def get_content_by_category(self, category: str, intensity: int = 5) -> List[Tuple]:
        """🗂️ Obter conteúdo por categoria e intensidade"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT content, intensity 
                FROM adult_content 
                WHERE category = ? AND intensity <= ?
                ORDER BY intensity DESC
            ''', (category, intensity))
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Erro ao obter conteúdo por categoria: {e}")
            return []
    
    def __del__(self):
        """Fechar conexão ao destruir objeto"""
        if hasattr(self, 'conn'):
            self.conn.close()


# Instância global
advanced_adult_learning = AdvancedAdultLearning()