"""
Sistema de Adaptação
Especializado em adaptar comportamento e respostas baseado no aprendizado
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import sqlite3

class AdaptationSystem:
    """Sistema de adaptação comportamental baseado em aprendizado"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'memoria', 'adaptation_system.db')
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
        
        # Parâmetros de adaptação
        self.adaptation_config = {
            'response_style_weight': 0.3,
            'topic_preference_weight': 0.4,
            'interaction_pattern_weight': 0.3,
            'minimum_samples': 5,
            'adaptation_threshold': 0.6
        }
    
    def create_tables(self):
        """Criar tabelas do sistema de adaptação"""
        with self.conn:
            # Perfis adaptativos por usuário
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS user_adaptations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    adaptation_type TEXT NOT NULL,
                    adaptation_data TEXT NOT NULL,
                    confidence_score REAL DEFAULT 0.0,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    samples_count INTEGER DEFAULT 1,
                    UNIQUE(user_id, adaptation_type)
                )
            ''')
            
            # Histórico de adaptações aplicadas
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS adaptation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    adaptation_applied TEXT NOT NULL,
                    context_data TEXT,
                    effectiveness_score REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Regras de adaptação personalizadas
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS adaptation_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    rule_name TEXT NOT NULL,
                    rule_conditions TEXT NOT NULL,
                    rule_actions TEXT NOT NULL,
                    rule_priority INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def analyze_user_patterns(self, user_id: str, interaction_history: List[Dict]) -> Dict:
        """Analisar padrões do usuário para adaptação"""
        patterns = {
            'response_style_preferences': {},
            'topic_interests': {},
            'interaction_timing': {},
            'communication_style': {},
            'complexity_preference': {}
        }
        
        if not interaction_history:
            return patterns
        
        try:
            # Analisar preferências de estilo de resposta
            patterns['response_style_preferences'] = self._analyze_response_style_preferences(
                interaction_history
            )
            
            # Analisar interesses por tópico
            patterns['topic_interests'] = self._analyze_topic_interests(interaction_history)
            
            # Analisar padrões de timing
            patterns['interaction_timing'] = self._analyze_interaction_timing(interaction_history)
            
            # Analisar estilo de comunicação
            patterns['communication_style'] = self._analyze_communication_style(interaction_history)
            
            # Analisar preferência de complexidade
            patterns['complexity_preference'] = self._analyze_complexity_preference(interaction_history)
            
            return patterns
        
        except Exception as e:
            print(f"Erro ao analisar padrões do usuário: {e}")
            return patterns
    
    def _analyze_response_style_preferences(self, history: List[Dict]) -> Dict:
        """Analisar preferências de estilo de resposta"""
        style_scores = {
            'formal': 0,
            'casual': 0,
            'enthusiastic': 0,
            'technical': 0,
            'explanatory': 0
        }
        
        positive_interactions = [h for h in history if h.get('feedback') == 'positive']
        
        for interaction in positive_interactions:
            response = interaction.get('bot_response', '')
            
            # Detectar formalidade
            if any(word in response.lower() for word in ['senhor', 'senhora', 'cordialmente']):
                style_scores['formal'] += 1
            elif any(word in response.lower() for word in ['cara', 'mano', 'beleza']):
                style_scores['casual'] += 1
            
            # Detectar entusiasmo
            emoji_count = len([c for c in response if c in '😊😄✨🎉👍'])
            exclamation_count = response.count('!')
            if emoji_count > 2 or exclamation_count > 2:
                style_scores['enthusiastic'] += 1
            
            # Detectar tecnicismo
            if any(term in response.lower() for term in ['algoritmo', 'implementação', 'framework']):
                style_scores['technical'] += 1
            
            # Detectar explicação detalhada
            if len(response) > 200 and ('porque' in response.lower() or 'exemplo' in response.lower()):
                style_scores['explanatory'] += 1
        
        # Normalizar scores
        total_interactions = len(positive_interactions) if positive_interactions else 1
        return {style: score/total_interactions for style, score in style_scores.items()}
    
    def _analyze_topic_interests(self, history: List[Dict]) -> Dict:
        """Analisar interesses por tópico"""
        topic_keywords = {
            'tecnologia': ['python', 'programação', 'código', 'software', 'algoritmo'],
            'negócios': ['empresa', 'mercado', 'vendas', 'cliente', 'estratégia'],
            'ciência': ['pesquisa', 'dados', 'análise', 'experimento', 'método'],
            'educação': ['aprender', 'ensinar', 'curso', 'estudo', 'conhecimento'],
            'entretenimento': ['filme', 'música', 'jogo', 'diversão', 'hobby']
        }
        
        topic_scores = {topic: 0 for topic in topic_keywords.keys()}
        positive_interactions = [h for h in history if h.get('feedback') == 'positive']
        
        for interaction in positive_interactions:
            message = interaction.get('user_message', '').lower()
            
            for topic, keywords in topic_keywords.items():
                for keyword in keywords:
                    if keyword in message:
                        topic_scores[topic] += 1
                        break
        
        total_positive = len(positive_interactions) if positive_interactions else 1
        return {topic: score/total_positive for topic, score in topic_scores.items()}
    
    def _analyze_interaction_timing(self, history: List[Dict]) -> Dict:
        """Analisar padrões de timing de interação"""
        timing_data = {
            'preferred_hours': [],
            'session_duration_preference': 'medium',
            'response_time_sensitivity': 'normal'
        }
        
        try:
            # Extrair horários das interações
            hours = []
            for interaction in history:
                timestamp_str = interaction.get('timestamp')
                if timestamp_str:
                    try:
                        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        hours.append(dt.hour)
                    except:
                        continue
            
            if hours:
                # Encontrar horários mais comuns
                hour_counts = {}
                for hour in hours:
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
                
                # Top 3 horários preferenciais
                timing_data['preferred_hours'] = sorted(
                    hour_counts.keys(), 
                    key=lambda h: hour_counts[h], 
                    reverse=True
                )[:3]
        
        except Exception as e:
            print(f"Erro ao analisar timing: {e}")
        
        return timing_data
    
    def _analyze_communication_style(self, history: List[Dict]) -> Dict:
        """Analisar estilo de comunicação do usuário"""
        style_indicators = {
            'message_length_preference': 'medium',
            'question_complexity': 'medium',
            'emoji_usage': 'low',
            'politeness_level': 'medium'
        }
        
        try:
            user_messages = [h.get('user_message', '') for h in history]
            if not user_messages:
                return style_indicators
            
            # Analisar comprimento médio das mensagens
            avg_length = sum(len(msg) for msg in user_messages) / len(user_messages)
            if avg_length > 100:
                style_indicators['message_length_preference'] = 'long'
            elif avg_length < 30:
                style_indicators['message_length_preference'] = 'short'
            
            # Analisar uso de emojis
            total_emojis = sum(len([c for c in msg if ord(c) > 127]) for msg in user_messages)
            emoji_ratio = total_emojis / len(user_messages)
            if emoji_ratio > 2:
                style_indicators['emoji_usage'] = 'high'
            elif emoji_ratio > 0.5:
                style_indicators['emoji_usage'] = 'medium'
            
            # Analisar polidez
            polite_words = ['por favor', 'obrigado', 'obrigada', 'desculpe', 'com licença']
            polite_count = sum(
                sum(word in msg.lower() for word in polite_words) 
                for msg in user_messages
            )
            
            if polite_count / len(user_messages) > 0.3:
                style_indicators['politeness_level'] = 'high'
        
        except Exception as e:
            print(f"Erro ao analisar estilo de comunicação: {e}")
        
        return style_indicators
    
    def _analyze_complexity_preference(self, history: List[Dict]) -> Dict:
        """Analisar preferência de complexidade nas respostas"""
        complexity_data = {
            'technical_depth': 'medium',
            'example_preference': 'yes',
            'step_by_step': 'yes'
        }
        
        try:
            positive_responses = [
                h.get('bot_response', '') for h in history 
                if h.get('feedback') == 'positive'
            ]
            
            if not positive_responses:
                return complexity_data
            
            # Analisar profundidade técnica
            technical_terms = ['implementar', 'configurar', 'algoritmo', 'estrutura']
            avg_technical_density = sum(
                sum(term in resp.lower() for term in technical_terms)
                for resp in positive_responses
            ) / len(positive_responses)
            
            if avg_technical_density > 1:
                complexity_data['technical_depth'] = 'high'
            elif avg_technical_density < 0.3:
                complexity_data['technical_depth'] = 'low'
            
            # Analisar preferência por exemplos
            example_indicators = ['exemplo', 'por exemplo', 'como:', 'veja:']
            example_ratio = sum(
                any(indicator in resp.lower() for indicator in example_indicators)
                for resp in positive_responses
            ) / len(positive_responses)
            
            complexity_data['example_preference'] = 'yes' if example_ratio > 0.4 else 'moderate'
        
        except Exception as e:
            print(f"Erro ao analisar preferência de complexidade: {e}")
        
        return complexity_data
    
    def create_adaptation_profile(self, user_id: str, patterns: Dict) -> Dict:
        """Criar perfil de adaptação baseado nos padrões"""
        adaptation_profile = {
            'response_style': self._determine_optimal_style(patterns),
            'content_strategy': self._determine_content_strategy(patterns),
            'interaction_approach': self._determine_interaction_approach(patterns),
            'personalization_level': 'high'
        }
        
        # Salvar adaptações no banco
        for adaptation_type, adaptation_data in adaptation_profile.items():
            self.save_user_adaptation(user_id, adaptation_type, adaptation_data)
        
        return adaptation_profile
    
    def _determine_optimal_style(self, patterns: Dict) -> Dict:
        """Determinar estilo ótimo baseado nos padrões"""
        style_prefs = patterns.get('response_style_preferences', {})
        comm_style = patterns.get('communication_style', {})
        
        # Determinar formalidade
        formality = 'casual'
        if style_prefs.get('formal', 0) > 0.3:
            formality = 'formal'
        elif comm_style.get('politeness_level') == 'high':
            formality = 'semi-formal'
        
        # Determinar entusiasmo
        enthusiasm = 'moderate'
        if style_prefs.get('enthusiastic', 0) > 0.4:
            enthusiasm = 'high'
        elif comm_style.get('emoji_usage') == 'low':
            enthusiasm = 'low'
        
        return {
            'formality': formality,
            'enthusiasm': enthusiasm,
            'technical_level': 'medium' if style_prefs.get('technical', 0) > 0.3 else 'low'
        }
    
    def _determine_content_strategy(self, patterns: Dict) -> Dict:
        """Determinar estratégia de conteúdo"""
        complexity_prefs = patterns.get('complexity_preference', {})
        topic_interests = patterns.get('topic_interests', {})
        
        # Tópicos preferidos
        preferred_topics = [
            topic for topic, score in topic_interests.items() 
            if score > 0.2
        ]
        
        return {
            'preferred_topics': preferred_topics,
            'explanation_depth': complexity_prefs.get('technical_depth', 'medium'),
            'use_examples': complexity_prefs.get('example_preference', 'yes'),
            'structured_responses': complexity_prefs.get('step_by_step', 'yes')
        }
    
    def _determine_interaction_approach(self, patterns: Dict) -> Dict:
        """Determinar abordagem de interação"""
        timing = patterns.get('interaction_timing', {})
        comm_style = patterns.get('communication_style', {})
        
        return {
            'preferred_hours': timing.get('preferred_hours', []),
            'response_length_preference': comm_style.get('message_length_preference', 'medium'),
            'emoji_usage_level': comm_style.get('emoji_usage', 'low')
        }
    
    def save_user_adaptation(self, user_id: str, adaptation_type: str, adaptation_data: Any, 
                           confidence_score: float = 0.7):
        """Salvar adaptação do usuário"""
        try:
            adaptation_json = json.dumps(adaptation_data)
            
            with self.conn:
                self.conn.execute('''
                    INSERT OR REPLACE INTO user_adaptations
                    (user_id, adaptation_type, adaptation_data, confidence_score, samples_count)
                    VALUES (?, ?, ?, ?, COALESCE((SELECT samples_count + 1 FROM user_adaptations 
                            WHERE user_id = ? AND adaptation_type = ?), 1))
                ''', (user_id, adaptation_type, adaptation_json, confidence_score, user_id, adaptation_type))
        
        except Exception as e:
            print(f"Erro ao salvar adaptação: {e}")
    
    def get_user_adaptations(self, user_id: str) -> Dict:
        """Obter adaptações do usuário"""
        try:
            cursor = self.conn.execute('''
                SELECT adaptation_type, adaptation_data, confidence_score, samples_count
                FROM user_adaptations
                WHERE user_id = ?
            ''', (user_id,))
            
            adaptations = {}
            for row in cursor.fetchall():
                adaptation_type = row[0]
                adaptation_data = json.loads(row[1])
                confidence_score = row[2]
                samples_count = row[3]
                
                adaptations[adaptation_type] = {
                    'data': adaptation_data,
                    'confidence': confidence_score,
                    'samples': samples_count
                }
            
            return adaptations
        
        except Exception as e:
            print(f"Erro ao obter adaptações: {e}")
            return {}
    
    def apply_adaptations(self, user_id: str, base_response: str, context: Dict) -> str:
        """Aplicar adaptações a uma resposta"""
        try:
            adaptations = self.get_user_adaptations(user_id)
            if not adaptations:
                return base_response
            
            adapted_response = base_response
            
            # Aplicar adaptações de estilo
            if 'response_style' in adaptations:
                style_data = adaptations['response_style']['data']
                adapted_response = self._apply_style_adaptation(adapted_response, style_data)
            
            # Aplicar adaptações de conteúdo
            if 'content_strategy' in adaptations:
                content_data = adaptations['content_strategy']['data']
                adapted_response = self._apply_content_adaptation(adapted_response, content_data, context)
            
            # Aplicar adaptações de interação
            if 'interaction_approach' in adaptations:
                interaction_data = adaptations['interaction_approach']['data']
                adapted_response = self._apply_interaction_adaptation(adapted_response, interaction_data)
            
            # Registrar aplicação
            self._log_adaptation_application(user_id, adaptations, context)
            
            return adapted_response
        
        except Exception as e:
            print(f"Erro ao aplicar adaptações: {e}")
            return base_response
    
    def _apply_style_adaptation(self, response: str, style_data: Dict) -> str:
        """Aplicar adaptações de estilo"""
        try:
            adapted_response = response
            
            # Ajustar formalidade
            formality = style_data.get('formality', 'casual')
            if formality == 'formal':
                # Tornar mais formal
                adapted_response = adapted_response.replace(' você ', ' o senhor/senhora ')
                adapted_response = adapted_response.replace('Oi', 'Olá')
                adapted_response = adapted_response.replace('tchau', 'até logo')
            elif formality == 'casual':
                # Tornar mais casual
                adapted_response = adapted_response.replace('senhor/senhora', 'você')
                adapted_response = adapted_response.replace('Olá', 'Oi')
            
            # Ajustar entusiasmo
            enthusiasm = style_data.get('enthusiasm', 'moderate')
            if enthusiasm == 'high':
                if not any(emoji in adapted_response for emoji in ['😊', '✨', '🎉']):
                    adapted_response += ' 😊'
                if '!' not in adapted_response:
                    adapted_response = adapted_response.rstrip('.') + '!'
            elif enthusiasm == 'low':
                # Remover emojis e exclamações excessivas
                for emoji in ['😊', '✨', '🎉', '👍']:
                    adapted_response = adapted_response.replace(emoji, '')
                adapted_response = adapted_response.replace('!!', '.')
            
            return adapted_response
        
        except Exception as e:
            print(f"Erro ao aplicar adaptação de estilo: {e}")
            return response
    
    def _apply_content_adaptation(self, response: str, content_data: Dict, context: Dict) -> str:
        """Aplicar adaptações de conteúdo"""
        try:
            adapted_response = response
            
            # Ajustar profundidade de explicação
            explanation_depth = content_data.get('explanation_depth', 'medium')
            if explanation_depth == 'high' and len(response) < 200:
                adapted_response += "\n\nPara mais detalhes técnicos, posso explicar os conceitos mais profundamente se desejar."
            elif explanation_depth == 'low' and len(response) > 300:
                # Tentar resumir (simplificado)
                sentences = adapted_response.split('.')
                if len(sentences) > 3:
                    adapted_response = '. '.join(sentences[:2]) + '.'
            
            # Adicionar exemplos se preferido
            use_examples = content_data.get('use_examples', 'yes')
            if use_examples == 'yes' and 'exemplo' not in response.lower():
                topic = context.get('topic', 'geral')
                adapted_response += f"\n\nPor exemplo, no contexto de {topic}, isso seria aplicado de forma prática."
            
            return adapted_response
        
        except Exception as e:
            print(f"Erro ao aplicar adaptação de conteúdo: {e}")
            return response
    
    def _apply_interaction_adaptation(self, response: str, interaction_data: Dict) -> str:
        """Aplicar adaptações de interação"""
        try:
            adapted_response = response
            
            # Ajustar comprimento da resposta
            length_pref = interaction_data.get('response_length_preference', 'medium')
            if length_pref == 'short' and len(response) > 150:
                # Simplificar resposta
                main_points = response.split('\n')[0]  # Pegar primeiro parágrafo
                adapted_response = main_points + "\n\nPosso detalhar mais se necessário."
            elif length_pref == 'long' and len(response) < 100:
                adapted_response += "\n\nEsse tópico tem várias nuances interessantes que posso explorar mais."
            
            # Ajustar uso de emoji
            emoji_level = interaction_data.get('emoji_usage_level', 'low')
            if emoji_level == 'high':
                if not any(c in response for c in '😊✨👍'):
                    adapted_response += ' ✨'
            
            return adapted_response
        
        except Exception as e:
            print(f"Erro ao aplicar adaptação de interação: {e}")
            return response
    
    def _log_adaptation_application(self, user_id: str, adaptations: Dict, context: Dict):
        """Registrar aplicação de adaptação"""
        try:
            applied_adaptations = list(adaptations.keys())
            
            with self.conn:
                self.conn.execute('''
                    INSERT INTO adaptation_history
                    (user_id, adaptation_applied, context_data)
                    VALUES (?, ?, ?)
                ''', (user_id, json.dumps(applied_adaptations), json.dumps(context)))
        
        except Exception as e:
            print(f"Erro ao registrar aplicação de adaptação: {e}")
    
    def update_adaptation_effectiveness(self, user_id: str, feedback_score: float):
        """Atualizar efetividade das adaptações baseado no feedback"""
        try:
            # Obter última aplicação de adaptação
            cursor = self.conn.execute('''
                SELECT id, adaptation_applied FROM adaptation_history
                WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1
            ''', (user_id,))
            
            last_application = cursor.fetchone()
            if not last_application:
                return
            
            # Atualizar score de efetividade
            with self.conn:
                self.conn.execute('''
                    UPDATE adaptation_history
                    SET effectiveness_score = ?
                    WHERE id = ?
                ''', (feedback_score, last_application[0]))
            
            # Atualizar confiança das adaptações baseado na efetividade
            applied_adaptations = json.loads(last_application[1])
            for adaptation_type in applied_adaptations:
                self._update_adaptation_confidence(user_id, adaptation_type, feedback_score)
        
        except Exception as e:
            print(f"Erro ao atualizar efetividade: {e}")
    
    def _update_adaptation_confidence(self, user_id: str, adaptation_type: str, feedback_score: float):
        """Atualizar confiança de uma adaptação específica"""
        try:
            # Obter confiança atual
            cursor = self.conn.execute('''
                SELECT confidence_score, samples_count FROM user_adaptations
                WHERE user_id = ? AND adaptation_type = ?
            ''', (user_id, adaptation_type))
            
            current = cursor.fetchone()
            if not current:
                return
            
            current_confidence = current[0]
            samples_count = current[1]
            
            # Calcular nova confiança (média ponderada)
            feedback_weight = 0.2  # Peso do feedback atual
            new_confidence = (current_confidence * (1 - feedback_weight)) + (feedback_score * feedback_weight)
            
            # Atualizar no banco
            with self.conn:
                self.conn.execute('''
                    UPDATE user_adaptations
                    SET confidence_score = ?
                    WHERE user_id = ? AND adaptation_type = ?
                ''', (new_confidence, user_id, adaptation_type))
        
        except Exception as e:
            print(f"Erro ao atualizar confiança da adaptação: {e}")
    
    def get_adaptation_report(self, user_id: str) -> Dict:
        """Obter relatório de adaptações do usuário"""
        try:
            adaptations = self.get_user_adaptations(user_id)
            
            # Calcular efetividade média
            cursor = self.conn.execute('''
                SELECT AVG(effectiveness_score) FROM adaptation_history
                WHERE user_id = ? AND effectiveness_score IS NOT NULL
            ''', (user_id,))
            
            avg_effectiveness = cursor.fetchone()[0] or 0
            
            # Contar aplicações recentes
            cursor = self.conn.execute('''
                SELECT COUNT(*) FROM adaptation_history
                WHERE user_id = ? AND timestamp >= ?
            ''', (user_id, (datetime.now() - timedelta(days=7)).isoformat()))
            
            recent_applications = cursor.fetchone()[0]
            
            return {
                'user_id': user_id,
                'active_adaptations': adaptations,
                'average_effectiveness': avg_effectiveness,
                'recent_applications': recent_applications,
                'adaptation_confidence': sum(
                    a['confidence'] for a in adaptations.values()
                ) / len(adaptations) if adaptations else 0,
                'report_timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"Erro ao gerar relatório de adaptação: {e}")
            return {
                'error': str(e),
                'report_timestamp': datetime.now().isoformat()
            }