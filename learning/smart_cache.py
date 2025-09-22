"""
Sistema de Cache Inteligente
Otimização de performance e aprendizado rápido
"""
import json
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import threading
from collections import defaultdict, OrderedDict

class SmartCache:
    """Cache inteligente para otimizar respostas e aprendizado"""
    
    def __init__(self, max_memory_items=1000, ttl_minutes=60):
        self.max_memory_items = max_memory_items
        self.ttl_minutes = ttl_minutes
        
        # Cache em memória (mais rápido)
        self.memory_cache = OrderedDict()
        self.pattern_cache = {}
        self.user_preferences_cache = {}
        
        # Cache de contexto por tópico
        self.context_cache = defaultdict(list)
        
        # Cache de estatísticas
        self.stats = {
            'hits': 0,
            'misses': 0,
            'cache_size': 0
        }
        
        # Thread lock para operações thread-safe
        self.lock = threading.Lock()
        
    def _generate_key(self, user_id: str, message: str, context: str = "") -> str:
        """Gerar chave única para cache"""
        combined = f"{user_id}:{message}:{context}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _is_expired(self, timestamp: datetime) -> bool:
        """Verificar se item do cache expirou"""
        expiry_time = timestamp + timedelta(minutes=self.ttl_minutes)
        return datetime.now() > expiry_time
    
    def get_cached_response(self, user_id: str, message: str, context: str = "") -> Optional[Dict]:
        """Buscar resposta no cache"""
        with self.lock:
            cache_key = self._generate_key(user_id, message, context)
            
            if cache_key in self.memory_cache:
                cached_item = self.memory_cache[cache_key]
                
                # Verificar se não expirou
                if not self._is_expired(cached_item['timestamp']):
                    # Mover para final (LRU)
                    self.memory_cache.move_to_end(cache_key)
                    self.stats['hits'] += 1
                    return cached_item['data']
                else:
                    # Remover item expirado
                    del self.memory_cache[cache_key]
            
            self.stats['misses'] += 1
            return None
    
    def cache_response(self, user_id: str, message: str, response: str, 
                      context: str = "", metadata: Dict = None):
        """Armazenar resposta no cache"""
        with self.lock:
            cache_key = self._generate_key(user_id, message, context)
            
            cached_data = {
                'response': response,
                'metadata': metadata or {},
                'user_id': user_id,
                'message': message,
                'context': context
            }
            
            cached_item = {
                'data': cached_data,
                'timestamp': datetime.now(),
                'access_count': 1
            }
            
            # Adicionar ao cache
            self.memory_cache[cache_key] = cached_item
            
            # Limpar cache se muito grande (LRU)
            if len(self.memory_cache) > self.max_memory_items:
                # Remove o mais antigo
                oldest_key = next(iter(self.memory_cache))
                del self.memory_cache[oldest_key]
            
            self.stats['cache_size'] = len(self.memory_cache)
    
    def cache_user_preferences(self, user_id: str, preferences: Dict):
        """Cache de preferências do usuário"""
        with self.lock:
            self.user_preferences_cache[user_id] = {
                'preferences': preferences,
                'timestamp': datetime.now()
            }
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict]:
        """Buscar preferências do usuário no cache"""
        with self.lock:
            if user_id in self.user_preferences_cache:
                cached = self.user_preferences_cache[user_id]
                if not self._is_expired(cached['timestamp']):
                    return cached['preferences']
                else:
                    del self.user_preferences_cache[user_id]
            return None
    
    def cache_context_patterns(self, topic: str, patterns: List[str]):
        """Cache de padrões por tópico"""
        with self.lock:
            self.context_cache[topic] = {
                'patterns': patterns,
                'timestamp': datetime.now(),
                'usage_count': self.context_cache[topic].get('usage_count', 0) + 1
            }
    
    def get_context_patterns(self, topic: str) -> List[str]:
        """Buscar padrões de contexto por tópico"""
        with self.lock:
            if topic in self.context_cache:
                cached = self.context_cache[topic]
                if not self._is_expired(cached['timestamp']):
                    cached['usage_count'] = cached.get('usage_count', 0) + 1
                    return cached['patterns']
                else:
                    del self.context_cache[topic]
            return []
    
    def get_similar_cached_responses(self, user_id: str, message: str, 
                                   similarity_threshold: float = 0.7) -> List[Dict]:
        """Encontrar respostas similares no cache"""
        similar_responses = []
        
        with self.lock:
            for cache_key, cached_item in self.memory_cache.items():
                if self._is_expired(cached_item['timestamp']):
                    continue
                
                cached_data = cached_item['data']
                if cached_data['user_id'] == user_id:
                    # Calcular similaridade simples (pode ser melhorado)
                    similarity = self._calculate_similarity(
                        message, cached_data['message']
                    )
                    
                    if similarity >= similarity_threshold:
                        similar_responses.append({
                            'response': cached_data['response'],
                            'similarity': similarity,
                            'original_message': cached_data['message']
                        })
        
        # Ordenar por similaridade
        similar_responses.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_responses[:5]  # Top 5
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcular similaridade simples entre dois textos"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def clear_expired(self):
        """Limpar itens expirados do cache"""
        with self.lock:
            expired_keys = []
            
            # Cache de memória
            for key, item in self.memory_cache.items():
                if self._is_expired(item['timestamp']):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.memory_cache[key]
            
            # Cache de preferências
            expired_prefs = []
            for user_id, cached in self.user_preferences_cache.items():
                if self._is_expired(cached['timestamp']):
                    expired_prefs.append(user_id)
            
            for user_id in expired_prefs:
                del self.user_preferences_cache[user_id]
            
            # Cache de contexto
            expired_contexts = []
            for topic, cached in self.context_cache.items():
                if self._is_expired(cached['timestamp']):
                    expired_contexts.append(topic)
            
            for topic in expired_contexts:
                del self.context_cache[topic]
            
            self.stats['cache_size'] = len(self.memory_cache)
    
    def get_stats(self) -> Dict:
        """Obter estatísticas do cache"""
        with self.lock:
            hit_rate = 0
            total_requests = self.stats['hits'] + self.stats['misses']
            if total_requests > 0:
                hit_rate = (self.stats['hits'] / total_requests) * 100
            
            return {
                'hit_rate_percentage': round(hit_rate, 2),
                'total_hits': self.stats['hits'],
                'total_misses': self.stats['misses'],
                'cache_size': self.stats['cache_size'],
                'memory_cache_size': len(self.memory_cache),
                'preferences_cache_size': len(self.user_preferences_cache),
                'context_cache_size': len(self.context_cache)
            }
    
    def preload_common_patterns(self, patterns: Dict[str, List[str]]):
        """Pré-carregar padrões comuns no cache"""
        for topic, pattern_list in patterns.items():
            self.cache_context_patterns(topic, pattern_list)


class PredictiveCache(SmartCache):
    """Cache preditivo que antecipa necessidades do usuário"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prediction_patterns = defaultdict(list)
        self.user_sequences = defaultdict(list)
    
    def record_user_sequence(self, user_id: str, message: str):
        """Registrar sequência de mensagens do usuário"""
        with self.lock:
            self.user_sequences[user_id].append({
                'message': message,
                'timestamp': datetime.now()
            })
            
            # Manter apenas últimas 20 mensagens
            if len(self.user_sequences[user_id]) > 20:
                self.user_sequences[user_id] = self.user_sequences[user_id][-20:]
    
    def predict_next_topics(self, user_id: str, current_message: str) -> List[str]:
        """Prever próximos tópicos com base no histórico"""
        if user_id not in self.user_sequences:
            return []
        
        recent_messages = self.user_sequences[user_id][-5:]  # Últimas 5
        
        # Análise simples de padrões
        topics = []
        for msg in recent_messages:
            # Extrair tópicos principais (implementação simplificada)
            words = msg['message'].lower().split()
            for word in words:
                if len(word) > 4 and word not in ['como', 'você', 'pode', 'isso']:
                    topics.append(word)
        
        return list(set(topics))
    
    def preload_predictions(self, user_id: str, predictions: List[str]):
        """Pré-carregar respostas para predições"""
        for prediction in predictions:
            # Gerar contexto antecipado
            self.cache_context_patterns(f"predict_{prediction}", [prediction])


# Instância global do cache
smart_cache = SmartCache()
predictive_cache = PredictiveCache()