"""
Processamento de Texto
Utilitários para manipulação e análise de texto
"""
import re
from typing import List, Dict, Optional, Set
import unicodedata

class TextProcessor:
    """Processador de texto com funcionalidades avançadas"""
    
    def __init__(self):
        # Palavras comuns em português para filtragem
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'o', 'a', 'os', 'as', 'um', 'uma',
            'e', 'é', 'ou', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na',
            'nos', 'nas', 'por', 'para', 'com', 'sem', 'até', 'desde', 'que',
            'se', 'não', 'mas', 'como', 'quando', 'onde', 'porque', 'então'
        }
    
    def clean_text(self, text: str, remove_special_chars: bool = True) -> str:
        """Limpar texto removendo caracteres especiais e normalizando"""
        if not text:
            return ""
        
        # Normalizar unicode
        text = unicodedata.normalize('NFKD', text)
        
        # Remover quebras de linha extras
        text = re.sub(r'\n+', ' ', text)
        
        # Remover espaços extras
        text = re.sub(r'\s+', ' ', text)
        
        if remove_special_chars:
            # Manter apenas letras, números e pontuação básica
            text = re.sub(r'[^\w\s.,!?;:-]', '', text)
        
        return text.strip()
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extrair palavras-chave do texto"""
        if not text:
            return []
        
        # Limpar e normalizar texto
        cleaned = self.clean_text(text.lower())
        
        # Dividir em palavras
        words = re.findall(r'\b\w{3,}\b', cleaned)  # Palavras com 3+ caracteres
        
        # Filtrar stop words
        keywords = [word for word in words if word not in self.stop_words]
        
        # Contar frequência
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Ordenar por frequência e retornar top palavras
        sorted_keywords = sorted(word_freq.keys(), key=lambda w: word_freq[w], reverse=True)
        
        return sorted_keywords[:max_keywords]
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extrair sentenças do texto"""
        if not text:
            return []
        
        # Regex para detectar fim de sentença
        sentences = re.split(r'[.!?]+\s+', text.strip())
        
        # Filtrar sentenças muito curtas
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def detect_language_hints(self, text: str) -> Dict[str, float]:
        """Detectar pistas de idioma no texto"""
        if not text:
            return {'portuguese': 0.0, 'english': 0.0}
        
        text_lower = text.lower()
        
        # Indicadores de português
        pt_indicators = ['não', 'ção', 'ões', 'você', 'também', 'então', 'mais']
        pt_score = sum(1 for indicator in pt_indicators if indicator in text_lower)
        
        # Indicadores de inglês  
        en_indicators = ['the', 'and', 'you', 'that', 'with', 'have', 'this']
        en_score = sum(1 for indicator in en_indicators if indicator in text_lower)
        
        total_words = len(text_lower.split())
        if total_words == 0:
            return {'portuguese': 0.0, 'english': 0.0}
        
        return {
            'portuguese': pt_score / total_words,
            'english': en_score / total_words
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extrair entidades nomeadas básicas"""
        entities = {
            'emails': [],
            'urls': [],
            'mentions': [],
            'hashtags': [],
            'numbers': []
        }
        
        if not text:
            return entities
        
        # Emails
        entities['emails'] = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        
        # URLs
        entities['urls'] = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        
        # Menções (@usuario)
        entities['mentions'] = re.findall(r'@\w+', text)
        
        # Hashtags
        entities['hashtags'] = re.findall(r'#\w+', text)
        
        # Números
        entities['numbers'] = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        
        return entities
    
    def calculate_readability_score(self, text: str) -> float:
        """Calcular score básico de legibilidade (0-1)"""
        if not text:
            return 0.0
        
        sentences = self.extract_sentences(text)
        words = text.split()
        
        if not sentences or not words:
            return 0.0
        
        # Métricas básicas
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Score baseado em comprimento (sentenças e palavras menores = mais legível)
        sentence_score = max(0, 1 - (avg_sentence_length - 15) / 20)  # Ideal ~15 palavras/sentença
        word_score = max(0, 1 - (avg_word_length - 5) / 5)  # Ideal ~5 caracteres/palavra
        
        return (sentence_score + word_score) / 2

    def sentiment_indicators(self, text: str) -> Dict[str, float]:
        """Detectar indicadores básicos de sentimento"""
        if not text:
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
        
        text_lower = text.lower()
        
        # Palavras positivas
        positive_words = [
            'bom', 'boa', 'ótimo', 'ótima', 'excelente', 'fantástico', 'maravilhoso',
            'feliz', 'alegre', 'satisfeito', 'contente', 'gostei', 'adoro', 'amo',
            'perfeito', 'incrível', 'legal', 'demais', 'top'
        ]
        
        # Palavras negativas
        negative_words = [
            'ruim', 'péssimo', 'péssima', 'horrível', 'terrível', 'odiei', 'detesto',
            'triste', 'chateado', 'irritado', 'furioso', 'decepcionado', 'frustrado',
            'problema', 'erro', 'falha', 'difícil', 'impossível'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
        
        pos_ratio = positive_count / total_sentiment_words
        neg_ratio = negative_count / total_sentiment_words
        
        return {
            'positive': pos_ratio,
            'negative': neg_ratio,
            'neutral': max(0, 1 - pos_ratio - neg_ratio)
        }

# Funções de conveniência
def clean_text(text: str, remove_special_chars: bool = True) -> str:
    """Função de conveniência para limpeza de texto"""
    processor = TextProcessor()
    return processor.clean_text(text, remove_special_chars)

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Função de conveniência para extração de palavras-chave"""
    processor = TextProcessor()
    return processor.extract_keywords(text, max_keywords)

def detect_sentiment(text: str) -> str:
    """Detectar sentimento predominante"""
    processor = TextProcessor()
    indicators = processor.sentiment_indicators(text)
    
    max_sentiment = max(indicators.keys(), key=lambda k: indicators[k])
    return max_sentiment