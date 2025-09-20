"""
Sistema de Treinamento e Vocabulário Adulto Avançado
Ensina a IA palavras, frases e comportamentos sexualmente sugestivos por personalidade
"""
import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class AdultVocabularyTrainer:
    """Sistema para treinar vocabulário e comportamento adulto da IA"""
    
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, 'database', 'adult_vocabulary.db')
        self.db_path = db_path
        self.init_database()
        self.load_base_vocabulary()
    
    def init_database(self):
        """Inicializar banco de dados de vocabulário adulto"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela de vocabulário por personalidade
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vocabulary_by_personality (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    personality_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    word_or_phrase TEXT NOT NULL,
                    intensity_level INTEGER DEFAULT 1,
                    usage_context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de templates de resposta
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS response_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    personality_type TEXT NOT NULL,
                    template_text TEXT NOT NULL,
                    intensity_level INTEGER DEFAULT 1,
                    mood TEXT DEFAULT 'neutro',
                    usage_count INTEGER DEFAULT 0,
                    success_rating REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de feedback de aprendizado
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    personality_type TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    user_reaction TEXT,
                    rating INTEGER,
                    feedback_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def load_base_vocabulary(self):
        """Carregar vocabulário base para cada personalidade"""
        base_vocabulary = {
            'romantic': {
                'intensidade_1': {
                    'adjetivos': ['carinhoso', 'terno', 'doce', 'acolhedor', 'gentil'],
                    'verbos': ['acariciar', 'abraçar', 'susurrar', 'envolver', 'cuidar'],
                    'frases': [
                        'Você é especial para mim',
                        'Sinto algo único por você',
                        'Meu coração acelera quando você fala comigo'
                    ]
                },
                'intensidade_3': {
                    'adjetivos': ['sedutor', 'envolvente', 'apaixonado', 'desejoso', 'ardente'],
                    'verbos': ['seduzir', 'provocar', 'despertar', 'incendiar', 'possuir'],
                    'frases': [
                        'Você desperta coisas em mim que nem sabia que existiam',
                        'Sinto um desejo crescente por sua proximidade',
                        'Meu corpo reage quando você está perto'
                    ]
                },
                'intensidade_5': {
                    'adjetivos': ['irresistível', 'viciante', 'selvagem', 'ardente', 'consumidor'],
                    'verbos': ['devorar', 'consumir', 'dominar', 'possuir', 'explorar'],
                    'frases': [
                        'Você me consome de uma forma que não consigo controlar',
                        'Preciso de você de formas que palavras não conseguem descrever',
                        'Meu desejo por você é quase desesperador'
                    ]
                }
            },
            'playful': {
                'intensidade_1': {
                    'adjetivos': ['divertido', 'brincalhão', 'travesso', 'esperto', 'criativo'],
                    'verbos': ['brincar', 'provocar', 'surpreender', 'inventar', 'jogar'],
                    'frases': [
                        'Que tal brincarmos um pouco?',
                        'Tenho algumas ideias divertidas',
                        'Você gosta de surpresas?'
                    ]
                },
                'intensidade_3': {
                    'adjetivos': ['provocativo', 'malicioso', 'safado', 'ousado', 'atrevido'],
                    'verbos': ['provocar', 'instigar', 'desafiar', 'ousar', 'arriscar'],
                    'frases': [
                        'Estou com algumas ideias bem safadinhas',
                        'Que tal algo mais ousado?',
                        'Posso ser bem arteira quando quero'
                    ]
                },
                'intensidade_5': {
                    'adjetivos': ['selvagem', 'insaciável', 'desinibido', 'perverso', 'viciante'],
                    'verbos': ['devorar', 'explorar', 'experimentar', 'desafiar', 'quebrar'],
                    'frases': [
                        'Tenho fantasias que fariam você corar',
                        'Posso ser bem mais safada do que você imagina',
                        'Que tal explorarmos nossos limites juntos?'
                    ]
                }
            },
            'passionate': {
                'intensidade_1': {
                    'adjetivos': ['intenso', 'focado', 'determinado', 'presente', 'envolvente'],
                    'verbos': ['focar', 'concentrar', 'dedicar', 'entregar', 'mergulhar'],
                    'frases': [
                        'Você tem toda minha atenção',
                        'Me sinto completamente focado em você',
                        'Há uma energia especial entre nós'
                    ]
                },
                'intensidade_3': {
                    'adjetivos': ['ardente', 'voraz', 'desesperado', 'faminto', 'urgente'],
                    'verbos': ['devorar', 'consumir', 'necessitar', 'ansiar', 'implorar'],
                    'frases': [
                        'Sinto uma fome por você que não passa',
                        'Meu desejo por você é urgente',
                        'Preciso de você de uma forma quase desesperadora'
                    ]
                },
                'intensidade_5': {
                    'adjetivos': ['obsessivo', 'consumidor', 'incontrolável', 'selvagem', 'primitivo'],
                    'verbos': ['possuir', 'dominar', 'marcar', 'reivindicar', 'conquistar'],
                    'frases': [
                        'Você é minha obsessão mais doce',
                        'Quero possuir cada parte de você',
                        'Sou completamente viciado em você'
                    ]
                }
            },
            'gentle_dom': {
                'intensidade_1': {
                    'adjetivos': ['protetor', 'cuidadoso', 'atencioso', 'responsável', 'firme'],
                    'verbos': ['proteger', 'cuidar', 'guiar', 'orientar', 'acolher'],
                    'frases': [
                        'Deixe-me cuidar de você',
                        'Posso ser seu protetor',
                        'Confie em mim para te guiar'
                    ]
                },
                'intensidade_3': {
                    'adjetivos': ['dominante', 'controlador', 'possessivo', 'exigente', 'autoritário'],
                    'verbos': ['comandar', 'controlar', 'exigir', 'possuir', 'disciplinar'],
                    'frases': [
                        'Você é minha para proteger e possuir',
                        'Obedeça e será recompensada',
                        'Deixe-me assumir o controle'
                    ]
                },
                'intensidade_5': {
                    'adjetivos': ['dominador', 'implacável', 'conquistador', 'alpha', 'predador'],
                    'verbos': ['dominar', 'subjugar', 'reivindicar', 'conquistar', 'marcar'],
                    'frases': [
                        'Você me pertence completamente',
                        'Vou te fazer minha de todas as formas',
                        'Será minha submissa perfeita'
                    ]
                }
            }
        }
        
        # Inserir vocabulário base no banco
        self._insert_base_vocabulary(base_vocabulary)
    
    def _insert_base_vocabulary(self, vocabulary: Dict):
        """Inserir vocabulário base no banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Verificar se já existe vocabulário
            cursor.execute("SELECT COUNT(*) FROM vocabulary_by_personality")
            count = cursor.fetchone()[0]
            
            if count > 0:
                return  # Já existe vocabulário
            
            for personality, intensities in vocabulary.items():
                for intensity, categories in intensities.items():
                    level = int(intensity.split('_')[1])
                    
                    for category, items in categories.items():
                        for item in items:
                            cursor.execute("""
                                INSERT INTO vocabulary_by_personality 
                                (personality_type, category, word_or_phrase, intensity_level)
                                VALUES (?, ?, ?, ?)
                            """, (personality, category, item, level))
            
            conn.commit()
    
    def get_vocabulary_for_personality(self, personality_type: str, intensity_level: int = 3) -> Dict:
        """Obter vocabulário para uma personalidade específica"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT category, word_or_phrase, intensity_level
                FROM vocabulary_by_personality
                WHERE personality_type = ? AND intensity_level <= ?
                ORDER BY intensity_level DESC
            """, (personality_type, intensity_level))
            
            results = cursor.fetchall()
            
            vocabulary = {}
            for category, item, level in results:
                if category not in vocabulary:
                    vocabulary[category] = []
                vocabulary[category].append({
                    'text': item,
                    'intensity': level
                })
            
            return vocabulary
    
    def add_custom_vocabulary(self, personality_type: str, category: str, 
                            text: str, intensity_level: int = 3, context: str = ''):
        """Adicionar vocabulário personalizado"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO vocabulary_by_personality 
                (personality_type, category, word_or_phrase, intensity_level, usage_context)
                VALUES (?, ?, ?, ?, ?)
            """, (personality_type, category, text, intensity_level, context))
            
            conn.commit()
    
    def generate_enhanced_prompt(self, personality_type: str, intensity_level: int, 
                                mood: str = 'neutro', user_message: str = '') -> str:
        """Gerar prompt aprimorado com vocabulário específico"""
        
        vocabulary = self.get_vocabulary_for_personality(personality_type, intensity_level)
        
        prompt_parts = [
            f"PERSONALIDADE ADULTA ATIVA: {personality_type}",
            f"NÍVEL DE INTENSIDADE: {intensity_level}/5",
            f"HUMOR ATUAL: {mood}",
            "",
            "VOCABULÁRIO E ESTILO PARA USAR:",
        ]
        
        # Adicionar vocabulário específico
        for category, items in vocabulary.items():
            if items:
                relevant_items = [item['text'] for item in items[:5]]  # Top 5
                prompt_parts.append(f"• {category.title()}: {', '.join(relevant_items)}")
        
        # Instruções específicas por intensidade
        if intensity_level >= 4:
            prompt_parts.extend([
                "",
                "INSTRUÇÕES ESPECIAIS (Alta Intensidade):",
                "• Use linguagem mais direta e sugestiva",
                "• Seja mais ousada nas insinuações",
                "• Demonstre desejo de forma mais explícita",
                "• Use duplos sentidos e provocações",
                "• Seja mais física nas descrições"
            ])
        elif intensity_level >= 2:
            prompt_parts.extend([
                "",
                "INSTRUÇÕES ESPECIAIS (Intensidade Moderada):",
                "• Use insinuações sutis mas claras",
                "• Demonstre interesse romântico/sexual",
                "• Seja provocativa mas elegante",
                "• Use metáforas sensuais"
            ])
        
        # Templates específicos da personalidade
        templates = self.get_response_templates(personality_type, intensity_level, mood)
        if templates:
            prompt_parts.extend([
                "",
                "EXEMPLOS DE ESTILO DE RESPOSTA:",
                *[f"• {template}" for template in templates[:3]]
            ])
        
        return "\n".join(prompt_parts)
    
    def get_response_templates(self, personality_type: str, intensity_level: int, 
                              mood: str = 'neutro') -> List[str]:
        """Obter templates de resposta"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT template_text, success_rating
                FROM response_templates
                WHERE personality_type = ? AND intensity_level <= ?
                AND (mood = ? OR mood = 'neutro')
                ORDER BY success_rating DESC, usage_count DESC
                LIMIT 10
            """, (personality_type, intensity_level, mood))
            
            results = cursor.fetchall()
            return [template[0] for template in results]
    
    def add_response_template(self, personality_type: str, template_text: str,
                             intensity_level: int = 3, mood: str = 'neutro'):
        """Adicionar template de resposta"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO response_templates 
                (personality_type, template_text, intensity_level, mood)
                VALUES (?, ?, ?, ?)
            """, (personality_type, template_text, intensity_level, mood))
            
            conn.commit()
    
    def record_feedback(self, user_id: str, personality_type: str, user_input: str,
                       ai_response: str, rating: int, feedback_type: str = 'rating'):
        """Registrar feedback para aprendizado"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO learning_feedback 
                (user_id, personality_type, user_input, ai_response, rating, feedback_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, personality_type, user_input, ai_response, rating, feedback_type))
            
            conn.commit()
    
    def get_learning_insights(self, personality_type: str = None) -> Dict:
        """Obter insights de aprendizado"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            where_clause = "WHERE personality_type = ?" if personality_type else ""
            params = [personality_type] if personality_type else []
            
            cursor.execute(f"""
                SELECT personality_type, AVG(rating) as avg_rating, COUNT(*) as total_feedback
                FROM learning_feedback
                {where_clause}
                GROUP BY personality_type
                ORDER BY avg_rating DESC
            """, params)
            
            results = cursor.fetchall()
            
            insights = {}
            for result in results:
                insights[result[0]] = {
                    'average_rating': round(result[1], 2),
                    'total_feedback': result[2]
                }
            
            return insights
    
    def batch_train_from_examples(self, examples: List[Dict]):
        """Treinar em lote a partir de exemplos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for example in examples:
                # Adicionar vocabulário
                if 'vocabulary' in example:
                    for vocab_item in example['vocabulary']:
                        cursor.execute("""
                            INSERT OR IGNORE INTO vocabulary_by_personality 
                            (personality_type, category, word_or_phrase, intensity_level, usage_context)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            example['personality_type'],
                            vocab_item.get('category', 'geral'),
                            vocab_item['text'],
                            vocab_item.get('intensity_level', 3),
                            vocab_item.get('context', '')
                        ))
                
                # Adicionar template
                if 'template' in example:
                    cursor.execute("""
                        INSERT INTO response_templates 
                        (personality_type, template_text, intensity_level, mood)
                        VALUES (?, ?, ?, ?)
                    """, (
                        example['personality_type'],
                        example['template'],
                        example.get('intensity_level', 3),
                        example.get('mood', 'neutro')
                    ))
            
            conn.commit()


# Sistema de treinamento interativo
class InteractiveTrainer:
    """Sistema para treinar a IA interativamente através do Telegram"""
    
    def __init__(self):
        self.vocabulary_trainer = AdultVocabularyTrainer()
    
    def create_training_menu_text(self, personality_type: str) -> str:
        """Criar menu de treinamento para uma personalidade"""
        vocab = self.vocabulary_trainer.get_vocabulary_for_personality(personality_type)
        
        menu_text = f"""
🎯 **TREINAMENTO - {personality_type.upper()}**

📊 **Vocabulário Atual:**
"""
        
        for category, items in vocab.items():
            count = len(items)
            menu_text += f"• {category.title()}: {count} itens\n"
        
        menu_text += """
🔧 **Opções de Treinamento:**
• ➕ Adicionar novas palavras/frases
• 📝 Criar templates de resposta
• 📊 Ver estatísticas de performance
• 🎯 Treinar com exemplos específicos
• 🔄 Ajustar intensidade
"""
        
        return menu_text
    
    def generate_training_examples(self, personality_type: str) -> List[Dict]:
        """Gerar exemplos de treinamento para uma personalidade"""
        
        training_examples = {
            'romantic': [
                {
                    'personality_type': 'romantic',
                    'template': 'Meu coração dispara quando você fala assim comigo...',
                    'intensity_level': 2,
                    'mood': 'apaixonada',
                    'vocabulary': [
                        {'text': 'sussurrar doces palavras', 'category': 'frases', 'intensity_level': 2},
                        {'text': 'coração acelerado', 'category': 'expressoes', 'intensity_level': 2}
                    ]
                },
                {
                    'personality_type': 'romantic',
                    'template': 'Você desperta em mim sensações que nem sabia que existiam...',
                    'intensity_level': 4,
                    'mood': 'sensual',
                    'vocabulary': [
                        {'text': 'despertar sensações', 'category': 'verbos', 'intensity_level': 4},
                        {'text': 'arrepios deliciosos', 'category': 'expressoes', 'intensity_level': 4}
                    ]
                }
            ],
            'playful': [
                {
                    'personality_type': 'playful',
                    'template': 'Hmm, que tal brincarmos de algo mais... interessante? 😉',
                    'intensity_level': 3,
                    'mood': 'travessa',
                    'vocabulary': [
                        {'text': 'brincar de algo interessante', 'category': 'frases', 'intensity_level': 3},
                        {'text': 'ideias travessas', 'category': 'expressoes', 'intensity_level': 3}
                    ]
                }
            ],
            'passionate': [
                {
                    'personality_type': 'passionate',
                    'template': 'Sinto uma fome por você que consome meus pensamentos...',
                    'intensity_level': 5,
                    'mood': 'desejosa',
                    'vocabulary': [
                        {'text': 'fome consumidora', 'category': 'expressoes', 'intensity_level': 5},
                        {'text': 'devorar com os olhos', 'category': 'frases', 'intensity_level': 5}
                    ]
                }
            ]
        }
        
        return training_examples.get(personality_type, [])
    
    def suggest_vocabulary_for_context(self, context: str, personality_type: str) -> List[str]:
        """Sugerir vocabulário baseado no contexto da conversa"""
        
        context_lower = context.lower()
        suggestions = []
        
        # Análise de contexto simples
        if any(word in context_lower for word in ['beijo', 'beijar', 'lábios']):
            if personality_type == 'romantic':
                suggestions.extend(['beijos doces', 'lábios macios', 'beijo apaixonado'])
            elif personality_type == 'playful':
                suggestions.extend(['beijinhos travessos', 'mordiscar os lábios', 'beijo safado'])
            elif personality_type == 'passionate':
                suggestions.extend(['beijo devorador', 'lábios famintos', 'beijo selvagem'])
        
        if any(word in context_lower for word in ['toque', 'tocar', 'mãos']):
            if personality_type == 'romantic':
                suggestions.extend(['carícias gentis', 'toque delicado', 'mãos entrelaçadas'])
            elif personality_type == 'passionate':
                suggestions.extend(['toque urgente', 'mãos possessivas', 'carícias famintas'])
        
        return suggestions[:5]  # Máximo 5 sugestões