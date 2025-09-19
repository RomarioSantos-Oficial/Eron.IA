from enum import Enum
import sqlite3
import os
from datetime import datetime

class Emotion(Enum):
    HAPPY = "feliz"
    EXCITED = "animado"
    CALM = "calmo"
    NEUTRAL = "neutro"
    TIRED = "cansado"
    SAD = "triste"
    ANGRY = "irritado"

class EmotionSystem:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'memoria', 'emotions.db')
            
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
        
    def create_tables(self):
        with self.conn:
            # Tabela de estados emocionais do bot
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS bot_emotions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    emotion TEXT NOT NULL,
                    intensity INTEGER NOT NULL,
                    trigger TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de estados emocionais do usuário (detectados)
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS user_emotions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    emotion TEXT NOT NULL,
                    confidence FLOAT NOT NULL,
                    message_text TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de preferências emocionais
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS emotion_preferences (
                    user_id TEXT PRIMARY KEY,
                    preferred_emotions TEXT,
                    emotional_range INTEGER DEFAULT 3,
                    emotion_detection_enabled BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
    def set_bot_emotion(self, user_id, emotion, intensity=1, trigger=None):
        """Define o estado emocional atual do bot para um usuário específico"""
        if not isinstance(emotion, Emotion):
            raise ValueError("Emoção deve ser um membro de Emotion enum")
            
        with self.conn:
            self.conn.execute('''
                INSERT INTO bot_emotions (user_id, emotion, intensity, trigger)
                VALUES (?, ?, ?, ?)
            ''', (user_id, emotion.value, intensity, trigger))
            
    def get_bot_emotion(self, user_id):
        """Obtém o estado emocional atual do bot para um usuário específico"""
        cur = self.conn.cursor()
        cur.execute('''
            SELECT emotion, intensity, trigger
            FROM bot_emotions
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (user_id,))
        
        row = cur.fetchone()
        if row:
            return {
                'emotion': row[0],
                'intensity': row[1],
                'trigger': row[2]
            }
        return {'emotion': Emotion.NEUTRAL.value, 'intensity': 1, 'trigger': None}
        
    def detect_user_emotion(self, user_id, message_text):
        """Detecta a emoção do usuário baseado na mensagem"""
        # TODO: Implementar análise de sentimento mais sofisticada
        # Por enquanto, usa uma detecção simples baseada em palavras-chave
        
        keywords = {
            Emotion.HAPPY: ['feliz', 'alegre', 'contente', 'ótimo', 'maravilhoso'],
            Emotion.EXCITED: ['animado', 'empolgado', 'entusiasmado', 'uau'],
            Emotion.CALM: ['calmo', 'tranquilo', 'sereno', 'relaxado'],
            Emotion.SAD: ['triste', 'chateado', 'deprimido', 'mal'],
            Emotion.ANGRY: ['bravo', 'irritado', 'raiva', 'chato', 'odeio'],
            Emotion.TIRED: ['cansado', 'exausto', 'sono', 'preguiça']
        }
        
        detected_emotion = Emotion.NEUTRAL
        max_confidence = 0.0
        
        message_lower = message_text.lower()
        
        for emotion, words in keywords.items():
            confidence = sum(1 for word in words if word in message_lower) / len(words)
            if confidence > max_confidence:
                max_confidence = confidence
                detected_emotion = emotion
                
        if max_confidence > 0:
            with self.conn:
                self.conn.execute('''
                    INSERT INTO user_emotions 
                    (user_id, emotion, confidence, message_text)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, detected_emotion.value, max_confidence, message_text))
                
        return detected_emotion.value, max_confidence
        
    def get_user_emotional_history(self, user_id, limit=10):
        """Obtém o histórico emocional do usuário"""
        cur = self.conn.cursor()
        cur.execute('''
            SELECT emotion, confidence, message_text, timestamp
            FROM user_emotions
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        
        return [{
            'emotion': row[0],
            'confidence': row[1],
            'message': row[2],
            'timestamp': row[3]
        } for row in cur.fetchall()]
        
    def get_emotion_preferences(self, user_id):
        """Obtém as preferências emocionais do usuário"""
        cur = self.conn.cursor()
        cur.execute('''
            SELECT preferred_emotions, emotional_range, emotion_detection_enabled
            FROM emotion_preferences
            WHERE user_id = ?
        ''', (user_id,))
        
        row = cur.fetchone()
        if row:
            return {
                'preferred_emotions': row[0].split(',') if row[0] else [],
                'emotional_range': row[1],
                'emotion_detection_enabled': bool(row[2])
            }
            
        # Valores padrão se não existirem preferências
        return {
            'preferred_emotions': [],
            'emotional_range': 3,
            'emotion_detection_enabled': True
        }
        
    def update_emotion_preferences(self, user_id, preferred_emotions=None, 
                                 emotional_range=None, emotion_detection_enabled=None):
        """Atualiza as preferências emocionais do usuário"""
        cur = self.conn.cursor()
        cur.execute('SELECT 1 FROM emotion_preferences WHERE user_id = ?', (user_id,))
        exists = cur.fetchone() is not None
        
        if exists:
            updates = []
            params = []
            
            if preferred_emotions is not None:
                updates.append('preferred_emotions = ?')
                params.append(','.join(preferred_emotions))
                
            if emotional_range is not None:
                updates.append('emotional_range = ?')
                params.append(emotional_range)
                
            if emotion_detection_enabled is not None:
                updates.append('emotion_detection_enabled = ?')
                params.append(emotion_detection_enabled)
                
            if updates:
                updates.append('updated_at = CURRENT_TIMESTAMP')
                query = f'''
                    UPDATE emotion_preferences 
                    SET {', '.join(updates)}
                    WHERE user_id = ?
                '''
                params.append(user_id)
                
                with self.conn:
                    self.conn.execute(query, params)
        else:
            # Inserir novas preferências com valores padrão onde não especificado
            with self.conn:
                self.conn.execute('''
                    INSERT INTO emotion_preferences 
                    (user_id, preferred_emotions, emotional_range, emotion_detection_enabled)
                    VALUES (?, ?, ?, ?)
                ''', (
                    user_id,
                    ','.join(preferred_emotions) if preferred_emotions else '',
                    emotional_range if emotional_range is not None else 3,
                    emotion_detection_enabled if emotion_detection_enabled is not None else True
                ))
                
    def get_emotional_response_modifier(self, bot_emotion, intensity):
        """Retorna um modificador de resposta baseado no estado emocional do bot"""
        modifiers = {
            Emotion.HAPPY: {
                1: "😊 ",
                2: "😄 ",
                3: "🥰 "
            },
            Emotion.EXCITED: {
                1: "😃 ",
                2: "🤗 ",
                3: "✨ "
            },
            Emotion.CALM: {
                1: "😌 ",
                2: "🌸 ",
                3: "✨ "
            },
            Emotion.NEUTRAL: {
                1: "",
                2: "🙂 ",
                3: "😊 "
            },
            Emotion.TIRED: {
                1: "😴 ",
                2: "🥱 ",
                3: "💤 "
            },
            Emotion.SAD: {
                1: "😔 ",
                2: "🥺 ",
                3: "😢 "
            },
            Emotion.ANGRY: {
                1: "😤 ",
                2: "😠 ",
                3: "😡 "
            }
        }
        
        if isinstance(bot_emotion, str):
            try:
                bot_emotion = Emotion(bot_emotion)
            except ValueError:
                bot_emotion = Emotion.NEUTRAL
                
        intensity = max(1, min(3, intensity))  # Limitar entre 1 e 3
        
        return modifiers.get(bot_emotion, {}).get(intensity, "")