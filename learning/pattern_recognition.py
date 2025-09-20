"""
Sistema de Reconhecimento de Padrões
Especializado em identificar padrões de conversação e preferências do usuário
"""
import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class PatternRecognitionSystem:
    """Sistema avançado de reconhecimento de padrões para personalização"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'memoria', 'pattern_recognition.db')
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        """Criar tabelas para reconhecimento de padrões"""
        with self.conn:
            # Tabela de padrões de usuário
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS user_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    confidence_score REAL DEFAULT 0.5,
                    context TEXT
                )
            ''')
            
            # Tabela de correlações
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS pattern_correlations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    pattern_a TEXT NOT NULL,
                    pattern_b TEXT NOT NULL,
                    correlation_strength REAL DEFAULT 0.5,
                    co_occurrence_count INTEGER DEFAULT 1,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de tendências temporais
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS temporal_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    time_pattern TEXT NOT NULL,
                    behavior_pattern TEXT NOT NULL,
                    strength REAL DEFAULT 0.5,
                    sample_size INTEGER DEFAULT 1,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def analyze_conversation_pattern(self, user_id: str, message: str, response: str) -> Dict:
        """Analisar padrões em uma conversa"""
        patterns_found = {}
        
        # 1. Padrões de comprimento de mensagem
        message_length_category = self._categorize_message_length(message)
        patterns_found['message_length'] = message_length_category
        
        # 2. Padrões de sentimento
        sentiment = self._analyze_sentiment(message)
        patterns_found['sentiment'] = sentiment
        
        # 3. Padrões de tópicos
        topics = self._extract_topics(message)
        patterns_found['topics'] = topics
        
        # 4. Padrões temporais
        current_hour = datetime.now().hour
        time_category = self._categorize_time(current_hour)
        patterns_found['time_pattern'] = time_category
        
        # 5. Padrões de linguagem
        language_patterns = self._analyze_language_patterns(message)
        patterns_found['language_patterns'] = language_patterns
        
        # Salvar padrões encontrados
        self._save_patterns(user_id, patterns_found)
        
        return patterns_found
    
    def _categorize_message_length(self, message: str) -> str:
        """Categorizar comprimento da mensagem"""
        length = len(message)
        if length <= 20:
            return 'very_short'
        elif length <= 50:
            return 'short'
        elif length <= 150:
            return 'medium'
        elif length <= 300:
            return 'long'
        else:
            return 'very_long'
    
    def _analyze_sentiment(self, message: str) -> str:
        """Análise básica de sentimento"""
        message_lower = message.lower()
        
        positive_words = ['bom', 'ótimo', 'excelente', 'feliz', 'alegre', 'obrigado', 'gosto', 'legal']
        negative_words = ['ruim', 'péssimo', 'triste', 'raiva', 'ódio', 'problema', 'erro', 'difícil']
        question_words = ['?', 'como', 'que', 'quando', 'onde', 'por que', 'qual']
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        question_count = sum(1 for word in question_words if word in message_lower)
        
        if question_count > 0:
            return 'questioning'
        elif positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _extract_topics(self, message: str) -> List[str]:
        """Extrair tópicos da mensagem"""
        message_lower = message.lower()
        topics = []
        
        topic_keywords = {
            'technology': ['computador', 'software', 'programa', 'app', 'internet', 'site', 'código'],
            'entertainment': ['filme', 'música', 'jogo', 'série', 'tv', 'youtube', 'netflix'],
            'education': ['estudo', 'escola', 'faculdade', 'curso', 'aprender', 'ensino', 'prova'],
            'work': ['trabalho', 'emprego', 'projeto', 'reunião', 'chefe', 'carreira', 'salário'],
            'personal': ['família', 'amigo', 'relacionamento', 'casa', 'comida', 'saúde', 'vida'],
            'sports': ['futebol', 'esporte', 'jogo', 'time', 'partida', 'campeonato', 'atleta']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)
        
        return topics if topics else ['general']
    
    def _categorize_time(self, hour: int) -> str:
        """Categorizar horário da mensagem"""
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 18:
            return 'afternoon'
        elif 18 <= hour < 22:
            return 'evening'
        else:
            return 'night'
    
    def _analyze_language_patterns(self, message: str) -> Dict:
        """Analisar padrões de linguagem"""
        patterns = {}
        
        # Formalidade
        formal_indicators = ['senhor', 'senhora', 'por favor', 'gostaria', 'poderia']
        informal_indicators = ['oi', 'olá', 'opa', 'cara', 'mano', 'galera']
        
        formal_count = sum(1 for word in formal_indicators if word in message.lower())
        informal_count = sum(1 for word in informal_indicators if word in message.lower())
        
        if formal_count > informal_count:
            patterns['formality'] = 'formal'
        elif informal_count > formal_count:
            patterns['formality'] = 'informal'
        else:
            patterns['formality'] = 'neutral'
        
        # Emotividade
        emotion_indicators = ['!', '😊', '😢', '😠', '❤️', 'haha', 'kkkk', 'rsrs']
        emotion_count = sum(1 for indicator in emotion_indicators if indicator in message)
        
        patterns['emotiveness'] = 'high' if emotion_count > 2 else ('medium' if emotion_count > 0 else 'low')
        
        return patterns
    
    def _save_patterns(self, user_id: str, patterns: Dict):
        """Salvar padrões identificados"""
        try:
            with self.conn:
                for pattern_type, pattern_value in patterns.items():
                    if isinstance(pattern_value, list):
                        pattern_value = json.dumps(pattern_value)
                    elif isinstance(pattern_value, dict):
                        pattern_value = json.dumps(pattern_value)
                    
                    # Verificar se padrão já existe
                    cursor = self.conn.execute('''
                        SELECT id, frequency FROM user_patterns
                        WHERE user_id = ? AND pattern_type = ? AND pattern_data = ?
                    ''', (user_id, pattern_type, str(pattern_value)))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Atualizar frequência
                        self.conn.execute('''
                            UPDATE user_patterns
                            SET frequency = frequency + 1,
                                last_seen = CURRENT_TIMESTAMP,
                                confidence_score = MIN(1.0, confidence_score + 0.1)
                            WHERE id = ?
                        ''', (existing[0],))
                    else:
                        # Inserir novo padrão
                        self.conn.execute('''
                            INSERT INTO user_patterns
                            (user_id, pattern_type, pattern_data, confidence_score)
                            VALUES (?, ?, ?, 0.3)
                        ''', (user_id, pattern_type, str(pattern_value)))
        except Exception as e:
            print(f"Erro ao salvar padrões: {e}")
    
    def get_user_patterns(self, user_id: str, pattern_type: Optional[str] = None) -> List[Dict]:
        """Obter padrões do usuário"""
        try:
            query = '''
                SELECT pattern_type, pattern_data, frequency, confidence_score, last_seen
                FROM user_patterns
                WHERE user_id = ?
            '''
            params = [user_id]
            
            if pattern_type:
                query += ' AND pattern_type = ?'
                params.append(pattern_type)
            
            query += ' ORDER BY confidence_score DESC, frequency DESC'
            
            cursor = self.conn.execute(query, params)
            results = cursor.fetchall()
            
            patterns = []
            for row in results:
                pattern = {
                    'type': row[0],
                    'data': row[1],
                    'frequency': row[2],
                    'confidence': row[3],
                    'last_seen': row[4]
                }
                
                # Tentar decodificar JSON se necessário
                try:
                    pattern['data'] = json.loads(row[1])
                except:
                    pattern['data'] = row[1]
                
                patterns.append(pattern)
            
            return patterns
        
        except Exception as e:
            print(f"Erro ao obter padrões: {e}")
            return []
    
    def predict_user_preference(self, user_id: str, context: str) -> Dict:
        """Prever preferência do usuário baseado em padrões"""
        patterns = self.get_user_patterns(user_id)
        
        predictions = {
            'response_length': 'medium',
            'formality': 'neutral',
            'topics_of_interest': [],
            'preferred_time': 'any',
            'confidence': 0.5
        }
        
        # Analisar padrões para fazer previsões
        topic_frequencies = {}
        formality_scores = {'formal': 0, 'informal': 0, 'neutral': 0}
        length_preferences = {}
        
        for pattern in patterns:
            if pattern['type'] == 'topics':
                topics = pattern['data'] if isinstance(pattern['data'], list) else [pattern['data']]
                for topic in topics:
                    topic_frequencies[topic] = topic_frequencies.get(topic, 0) + pattern['frequency']
            
            elif pattern['type'] == 'language_patterns' and isinstance(pattern['data'], dict):
                formality = pattern['data'].get('formality', 'neutral')
                formality_scores[formality] += pattern['frequency'] * pattern['confidence']
            
            elif pattern['type'] == 'message_length':
                length_preferences[pattern['data']] = length_preferences.get(pattern['data'], 0) + pattern['frequency']
        
        # Determinar preferências
        if topic_frequencies:
            predictions['topics_of_interest'] = sorted(topic_frequencies.keys(), 
                                                     key=lambda x: topic_frequencies[x], 
                                                     reverse=True)[:3]
        
        if formality_scores:
            predictions['formality'] = max(formality_scores, key=formality_scores.get)
        
        if length_preferences:
            preferred_length = max(length_preferences, key=length_preferences.get)
            predictions['response_length'] = preferred_length
        
        # Calcular confiança geral
        total_patterns = len(patterns)
        if total_patterns > 0:
            avg_confidence = sum(p['confidence'] for p in patterns) / total_patterns
            predictions['confidence'] = min(1.0, avg_confidence + (total_patterns * 0.05))
        
        return predictions
    
    def cleanup_old_patterns(self, days_old: int = 30):
        """Limpar padrões antigos e de baixa confiança"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            with self.conn:
                # Remover padrões muito antigos com baixa confiança
                self.conn.execute('''
                    DELETE FROM user_patterns
                    WHERE last_seen < ? AND confidence_score < 0.3
                ''', (cutoff_date.isoformat(),))
                
                # Reduzir confiança de padrões antigos
                self.conn.execute('''
                    UPDATE user_patterns
                    SET confidence_score = MAX(0.1, confidence_score - 0.1)
                    WHERE last_seen < ?
                ''', (cutoff_date.isoformat(),))
        
        except Exception as e:
            print(f"Erro ao limpar padrões antigos: {e}")