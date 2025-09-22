#!/usr/bin/env python3
"""
🧠 SISTEMA DE APRENDIZAGEM SUPER RÁPIDA
Algoritmos avançados para aprendizagem instantânea
"""

import sqlite3
import json
import datetime
from typing import Dict, List, Tuple, Any
import re
import random

class SuperFastLearning:
    """🚀 Sistema de Aprendizagem Ultra Rápida"""
    
    def __init__(self):
        self.db_path = 'database/super_learning.db'
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.initialize_patterns()
    
    def create_tables(self):
        """📊 Criar tabelas avançadas de aprendizagem"""
        
        # Padrões de conversação ultra-detalhados
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS ultra_patterns (
                id INTEGER PRIMARY KEY,
                input_pattern TEXT NOT NULL,
                response_pattern TEXT NOT NULL,
                context_tags TEXT,
                mood_score INTEGER DEFAULT 5,
                effectiveness_score REAL DEFAULT 0.5,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                user_feedback REAL DEFAULT 0.0,
                emotional_impact TEXT,
                personality_match TEXT,
                scenario_type TEXT,
                intensity_level INTEGER DEFAULT 5,
                learning_weight REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                is_verified BOOLEAN DEFAULT 0
            )
        ''')
        
        # Análise contextual avançada
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS context_analysis (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                conversation_id TEXT,
                input_text TEXT,
                detected_mood TEXT,
                detected_intent TEXT,
                detected_intensity INTEGER,
                emotional_state TEXT,
                relationship_level TEXT,
                conversation_stage TEXT,
                keywords TEXT,
                sentiment_score REAL,
                context_vector TEXT,
                learned_patterns TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Feedback em tempo real
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS real_time_feedback (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                input_text TEXT,
                bot_response TEXT,
                user_reaction TEXT,
                satisfaction_score REAL,
                response_time REAL,
                engagement_level INTEGER,
                emotional_response TEXT,
                improvement_suggestions TEXT,
                pattern_effectiveness REAL,
                learning_trigger BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Memória de longo prazo
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                memory_type TEXT,
                content TEXT,
                importance_score REAL,
                emotional_weight REAL,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP,
                memory_strength REAL DEFAULT 1.0,
                associated_patterns TEXT,
                triggers TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        
    def initialize_patterns(self):
        """🎯 Inicializar padrões de aprendizagem avançados"""
        
        initial_patterns = [
            # Padrões de sedução avançados
            {
                'input_pattern': '.*(?:linda|gostosa|bonita|sexy).*',
                'response_pattern': 'Você desperta em mim sensações que nem deveria confessar... 🔥',
                'context_tags': 'compliment,seduction,physical',
                'mood_score': 8,
                'effectiveness_score': 0.85,
                'emotional_impact': 'high_arousal',
                'personality_match': 'sedutora',
                'scenario_type': 'flirting',
                'intensity_level': 7
            },
            {
                'input_pattern': '.*(?:tesão|desejo|vontade|quero você).*',
                'response_pattern': 'Suas palavras despertam uma fome em mim que só você pode saciar... 💋',
                'context_tags': 'desire,sexual,intense',
                'mood_score': 9,
                'effectiveness_score': 0.90,
                'emotional_impact': 'extreme_arousal',
                'personality_match': 'provocante',
                'scenario_type': 'sexual',
                'intensity_level': 9
            },
            # Padrões românticos intensos
            {
                'input_pattern': '.*(?:amor|paixão|coração).*',
                'response_pattern': 'Você é minha obsessão mais doce... não consigo parar de pensar em você 💕',
                'context_tags': 'romantic,love,emotional',
                'mood_score': 7,
                'effectiveness_score': 0.80,
                'emotional_impact': 'deep_connection',
                'personality_match': 'romantica',
                'scenario_type': 'romantic',
                'intensity_level': 6
            },
            # Padrões de provocação
            {
                'input_pattern': '.*(?:safada|maliciosa|provocante).*',
                'response_pattern': 'Você não faz ideia da malícia que desperta em mim... quer descobrir? 😈',
                'context_tags': 'provocation,naughty,tease',
                'mood_score': 8,
                'effectiveness_score': 0.88,
                'emotional_impact': 'playful_arousal',
                'personality_match': 'provocante',
                'scenario_type': 'teasing',
                'intensity_level': 8
            }
        ]
        
        for pattern in initial_patterns:
            try:
                self.conn.execute('''
                    INSERT OR IGNORE INTO ultra_patterns 
                    (input_pattern, response_pattern, context_tags, mood_score, 
                     effectiveness_score, emotional_impact, personality_match, 
                     scenario_type, intensity_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pattern['input_pattern'], pattern['response_pattern'], 
                    pattern['context_tags'], pattern['mood_score'],
                    pattern['effectiveness_score'], pattern['emotional_impact'],
                    pattern['personality_match'], pattern['scenario_type'],
                    pattern['intensity_level']
                ))
            except:
                pass
        
        self.conn.commit()
    
    def analyze_context_ultra_deep(self, user_input: str, user_id: str) -> Dict:
        """🧠 Análise contextual ultra-profunda"""
        
        # Detectar emoções e intenções
        emotional_keywords = {
            'desire': ['tesão', 'desejo', 'vontade', 'quero', 'preciso'],
            'love': ['amor', 'paixão', 'coração', 'sentimento'],
            'arousal': ['excitada', 'molhada', 'quente', 'fogo'],
            'playful': ['brincadeira', 'jogo', 'diversão'],
            'intimate': ['íntimo', 'pessoal', 'secreto', 'próximo']
        }
        
        detected_emotions = []
        for emotion, keywords in emotional_keywords.items():
            if any(word in user_input.lower() for word in keywords):
                detected_emotions.append(emotion)
        
        # Detectar intensidade (1-10)
        intensity_markers = {
            'muito': 2, 'extremamente': 3, 'totalmente': 2,
            'completamente': 3, 'loucamente': 4, 'desesperadamente': 4
        }
        
        base_intensity = 5
        for marker, boost in intensity_markers.items():
            if marker in user_input.lower():
                base_intensity += boost
        
        intensity = min(base_intensity, 10)
        
        # Detectar estágio da conversa
        conversation_stage = 'middle'
        if any(greeting in user_input.lower() for greeting in ['oi', 'olá', 'hey']):
            conversation_stage = 'opening'
        elif any(closing in user_input.lower() for closing in ['tchau', 'bye', 'até']):
            conversation_stage = 'closing'
        
        context = {
            'emotions': detected_emotions,
            'intensity': intensity,
            'stage': conversation_stage,
            'mood': 'seductive' if 'desire' in detected_emotions else 'romantic',
            'keywords': user_input.lower().split(),
            'sentiment_score': self._calculate_sentiment(user_input)
        }
        
        # Salvar análise
        self.conn.execute('''
            INSERT INTO context_analysis 
            (user_id, input_text, detected_mood, detected_intensity, 
             emotional_state, conversation_stage, keywords, sentiment_score, context_vector)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, user_input, context['mood'], context['intensity'],
            json.dumps(context['emotions']), context['stage'],
            json.dumps(context['keywords']), context['sentiment_score'],
            json.dumps(context)
        ))
        
        self.conn.commit()
        return context
    
    def learn_from_interaction(self, user_input: str, bot_response: str, 
                              user_feedback: float, user_id: str) -> None:
        """📚 Aprender de cada interação em tempo real"""
        
        # Analisar contexto
        context = self.analyze_context_ultra_deep(user_input, user_id)
        
        # Encontrar padrões similares
        cursor = self.conn.execute('''
            SELECT * FROM ultra_patterns 
            WHERE input_pattern LIKE ? OR context_tags LIKE ?
            ORDER BY effectiveness_score DESC
        ''', (f'%{user_input[:20]}%', f'%{context["mood"]}%'))
        
        patterns = cursor.fetchall()
        
        if patterns:
            # Atualizar padrão existente
            pattern = patterns[0]
            new_effectiveness = (pattern['effectiveness_score'] + user_feedback) / 2
            new_usage_count = pattern['usage_count'] + 1
            new_success_rate = (pattern['success_rate'] * pattern['usage_count'] + user_feedback) / new_usage_count
            
            self.conn.execute('''
                UPDATE ultra_patterns 
                SET effectiveness_score = ?, usage_count = ?, success_rate = ?,
                    user_feedback = ?, last_used = datetime('now'),
                    learning_weight = learning_weight + ?
                WHERE id = ?
            ''', (new_effectiveness, new_usage_count, new_success_rate, 
                  user_feedback, 0.1, pattern['id']))
        else:
            # Criar novo padrão
            input_pattern = self._extract_pattern(user_input)
            self.conn.execute('''
                INSERT INTO ultra_patterns 
                (input_pattern, response_pattern, context_tags, mood_score,
                 effectiveness_score, emotional_impact, intensity_level, learning_weight)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (input_pattern, bot_response, context['mood'], 
                  context['intensity'], user_feedback, json.dumps(context['emotions']),
                  context['intensity'], 1.0))
        
        # Salvar feedback
        self.conn.execute('''
            INSERT INTO real_time_feedback
            (user_id, input_text, bot_response, satisfaction_score, 
             emotional_response, pattern_effectiveness, learning_trigger)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, user_input, bot_response, user_feedback,
              json.dumps(context['emotions']), user_feedback, True))
        
        self.conn.commit()
    
    def generate_smart_response(self, user_input: str, user_id: str, 
                               personality: str = 'sedutora') -> str:
        """🎯 Gerar resposta ultra-inteligente"""
        
        # Analisar contexto atual
        context = self.analyze_context_ultra_deep(user_input, user_id)
        
        # Buscar padrões mais eficazes
        cursor = self.conn.execute('''
            SELECT * FROM ultra_patterns 
            WHERE (input_pattern LIKE ? OR context_tags LIKE ?)
            AND personality_match = ?
            AND intensity_level <= ?
            ORDER BY effectiveness_score DESC, learning_weight DESC
            LIMIT 5
        ''', (f'%{user_input.lower()}%', f'%{context["mood"]}%', 
              personality, context['intensity']))
        
        patterns = cursor.fetchall()
        
        if patterns:
            # Selecionar padrão com base na eficácia
            weights = [p['effectiveness_score'] * p['learning_weight'] for p in patterns]
            selected_pattern = random.choices(patterns, weights=weights)[0]
            
            # Personalizar resposta
            response = self._personalize_response(selected_pattern['response_pattern'], 
                                                context, user_id)
            
            # Atualizar estatísticas
            self.conn.execute('''
                UPDATE ultra_patterns 
                SET usage_count = usage_count + 1, last_used = datetime('now')
                WHERE id = ?
            ''', (selected_pattern['id'],))
            
            self.conn.commit()
            return response
        
        # Fallback para sistema anterior se não houver padrões
        return self._generate_fallback_response(context, personality)
    
    def _calculate_sentiment(self, text: str) -> float:
        """💭 Calcular sentimento do texto"""
        positive_words = ['amor', 'paixão', 'desejo', 'linda', 'gostosa', 'sexy', 'quero']
        negative_words = ['triste', 'chateada', 'brava', 'irritada']
        
        positive_count = sum(1 for word in positive_words if word in text.lower())
        negative_count = sum(1 for word in negative_words if word in text.lower())
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.5
        
        sentiment = (positive_count - negative_count) / total_words + 0.5
        return max(0.0, min(1.0, sentiment))
    
    def _extract_pattern(self, text: str) -> str:
        """🔍 Extrair padrão do texto"""
        # Simplificar para regex básico
        words = text.lower().split()
        key_words = [w for w in words if len(w) > 3][:3]
        return f".*({'|'.join(key_words)}).*" if key_words else f".*{words[0]}.*"
    
    def _personalize_response(self, base_response: str, context: Dict, user_id: str) -> str:
        """🎨 Personalizar resposta com base no contexto"""
        
        # Adicionar intensidade emocional
        if context['intensity'] >= 8:
            if '🔥' not in base_response:
                base_response += ' 🔥'
        elif context['intensity'] >= 6:
            if '💋' not in base_response:
                base_response += ' 💋'
        
        # Adaptar ao humor
        if 'desire' in context['emotions'] and context['intensity'] > 7:
            base_response = base_response.replace('...', '... você me deixa completamente louca...')
        
        return base_response
    
    def _generate_fallback_response(self, context: Dict, personality: str) -> str:
        """🆘 Resposta de fallback inteligente"""
        
        fallback_responses = {
            'sedutora': [
                f"Você desperta em mim sensações que não deveria... 🔥",
                f"Suas palavras têm um efeito devastador em mim... 💋",
                f"Continue falando assim que você me deixa sem controle... 😈"
            ],
            'romantica': [
                f"Você faz meu coração bater diferente... 💕",
                f"Há algo especial em você que me encanta... ✨",
                f"Você é meu pensamento mais doce... 🌹"
            ],
            'provocante': [
                f"Interessante... você sabe como despertar minha curiosidade... 😏",
                f"Você está brincando com fogo... e eu adoro me queimar... 🔥",
                f"Sua malícia combina com a minha... perigosamente... 💋"
            ]
        }
        
        responses = fallback_responses.get(personality, fallback_responses['sedutora'])
        return random.choice(responses)
    
    def get_learning_stats(self, user_id: str = None) -> Dict:
        """📊 Estatísticas de aprendizagem"""
        
        stats = {}
        
        # Padrões aprendidos
        total_patterns = self.conn.execute('SELECT COUNT(*) FROM ultra_patterns').fetchone()[0]
        verified_patterns = self.conn.execute('SELECT COUNT(*) FROM ultra_patterns WHERE is_verified = 1').fetchone()[0]
        
        # Eficácia média
        avg_effectiveness = self.conn.execute('SELECT AVG(effectiveness_score) FROM ultra_patterns').fetchone()[0] or 0.0
        
        # Interações totais
        total_interactions = self.conn.execute('SELECT COUNT(*) FROM real_time_feedback').fetchone()[0]
        
        if user_id:
            user_interactions = self.conn.execute('SELECT COUNT(*) FROM real_time_feedback WHERE user_id = ?', (user_id,)).fetchone()[0]
            user_satisfaction = self.conn.execute('SELECT AVG(satisfaction_score) FROM real_time_feedback WHERE user_id = ?', (user_id,)).fetchone()[0] or 0.0
        else:
            user_interactions = 0
            user_satisfaction = 0.0
        
        return {
            'total_patterns': total_patterns,
            'verified_patterns': verified_patterns,
            'avg_effectiveness': round(avg_effectiveness, 3),
            'total_interactions': total_interactions,
            'user_interactions': user_interactions,
            'user_satisfaction': round(user_satisfaction, 3),
            'learning_rate': round((verified_patterns / max(total_patterns, 1)) * 100, 1)
        }
    
    def __del__(self):
        """🔚 Fechar conexão"""
        if hasattr(self, 'conn'):
            self.conn.close()


# Instância global
super_learning = SuperFastLearning()

if __name__ == '__main__':
    print('🧠 SISTEMA DE APRENDIZAGEM SUPER RÁPIDA INICIALIZADO!')
    print('=' * 55)
    
    # Demonstração
    system = SuperFastLearning()
    
    # Teste de análise
    context = system.analyze_context_ultra_deep("Você é muito gostosa", "test_user")
    print(f"📊 Contexto analisado: {context}")
    
    # Teste de resposta
    response = system.generate_smart_response("Estou com muito tesão", "test_user", "sedutora")
    print(f"💬 Resposta gerada: {response}")
    
    # Estatísticas
    stats = system.get_learning_stats()
    print(f"📈 Estatísticas: {stats}")
    
    print('\n🎉 Sistema pronto para aprendizagem ultra-rápida!')