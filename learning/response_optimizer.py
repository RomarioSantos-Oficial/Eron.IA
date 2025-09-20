"""
Sistema Otimizador de Respostas
Especializado em otimizar respostas baseado no feedback e padrões do usuário
"""
import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class ResponseOptimizer:
    """Sistema para otimizar respostas da IA baseado em feedback e padrões"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'memoria', 'response_optimizer.db')
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        """Criar tabelas para otimização de respostas"""
        with self.conn:
            # Tabela de templates de resposta otimizados
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS response_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    question_type TEXT NOT NULL,
                    template TEXT NOT NULL,
                    success_rate REAL DEFAULT 0.5,
                    usage_count INTEGER DEFAULT 0,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                    avg_feedback_score REAL DEFAULT 0.0
                )
            ''')
            
            # Tabela de estratégias de resposta
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS response_strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    context_type TEXT NOT NULL,
                    strategy_name TEXT NOT NULL,
                    strategy_params TEXT NOT NULL,
                    effectiveness REAL DEFAULT 0.5,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de análise de feedback
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS feedback_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    response_features TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    feedback_score REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def analyze_response_effectiveness(self, user_id: str, question: str, response: str, 
                                     feedback_type: str, feedback_score: float = None) -> Dict:
        """Analisar efetividade de uma resposta baseada no feedback"""
        
        # Extrair características da resposta
        response_features = self._extract_response_features(response)
        
        # Categorizar tipo de pergunta
        question_type = self._categorize_question(question)
        
        # Converter feedback para score numérico
        if feedback_score is None:
            feedback_score = 1.0 if feedback_type == 'positive' else -1.0
        
        # Salvar análise
        self._save_feedback_analysis(user_id, question_type, response_features, 
                                   feedback_type, feedback_score)
        
        # Atualizar estratégias baseadas no feedback
        self._update_strategies(user_id, question_type, response_features, feedback_score)
        
        return {
            'question_type': question_type,
            'response_features': response_features,
            'feedback_score': feedback_score,
            'recommendations': self._generate_recommendations(user_id, question_type, feedback_score)
        }
    
    def _extract_response_features(self, response: str) -> Dict:
        """Extrair características da resposta"""
        features = {}
        
        # Comprimento
        length = len(response)
        features['length_category'] = self._categorize_length(length)
        features['word_count'] = len(response.split())
        
        # Estrutura
        features['has_lists'] = '•' in response or '-' in response or any(f'{i}.' in response for i in range(1, 10))
        features['has_headers'] = any(line.startswith('**') for line in response.split('\n'))
        features['paragraph_count'] = response.count('\n\n') + 1
        
        # Linguagem
        features['emoji_count'] = sum(1 for char in response if ord(char) > 127)
        features['question_count'] = response.count('?')
        features['exclamation_count'] = response.count('!')
        
        # Tom
        features['formality'] = self._assess_formality(response)
        features['enthusiasm'] = self._assess_enthusiasm(response)
        
        # Conteúdo
        features['has_examples'] = any(word in response.lower() for word in ['exemplo', 'por exemplo', 'como'])
        features['has_explanation'] = any(word in response.lower() for word in ['porque', 'pois', 'isso acontece'])
        features['has_instructions'] = any(word in response.lower() for word in ['primeiro', 'segundo', 'passo', 'faça'])
        
        return features
    
    def _categorize_question(self, question: str) -> str:
        """Categorizar tipo de pergunta"""
        question_lower = question.lower()
        
        # Palavras-chave para diferentes tipos
        how_keywords = ['como', 'de que forma', 'de que maneira']
        what_keywords = ['o que', 'que', 'qual']
        why_keywords = ['por que', 'porque', 'por qual motivo']
        when_keywords = ['quando', 'que horas', 'em que momento']
        where_keywords = ['onde', 'em que lugar', 'aonde']
        help_keywords = ['ajuda', 'socorro', 'problema', 'não consigo']
        
        if any(keyword in question_lower for keyword in help_keywords):
            return 'help_request'
        elif any(keyword in question_lower for keyword in how_keywords):
            return 'how_to'
        elif any(keyword in question_lower for keyword in what_keywords):
            return 'what_is'
        elif any(keyword in question_lower for keyword in why_keywords):
            return 'why_explanation'
        elif any(keyword in question_lower for keyword in when_keywords):
            return 'when_timing'
        elif any(keyword in question_lower for keyword in where_keywords):
            return 'where_location'
        elif '?' in question:
            return 'general_question'
        else:
            return 'statement_or_comment'
    
    def _categorize_length(self, length: int) -> str:
        """Categorizar comprimento da resposta"""
        if length < 50:
            return 'very_short'
        elif length < 150:
            return 'short'
        elif length < 400:
            return 'medium'
        elif length < 800:
            return 'long'
        else:
            return 'very_long'
    
    def _assess_formality(self, text: str) -> str:
        """Avaliar formalidade do texto"""
        formal_indicators = ['você', 'senhor', 'senhora', 'gostaria', 'poderia', 'por favor']
        informal_indicators = ['vc', 'tu', 'oi', 'opa', 'beleza', 'cara', 'mano']
        
        formal_score = sum(1 for word in formal_indicators if word in text.lower())
        informal_score = sum(1 for word in informal_indicators if word in text.lower())
        
        if formal_score > informal_score:
            return 'formal'
        elif informal_score > formal_score:
            return 'informal'
        else:
            return 'neutral'
    
    def _assess_enthusiasm(self, text: str) -> str:
        """Avaliar entusiasmo do texto"""
        enthusiasm_indicators = ['!', '😊', '🎉', '👍', '✨', 'ótimo', 'excelente', 'incrível']
        count = sum(1 for indicator in enthusiasm_indicators if indicator in text)
        
        if count > 3:
            return 'high'
        elif count > 0:
            return 'medium'
        else:
            return 'low'
    
    def _save_feedback_analysis(self, user_id: str, question_type: str, response_features: Dict,
                               feedback_type: str, feedback_score: float):
        """Salvar análise de feedback"""
        try:
            with self.conn:
                self.conn.execute('''
                    INSERT INTO feedback_analysis
                    (user_id, message_type, response_features, feedback_type, feedback_score)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, question_type, json.dumps(response_features), feedback_type, feedback_score))
        except Exception as e:
            print(f"Erro ao salvar análise de feedback: {e}")
    
    def _update_strategies(self, user_id: str, question_type: str, response_features: Dict, feedback_score: float):
        """Atualizar estratégias baseadas no feedback"""
        try:
            with self.conn:
                # Para cada característica da resposta, ajustar estratégia
                for feature, value in response_features.items():
                    # Verificar se estratégia existe
                    cursor = self.conn.execute('''
                        SELECT id, effectiveness, strategy_params FROM response_strategies
                        WHERE user_id = ? AND context_type = ? AND strategy_name = ?
                    ''', (user_id, question_type, feature))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Atualizar efetividade
                        old_effectiveness = existing[1]
                        new_effectiveness = old_effectiveness + (feedback_score * 0.1)
                        new_effectiveness = max(-1.0, min(1.0, new_effectiveness))
                        
                        self.conn.execute('''
                            UPDATE response_strategies
                            SET effectiveness = ?, last_updated = CURRENT_TIMESTAMP
                            WHERE id = ?
                        ''', (new_effectiveness, existing[0]))
                    else:
                        # Criar nova estratégia
                        strategy_params = json.dumps({'preferred_value': value, 'confidence': 0.3})
                        self.conn.execute('''
                            INSERT INTO response_strategies
                            (user_id, context_type, strategy_name, strategy_params, effectiveness)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (user_id, question_type, feature, strategy_params, feedback_score * 0.5))
        
        except Exception as e:
            print(f"Erro ao atualizar estratégias: {e}")
    
    def _generate_recommendations(self, user_id: str, question_type: str, feedback_score: float) -> List[str]:
        """Gerar recomendações de otimização"""
        recommendations = []
        
        try:
            # Analisar padrões de feedback anteriores
            cursor = self.conn.execute('''
                SELECT response_features, feedback_score FROM feedback_analysis
                WHERE user_id = ? AND message_type = ?
                ORDER BY timestamp DESC LIMIT 10
            ''', (user_id, question_type))
            
            feedback_history = cursor.fetchall()
            
            if len(feedback_history) >= 3:
                # Analisar padrões de sucesso
                positive_features = {}
                negative_features = {}
                
                for features_json, score in feedback_history:
                    features = json.loads(features_json)
                    
                    if score > 0:
                        for feature, value in features.items():
                            positive_features[feature] = positive_features.get(feature, []) + [value]
                    else:
                        for feature, value in features.items():
                            negative_features[feature] = negative_features.get(feature, []) + [value]
                
                # Gerar recomendações baseadas em padrões
                if feedback_score <= 0:  # Feedback negativo atual
                    recommendations.append("Considere ajustar o estilo da resposta")
                    
                    # Recomendações específicas
                    if 'length_category' in positive_features:
                        most_successful_length = max(set(positive_features['length_category']), 
                                                   key=positive_features['length_category'].count)
                        recommendations.append(f"Tente respostas {most_successful_length}")
                    
                    if 'formality' in positive_features:
                        preferred_formality = max(set(positive_features['formality']), 
                                                key=positive_features['formality'].count)
                        recommendations.append(f"Use tom mais {preferred_formality}")
                
                else:  # Feedback positivo
                    recommendations.append("Continue com estratégias similares")
            
            else:
                recommendations.append("Coletando dados para otimização personalizada")
        
        except Exception as e:
            print(f"Erro ao gerar recomendações: {e}")
            recommendations.append("Erro na análise - continue com estratégia padrão")
        
        return recommendations
    
    def get_optimal_response_strategy(self, user_id: str, question_type: str) -> Dict:
        """Obter estratégia otimizada para resposta"""
        try:
            # Buscar estratégias mais efetivas para este usuário e tipo de pergunta
            cursor = self.conn.execute('''
                SELECT strategy_name, strategy_params, effectiveness
                FROM response_strategies
                WHERE user_id = ? AND context_type = ?
                AND effectiveness > 0
                ORDER BY effectiveness DESC
            ''', (user_id, question_type))
            
            strategies = cursor.fetchall()
            
            optimal_strategy = {
                'length': 'medium',
                'formality': 'neutral',
                'enthusiasm': 'medium',
                'structure': 'paragraph',
                'include_examples': False,
                'include_explanations': True,
                'confidence': 0.5
            }
            
            # Aplicar estratégias aprendidas
            for strategy_name, params_json, effectiveness in strategies:
                try:
                    params = json.loads(params_json)
                    preferred_value = params.get('preferred_value')
                    
                    if strategy_name == 'length_category':
                        optimal_strategy['length'] = preferred_value
                    elif strategy_name == 'formality':
                        optimal_strategy['formality'] = preferred_value
                    elif strategy_name == 'enthusiasm':
                        optimal_strategy['enthusiasm'] = preferred_value
                    elif strategy_name == 'has_examples' and preferred_value:
                        optimal_strategy['include_examples'] = True
                    elif strategy_name == 'has_explanation' and preferred_value:
                        optimal_strategy['include_explanations'] = True
                
                except:
                    continue
            
            # Calcular confiança geral
            if strategies:
                avg_effectiveness = sum(s[2] for s in strategies) / len(strategies)
                optimal_strategy['confidence'] = min(1.0, max(0.1, avg_effectiveness))
            
            return optimal_strategy
        
        except Exception as e:
            print(f"Erro ao obter estratégia otimizada: {e}")
            return {
                'length': 'medium',
                'formality': 'neutral',
                'enthusiasm': 'medium',
                'structure': 'paragraph',
                'include_examples': False,
                'include_explanations': True,
                'confidence': 0.5
            }
    
    def generate_optimized_prompt(self, user_id: str, question: str, base_prompt: str) -> str:
        """Gerar prompt otimizado baseado nas preferências do usuário"""
        question_type = self._categorize_question(question)
        strategy = self.get_optimal_response_strategy(user_id, question_type)
        
        # Modificadores baseados na estratégia
        modifiers = []
        
        if strategy['length'] == 'short':
            modifiers.append("Seja conciso e direto.")
        elif strategy['length'] == 'long':
            modifiers.append("Forneça uma resposta detalhada e abrangente.")
        
        if strategy['formality'] == 'formal':
            modifiers.append("Use linguagem formal e respeitosa.")
        elif strategy['formality'] == 'informal':
            modifiers.append("Use linguagem casual e amigável.")
        
        if strategy['enthusiasm'] == 'high':
            modifiers.append("Seja entusiasmado e use emojis apropriados.")
        elif strategy['enthusiasm'] == 'low':
            modifiers.append("Mantenha tom neutro e profissional.")
        
        if strategy['include_examples']:
            modifiers.append("Inclua exemplos práticos quando relevante.")
        
        if strategy['include_explanations']:
            modifiers.append("Explique o raciocínio por trás da resposta.")
        
        # Combinar prompt base com modificadores
        if modifiers:
            optimized_prompt = base_prompt + "\n\nEstilo de resposta: " + " ".join(modifiers)
        else:
            optimized_prompt = base_prompt
        
        return optimized_prompt
    
    def cleanup_old_data(self, days_old: int = 60):
        """Limpar dados antigos de otimização"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            with self.conn:
                # Remover análises antigas
                self.conn.execute('''
                    DELETE FROM feedback_analysis
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                # Manter apenas estratégias efetivas
                self.conn.execute('''
                    DELETE FROM response_strategies
                    WHERE last_updated < ? AND effectiveness < 0.2
                ''', (cutoff_date.isoformat(),))
        
        except Exception as e:
            print(f"Erro ao limpar dados antigos: {e}")