"""
Sistema de Aprendizado Rápido
Otimizado para o modelo Qwen2.5-4B
"""
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

class FastLearning:
    """Sistema de aprendizado acelerado para Qwen2.5-4B"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'memoria', 'fast_learning.db')
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
        
        # Configurações de otimização
        self.optimization_config = {
            'max_context_items': 10,
            'min_pattern_score': 0.7,
            'topic_similarity_threshold': 0.6,
            'learning_rate': 0.1
        }
    
    def create_tables(self):
        """Criar tabelas otimizadas para aprendizado rápido"""
        with self.conn:
            # Tabela de padrões de resposta
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS response_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    question_type TEXT,
                    response_pattern TEXT,
                    success_count INTEGER DEFAULT 1,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                    effectiveness_score REAL DEFAULT 1.0
                )
            ''')
            
            # Tabela de contexto inteligente
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS smart_contexts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    topic TEXT,
                    context_data TEXT,
                    importance_score REAL DEFAULT 1.0,
                    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de sessões de aprendizado  
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS learning_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    session_start DATETIME DEFAULT CURRENT_TIMESTAMP,
                    questions_count INTEGER DEFAULT 0,
                    improvements_count INTEGER DEFAULT 0,
                    session_quality REAL DEFAULT 1.0
                )
            ''')
            
            # Tabela de preferências aprendidas
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS learned_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    preference_key TEXT,
                    preference_value TEXT,
                    confidence_score REAL DEFAULT 0.5,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def learn_response_pattern(self, user_id, question, response, user_feedback=None):
        """Aprender padrões de resposta baseado no sucesso"""
        question_type = self._classify_question_type(question)
        
        with self.conn:
            # Verificar se padrão similar já existe
            existing = self.conn.execute('''
                SELECT id, success_count, effectiveness_score 
                FROM response_patterns 
                WHERE user_id = ? AND question_type = ?
            ''', (user_id, question_type)).fetchone()
            
            if existing:
                # Atualizar padrão existente
                new_count = existing[1] + 1
                new_score = existing[2] * 0.9 + (1.0 if user_feedback != 'negative' else 0.3) * 0.1
                
                self.conn.execute('''
                    UPDATE response_patterns 
                    SET success_count = ?, effectiveness_score = ?, last_used = CURRENT_TIMESTAMP,
                        response_pattern = ?
                    WHERE id = ?
                ''', (new_count, new_score, response[:200], existing[0]))
            else:
                # Criar novo padrão
                self.conn.execute('''
                    INSERT INTO response_patterns 
                    (user_id, question_type, response_pattern, effectiveness_score)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, question_type, response[:200], 0.8))
    
    def _classify_question_type(self, question):
        """Classificar tipo de pergunta para padrões"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['qual', 'o que', 'what']):
            return 'informational'
        elif any(word in question_lower for word in ['como', 'how']):
            return 'procedural'
        elif any(word in question_lower for word in ['por que', 'why']):
            return 'explanatory'
        elif any(word in question_lower for word in ['você', 'seu', 'sua']):
            return 'personal'
        else:
            return 'general'
    
    def get_learning_context(self, user_id, current_topic, limit=10):
        """Obter contexto inteligente baseado no aprendizado"""
        with self.conn:
            # Buscar contexto relevante por tópico e importância
            contexts = self.conn.execute('''
                SELECT context_data, importance_score 
                FROM smart_contexts 
                WHERE user_id = ? AND topic LIKE ? 
                ORDER BY importance_score DESC, last_accessed DESC 
                LIMIT ?
            ''', (user_id, f'%{current_topic}%', limit)).fetchall()
            
            # Buscar padrões de resposta eficazes
            patterns = self.conn.execute('''
                SELECT response_pattern, effectiveness_score 
                FROM response_patterns 
                WHERE user_id = ? AND effectiveness_score > 0.7 
                ORDER BY effectiveness_score DESC, last_used DESC 
                LIMIT 5
            ''', (user_id,)).fetchall()
            
            return contexts, patterns
    
    def save_smart_context(self, user_id, topic, context_data, importance=1.0):
        """Salvar contexto inteligente com pontuação de importância"""
        with self.conn:
            self.conn.execute('''
                INSERT INTO smart_contexts 
                (user_id, topic, context_data, importance_score)
                VALUES (?, ?, ?, ?)
            ''', (user_id, topic, context_data, importance))
    
    def optimize_for_qwen(self, user_message, user_profile):
        """Otimizações específicas para Qwen2.5-4B"""
        # Extrair tópico principal da mensagem
        topic = self._extract_main_topic(user_message)
        
        # Buscar contexto aprendido
        contexts, patterns = self.get_learning_context(
            user_profile.get('user_id'), topic
        )
        
        # Construir prompt otimizado para Qwen
        optimization_hints = []
        
        if patterns:
            best_pattern = patterns[0][0]  # Melhor padrão
            optimization_hints.append(f"Padrão eficaz anterior: {best_pattern}")
        
        if contexts:
            relevant_context = contexts[0][0]  # Contexto mais relevante
            optimization_hints.append(f"Contexto relevante: {relevant_context}")
        
        return optimization_hints
    
    def _extract_main_topic(self, message):
        """Extrair tópico principal da mensagem"""
        # Palavras-chave por tópico
        topics = {
            'tecnologia': ['tecnologia', 'computador', 'software', 'app', 'internet'],
            'saude': ['saúde', 'doença', 'remédio', 'médico', 'hospital'],
            'educacao': ['escola', 'estudo', 'aprender', 'ensino', 'professor'],
            'entretenimento': ['filme', 'música', 'jogo', 'diversão', 'hobby'],
            'pessoal': ['nome', 'idade', 'você', 'seu', 'sua'],
            'geografia': ['país', 'cidade', 'capital', 'lugar', 'localização']
        }
        
        message_lower = message.lower()
        for topic, keywords in topics.items():
            if any(keyword in message_lower for keyword in keywords):
                return topic
        
        return 'geral'