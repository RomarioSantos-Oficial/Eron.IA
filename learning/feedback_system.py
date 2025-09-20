"""
Sistema de Feedback
Especializado em coletar, processar e aprender com feedback do usuário
"""
import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class FeedbackSystem:
    """Sistema completo de gerenciamento de feedback"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'memoria', 'feedback_system.db')
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        """Criar tabelas para sistema de feedback"""
        with self.conn:
            # Tabela principal de feedback
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS feedback_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    message_id TEXT,
                    user_message TEXT NOT NULL,
                    bot_response TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    feedback_score REAL,
                    feedback_details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Tabela de métricas agregadas
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS feedback_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    calculation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    sample_size INTEGER DEFAULT 1
                )
            ''')
            
            # Tabela de tendências de feedback
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS feedback_trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    trend_period TEXT NOT NULL,
                    positive_count INTEGER DEFAULT 0,
                    negative_count INTEGER DEFAULT 0,
                    neutral_count INTEGER DEFAULT 0,
                    avg_satisfaction REAL DEFAULT 0.0,
                    period_start DATETIME NOT NULL,
                    period_end DATETIME NOT NULL
                )
            ''')
    
    def register_feedback(self, user_id: str, platform: str, user_message: str, 
                         bot_response: str, feedback_type: str, 
                         feedback_score: Optional[float] = None,
                         feedback_details: Optional[Dict] = None,
                         message_id: Optional[str] = None) -> bool:
        """Registrar feedback do usuário"""
        try:
            # Normalizar tipo de feedback
            feedback_type = feedback_type.lower()
            if feedback_type not in ['positive', 'negative', 'neutral']:
                return False
            
            # Converter para score numérico se não fornecido
            if feedback_score is None:
                score_map = {'positive': 1.0, 'negative': -1.0, 'neutral': 0.0}
                feedback_score = score_map[feedback_type]
            
            # Serializar detalhes
            details_json = json.dumps(feedback_details) if feedback_details else None
            
            with self.conn:
                self.conn.execute('''
                    INSERT INTO feedback_entries
                    (user_id, platform, message_id, user_message, bot_response, 
                     feedback_type, feedback_score, feedback_details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, platform, message_id, user_message, bot_response,
                      feedback_type, feedback_score, details_json))
            
            # Processar feedback imediatamente
            self._process_new_feedback(user_id, feedback_type, feedback_score)
            
            return True
            
        except Exception as e:
            print(f"Erro ao registrar feedback: {e}")
            return False
    
    def _process_new_feedback(self, user_id: str, feedback_type: str, feedback_score: float):
        """Processar novo feedback e atualizar métricas"""
        try:
            # Atualizar métricas de satisfação
            self._update_satisfaction_metrics(user_id, feedback_score)
            
            # Atualizar tendências
            self._update_feedback_trends(user_id, feedback_type)
            
            # Trigger para otimização se necessário
            if feedback_type == 'negative':
                self._trigger_improvement_analysis(user_id)
        
        except Exception as e:
            print(f"Erro ao processar feedback: {e}")
    
    def _update_satisfaction_metrics(self, user_id: str, feedback_score: float):
        """Atualizar métricas de satisfação"""
        try:
            # Obter métrica atual
            cursor = self.conn.execute('''
                SELECT metric_value, sample_size FROM feedback_metrics
                WHERE user_id = ? AND metric_type = 'satisfaction'
                ORDER BY calculation_date DESC LIMIT 1
            ''', (user_id,))
            
            current_metric = cursor.fetchone()
            
            if current_metric:
                # Calcular nova média ponderada
                old_avg = current_metric[0]
                old_count = current_metric[1]
                new_count = old_count + 1
                new_avg = ((old_avg * old_count) + feedback_score) / new_count
            else:
                # Primeira métrica
                new_avg = feedback_score
                new_count = 1
            
            # Salvar nova métrica
            with self.conn:
                self.conn.execute('''
                    INSERT INTO feedback_metrics
                    (user_id, metric_type, metric_value, sample_size)
                    VALUES (?, 'satisfaction', ?, ?)
                ''', (user_id, new_avg, new_count))
        
        except Exception as e:
            print(f"Erro ao atualizar métricas de satisfação: {e}")
    
    def _update_feedback_trends(self, user_id: str, feedback_type: str):
        """Atualizar tendências de feedback"""
        try:
            # Definir período atual (semanal)
            now = datetime.now()
            week_start = now - timedelta(days=now.weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            week_end = week_start + timedelta(days=7)
            
            # Verificar se já existe registro para esta semana
            cursor = self.conn.execute('''
                SELECT id, positive_count, negative_count, neutral_count
                FROM feedback_trends
                WHERE user_id = ? AND period_start = ? AND period_end = ?
            ''', (user_id, week_start.isoformat(), week_end.isoformat()))
            
            existing = cursor.fetchone()
            
            with self.conn:
                if existing:
                    # Atualizar contadores
                    update_field = f"{feedback_type}_count"
                    self.conn.execute(f'''
                        UPDATE feedback_trends
                        SET {update_field} = {update_field} + 1
                        WHERE id = ?
                    ''', (existing[0],))
                else:
                    # Criar novo registro
                    counts = {'positive_count': 0, 'negative_count': 0, 'neutral_count': 0}
                    counts[f'{feedback_type}_count'] = 1
                    
                    self.conn.execute('''
                        INSERT INTO feedback_trends
                        (user_id, trend_period, positive_count, negative_count, 
                         neutral_count, period_start, period_end)
                        VALUES (?, 'weekly', ?, ?, ?, ?, ?)
                    ''', (user_id, counts['positive_count'], counts['negative_count'],
                          counts['neutral_count'], week_start.isoformat(), week_end.isoformat()))
        
        except Exception as e:
            print(f"Erro ao atualizar tendências: {e}")
    
    def _trigger_improvement_analysis(self, user_id: str):
        """Triggerar análise de melhoria após feedback negativo"""
        try:
            # Verificar se há padrão de feedback negativo recente
            recent_feedback = self.get_recent_feedback(user_id, days=7)
            negative_count = sum(1 for f in recent_feedback if f['feedback_type'] == 'negative')
            
            # Se mais de 3 feedbacks negativos na semana, marcar para análise especial
            if negative_count >= 3:
                print(f"ALERTA: Usuário {user_id} tem {negative_count} feedbacks negativos recentes")
                # Aqui poderia integrar com sistema de notificações ou análise automática
        
        except Exception as e:
            print(f"Erro ao analisar necessidade de melhoria: {e}")
    
    def get_user_feedback_summary(self, user_id: str, days: int = 30) -> Dict:
        """Obter resumo do feedback do usuário"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Contar tipos de feedback
            cursor = self.conn.execute('''
                SELECT feedback_type, COUNT(*) as count, AVG(feedback_score) as avg_score
                FROM feedback_entries
                WHERE user_id = ? AND timestamp >= ?
                GROUP BY feedback_type
            ''', (user_id, cutoff_date.isoformat()))
            
            feedback_counts = {}
            total_feedback = 0
            weighted_score = 0
            
            for row in cursor.fetchall():
                feedback_type = row[0]
                count = row[1]
                avg_score = row[2] or 0
                
                feedback_counts[feedback_type] = {
                    'count': count,
                    'avg_score': avg_score
                }
                total_feedback += count
                weighted_score += (avg_score * count)
            
            # Calcular métricas gerais
            overall_satisfaction = weighted_score / total_feedback if total_feedback > 0 else 0
            
            # Obter tendência
            trend = self._calculate_satisfaction_trend(user_id, days)
            
            return {
                'total_feedback': total_feedback,
                'feedback_by_type': feedback_counts,
                'overall_satisfaction': overall_satisfaction,
                'satisfaction_trend': trend,
                'period_days': days
            }
        
        except Exception as e:
            print(f"Erro ao obter resumo de feedback: {e}")
            return {
                'total_feedback': 0,
                'feedback_by_type': {},
                'overall_satisfaction': 0,
                'satisfaction_trend': 'stable',
                'period_days': days
            }
    
    def _calculate_satisfaction_trend(self, user_id: str, days: int) -> str:
        """Calcular tendência de satisfação"""
        try:
            # Dividir período em duas metades
            half_period = days // 2
            cutoff_date = datetime.now() - timedelta(days=days)
            mid_date = datetime.now() - timedelta(days=half_period)
            
            # Score da primeira metade
            cursor = self.conn.execute('''
                SELECT AVG(feedback_score) FROM feedback_entries
                WHERE user_id = ? AND timestamp >= ? AND timestamp < ?
            ''', (user_id, cutoff_date.isoformat(), mid_date.isoformat()))
            first_half = cursor.fetchone()[0] or 0
            
            # Score da segunda metade
            cursor = self.conn.execute('''
                SELECT AVG(feedback_score) FROM feedback_entries
                WHERE user_id = ? AND timestamp >= ?
            ''', (user_id, mid_date.isoformat()))
            second_half = cursor.fetchone()[0] or 0
            
            # Determinar tendência
            diff = second_half - first_half
            if diff > 0.2:
                return 'improving'
            elif diff < -0.2:
                return 'declining'
            else:
                return 'stable'
        
        except Exception as e:
            print(f"Erro ao calcular tendência: {e}")
            return 'stable'
    
    def get_recent_feedback(self, user_id: str, days: int = 7, limit: int = 50) -> List[Dict]:
        """Obter feedback recente"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor = self.conn.execute('''
                SELECT user_message, bot_response, feedback_type, feedback_score,
                       feedback_details, timestamp, platform
                FROM feedback_entries
                WHERE user_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, cutoff_date.isoformat(), limit))
            
            feedback_list = []
            for row in cursor.fetchall():
                feedback = {
                    'user_message': row[0],
                    'bot_response': row[1],
                    'feedback_type': row[2],
                    'feedback_score': row[3],
                    'feedback_details': json.loads(row[4]) if row[4] else None,
                    'timestamp': row[5],
                    'platform': row[6]
                }
                feedback_list.append(feedback)
            
            return feedback_list
        
        except Exception as e:
            print(f"Erro ao obter feedback recente: {e}")
            return []
    
    def get_feedback_insights(self, user_id: str) -> Dict:
        """Obter insights baseados no feedback"""
        try:
            insights = {
                'most_appreciated': [],
                'common_complaints': [],
                'suggested_improvements': [],
                'user_preferences': {}
            }
            
            # Analisar feedback positivo
            cursor = self.conn.execute('''
                SELECT bot_response FROM feedback_entries
                WHERE user_id = ? AND feedback_type = 'positive'
                ORDER BY timestamp DESC LIMIT 10
            ''', (user_id,))
            
            positive_responses = [row[0] for row in cursor.fetchall()]
            if positive_responses:
                insights['most_appreciated'] = self._analyze_common_features(positive_responses)
            
            # Analisar feedback negativo
            cursor = self.conn.execute('''
                SELECT bot_response FROM feedback_entries
                WHERE user_id = ? AND feedback_type = 'negative'
                ORDER BY timestamp DESC LIMIT 10
            ''', (user_id,))
            
            negative_responses = [row[0] for row in cursor.fetchall()]
            if negative_responses:
                insights['common_complaints'] = self._analyze_common_features(negative_responses)
            
            # Gerar sugestões de melhoria
            insights['suggested_improvements'] = self._generate_improvement_suggestions(
                user_id, positive_responses, negative_responses
            )
            
            return insights
        
        except Exception as e:
            print(f"Erro ao gerar insights: {e}")
            return {
                'most_appreciated': [],
                'common_complaints': [],
                'suggested_improvements': [],
                'user_preferences': {}
            }
    
    def _analyze_common_features(self, responses: List[str]) -> List[str]:
        """Analisar características comuns em respostas"""
        features = []
        
        if not responses:
            return features
        
        # Analisar características
        avg_length = sum(len(r) for r in responses) / len(responses)
        if avg_length > 300:
            features.append("Respostas detalhadas")
        elif avg_length < 100:
            features.append("Respostas concisas")
        
        emoji_count = sum(r.count('😊') + r.count('👍') + r.count('✨') for r in responses)
        if emoji_count / len(responses) > 1:
            features.append("Uso de emojis")
        
        list_count = sum(r.count('•') + r.count('-') for r in responses)
        if list_count / len(responses) > 2:
            features.append("Formatação em lista")
        
        return features
    
    def _generate_improvement_suggestions(self, user_id: str, positive_responses: List[str], 
                                        negative_responses: List[str]) -> List[str]:
        """Gerar sugestões de melhoria"""
        suggestions = []
        
        if not positive_responses and not negative_responses:
            return ["Continue monitorando feedback para sugestões personalizadas"]
        
        # Comparar características
        if positive_responses and negative_responses:
            pos_avg_len = sum(len(r) for r in positive_responses) / len(positive_responses)
            neg_avg_len = sum(len(r) for r in negative_responses) / len(negative_responses)
            
            if pos_avg_len > neg_avg_len * 1.5:
                suggestions.append("Usuário prefere respostas mais detalhadas")
            elif neg_avg_len > pos_avg_len * 1.5:
                suggestions.append("Usuário prefere respostas mais concisas")
        
        if len(negative_responses) > len(positive_responses):
            suggestions.append("Considere ajustar estilo de resposta baseado em padrões negativos")
        
        return suggestions if suggestions else ["Continue fornecendo respostas de qualidade"]
    
    def cleanup_old_feedback(self, days_old: int = 90):
        """Limpar feedback muito antigo"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            with self.conn:
                # Manter apenas dados estatísticos, remover detalhes
                self.conn.execute('''
                    DELETE FROM feedback_entries
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                # Limpar métricas muito antigas
                self.conn.execute('''
                    DELETE FROM feedback_metrics
                    WHERE calculation_date < ?
                ''', ((datetime.now() - timedelta(days=days_old * 2)).isoformat(),))
        
        except Exception as e:
            print(f"Erro ao limpar feedback antigo: {e}")
    
    def export_feedback_report(self, user_id: str, days: int = 30) -> Dict:
        """Exportar relatório completo de feedback"""
        try:
            summary = self.get_user_feedback_summary(user_id, days)
            insights = self.get_feedback_insights(user_id)
            recent_feedback = self.get_recent_feedback(user_id, days)
            
            return {
                'summary': summary,
                'insights': insights,
                'recent_feedback': recent_feedback,
                'report_generated': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"Erro ao exportar relatório: {e}")
            return {
                'error': str(e),
                'report_generated': datetime.now().isoformat()
            }