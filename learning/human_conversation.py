"""
Sistema de Conversação Humana
Torna as respostas mais naturais, empáticas e próximas para conversas simples
"""
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class HumanConversationSystem:
    """Sistema para conversas mais humanas e naturais"""
    
    def __init__(self):
        self.conversation_contexts = {
            'greeting': {
                'patterns': ['oi', 'olá', 'hello', 'hey', 'e aí', 'tudo bem'],
                'responses': [
                    "Oi! Como você está? 😊",
                    "Olá! Que bom te ver aqui! ✨",
                    "E aí! Tudo certo contigo? 🌟",
                    "Hey! Como está sendo seu dia? 💫",
                    "Oi! Pronto para uma boa conversa? 😄"
                ]
            },
            'wellbeing': {
                'patterns': ['como vai', 'tudo bem', 'como está', 'como anda'],
                'responses': [
                    "Por aqui tudo indo bem! E você, como está? 😌",
                    "Tô ótima, obrigada por perguntar! Como tem sido seu dia? ✨",
                    "Indo bem sim! E aí, como andam as coisas por aí? 🌸",
                    "Tudo tranquilo! Conta pra mim, como você tá? 💝",
                    "Bem demais! E você, está tudo certo? 🌺"
                ]
            },
            'gratitude': {
                'patterns': ['obrigado', 'obrigada', 'valeu', 'thanks'],
                'responses': [
                    "Imagina! Sempre que precisar, estou aqui! 💖",
                    "De nada! Foi um prazer te ajudar! 😊",
                    "Que isso! Estamos juntos nessa! ✨",
                    "Fico feliz em poder ajudar! 🌟",
                    "Não precisa agradecer! É sempre bom conversar contigo! 💫"
                ]
            },
            'casual_question': {
                'patterns': ['e aí', 'o que está fazendo', 'que que tá rolando'],
                'responses': [
                    "Por aqui tô só curtindo nossa conversa! E você, o que anda aprontando? 😄",
                    "Tô aqui pensando em como tornar nosso papo mais interessante! Conta novidade! ✨",
                    "Relaxando e esperando saber mais sobre você! Como tá sendo seu dia? 🌟",
                    "Aproveitando esse momento nosso aqui! E aí, me conta uma coisa boa! 💫",
                    "Tô na minha, curtindo trocar uma ideia contigo! Qual é a boa? 😊"
                ]
            },
            'personal_sharing': {
                'patterns': ['eu', 'meu', 'minha', 'aconteceu', 'hoje'],
                'encouraging_responses': [
                    "Nossa, que interessante! Me conta mais sobre isso! 😊",
                    "Adorei saber! Como foi essa experiência pra você? ✨",
                    "Que legal! Deve ter sido bem interessante, né? 🌟",
                    "Uau! Me fala mais detalhes, fiquei curiosa! 💫",
                    "Que bacana! Gostaria de compartilhar mais? 😄"
                ]
            }
        }
        
        # Expresões empáticas para diferentes contextos emocionais
        self.empathy_expressions = {
            'happy': ["Que alegria!", "Fico muito feliz por você! 😊", "Que maravilha! ✨"],
            'sad': ["Puxa, sinto muito... 😔", "Que pena, deve ser difícil... 💙", "Estou aqui contigo ✨"],
            'excited': ["Nossa, que animação! 🌟", "Adorei seu entusiasmo! 😄", "Que energia boa! ⚡"],
            'worried': ["Entendo sua preocupação... 💙", "Deve estar sendo difícil mesmo 😌", "Você não está sozinho(a) nisso 💝"],
            'confused': ["Realmente pode ser confuso mesmo... 🤔", "Vamos pensar juntos! 💭", "É normal se sentir assim 💫"]
        }
        
        # Conectores para tornar a conversa mais fluida
        self.conversation_connectors = [
            "E aí,", "Então,", "Puxa,", "Nossa,", "Ah,", "Caramba,", 
            "Realmente,", "Entendi,", "Interessante,", "Que legal,"
        ]
        
        # Finalizadores naturais
        self.natural_endings = [
            "E aí, o que você acha? 😊",
            "Me conta sua opinião! ✨",
            "Qual é sua experiência com isso? 🌟",
            "E você, já passou por algo assim? 💫",
            "Como você vê essa situação? 😄",
            "Fiquei curiosa sobre sua perspectiva! 🌸"
        ]

    def detect_conversation_type(self, message: str) -> str:
        """Detectar o tipo de conversa baseado na mensagem"""
        message_lower = message.lower().strip()
        
        for context_type, data in self.conversation_contexts.items():
            if any(pattern in message_lower for pattern in data['patterns']):
                return context_type
        
        # Análises mais específicas
        if '?' in message and len(message.split()) < 10:
            return 'simple_question'
        elif any(word in message_lower for word in ['sinto', 'triste', 'chateado', 'mal']):
            return 'emotional_negative'
        elif any(word in message_lower for word in ['feliz', 'alegre', 'animado', 'bem']):
            return 'emotional_positive'
        elif any(word in message_lower for word in ['não sei', 'confuso', 'dúvida']):
            return 'confusion'
        
        return 'general'
    
    def detect_user_mood(self, message: str, user_profile: dict = None) -> dict:
        """🎭 Detecta o humor/estado emocional do usuário com análise contextual"""
        message = message.lower().strip()
        
        # Estados emocionais positivos
        positive_indicators = [
            'feliz', 'alegre', 'animado', 'bem', 'ótimo', 'excelente', 
            'maravilhoso', 'perfeito', 'incrível', 'adorei', 'amei',
            'satisfeito', 'radiante', 'eufórico', 'empolgado'
        ]
        
        # Estados emocionais negativos
        negative_indicators = [
            'triste', 'chateado', 'irritado', 'nervoso', 'preocupado',
            'ansioso', 'mal', 'péssimo', 'terrível', 'odiei', 'detestei',
            'frustrado', 'desanimado', 'deprimido', 'estressado'
        ]
        
        # Estados neutros/curiosos
        curious_indicators = [
            'interessante', 'curioso', 'pensativo', 'reflexivo', 'intrigado',
            'questionador', 'investigativo', 'analítico'
        ]
        
        # Estados de necessidade de suporte
        support_indicators = [
            'ajuda', 'socorro', 'dificuldade', 'problema', 'confuso',
            'perdido', 'não entendo', 'não sei', 'preciso', 'auxílio'
        ]
        
        # Estados de energia/entusiasmo
        energetic_indicators = [
            'animado', 'empolgado', 'cheio de energia', 'entusiasmado',
            'motivado', 'inspirado', 'determinado'
        ]
        
        # Análise das palavras-chave
        mood_score = 0
        detected_emotions = []
        intensity_multiplier = 1
        
        for word in positive_indicators:
            if word in message:
                mood_score += 2
                detected_emotions.append('positive')
                if word in ['incrível', 'maravilhoso', 'perfeito']:
                    intensity_multiplier = 1.5
        
        for word in negative_indicators:
            if word in message:
                mood_score -= 2
                detected_emotions.append('negative')
                if word in ['péssimo', 'terrível', 'deprimido']:
                    intensity_multiplier = 1.5
        
        for word in curious_indicators:
            if word in message:
                mood_score += 1
                detected_emotions.append('curious')
        
        for word in support_indicators:
            if word in message:
                detected_emotions.append('needs_support')
                if word in ['socorro', 'ajuda', 'dificuldade']:
                    intensity_multiplier = 1.3
        
        for word in energetic_indicators:
            if word in message:
                mood_score += 1
                detected_emotions.append('energetic')
        
        # Análise de pontuação e estrutura para intensidade
        exclamation_count = message.count('!')
        question_count = message.count('?')
        caps_ratio = sum(1 for c in message if c.isupper()) / max(len(message), 1)
        
        if exclamation_count > 2:
            detected_emotions.append('excited')
            intensity_multiplier *= 1.2
        
        if question_count > 2:
            detected_emotions.append('confused')
            intensity_multiplier *= 1.1
        
        if caps_ratio > 0.3:  # Muitas maiúsculas indicam emoção intensa
            intensity_multiplier *= 1.4
        
        # Análise de contexto emocional usando palavras conectadas
        emotional_phrases = {
            'muito feliz': 3,
            'super animado': 3,
            'bem triste': -3,
            'muito mal': -3,
            'não aguento': -2,
            'adorando': 2,
            'odiando': -2,
            'apaixonado': 3,
            'decepcionado': -2
        }
        
        for phrase, score in emotional_phrases.items():
            if phrase in message:
                mood_score += score
                intensity_multiplier *= 1.3
        
        # Determinar humor principal com base em intensidade
        final_score = mood_score * intensity_multiplier
        
        if final_score > 2:
            primary_mood = 'very_happy'
        elif final_score > 0:
            primary_mood = 'happy'
        elif final_score < -2:
            primary_mood = 'very_sad'
        elif final_score < 0:
            primary_mood = 'sad'
        elif 'needs_support' in detected_emotions:
            primary_mood = 'needs_support'
        elif 'curious' in detected_emotions:
            primary_mood = 'curious'
        elif 'excited' in detected_emotions:
            primary_mood = 'excited'
        elif 'confused' in detected_emotions:
            primary_mood = 'confused'
        elif 'energetic' in detected_emotions:
            primary_mood = 'energetic'
        else:
            primary_mood = 'neutral'
        
        # Calcular intensidade final (1-5)
        base_intensity = min(abs(final_score) + len(detected_emotions), 5)
        final_intensity = int(base_intensity * min(intensity_multiplier, 2.0))
        final_intensity = max(1, min(final_intensity, 5))
        
        return {
            'primary_mood': primary_mood,
            'emotions': list(set(detected_emotions)),
            'mood_score': final_score,
            'intensity': final_intensity,
            'confidence': min(len(detected_emotions) * 20 + abs(final_score) * 10, 100),
            'indicators': {
                'exclamations': exclamation_count,
                'questions': question_count,
                'caps_ratio': caps_ratio,
                'intensity_multiplier': intensity_multiplier
            }
        }

    def detect_emotional_context(self, message: str) -> str:
        """Detectar o contexto emocional da mensagem"""
        message_lower = message.lower()
        
        # Indicadores de felicidade
        happy_indicators = ['feliz', 'alegre', 'animado', 'bem', 'ótimo', 'maravilha', 
                          'incrível', 'fantástico', 'perfeito', 'adorei', 'amei']
        
        # Indicadores de tristeza
        sad_indicators = ['triste', 'chateado', 'mal', 'péssimo', 'horrível', 
                        'difícil', 'problema', 'preocupado', 'angustiado']
        
        # Indicadores de animação
        excited_indicators = ['animado', 'empolgado', 'ansioso', 'não vejo a hora', 
                            'incrível', 'demais', 'muito bom']
        
        # Indicadores de confusão  
        confused_indicators = ['confuso', 'não entendo', 'não sei', 'dúvida', 
                             'complicado', 'difícil de entender']
        
        if any(indicator in message_lower for indicator in happy_indicators):
            return 'happy'
        elif any(indicator in message_lower for indicator in sad_indicators):
            return 'sad'
        elif any(indicator in message_lower for indicator in excited_indicators):
            return 'excited'
        elif any(indicator in message_lower for indicator in confused_indicators):
            return 'confused'
        
        return 'neutral'

    def generate_human_response(self, message: str, user_profile: Optional[Dict] = None) -> str:
        """Gerar resposta mais humana e natural com análise de humor avançada"""
        conversation_type = self.detect_conversation_type(message)
        mood_analysis = self.detect_user_mood(message, user_profile)
        
        # Resposta baseada no tipo de conversa
        if conversation_type in self.conversation_contexts:
            base_response = random.choice(self.conversation_contexts[conversation_type]['responses'])
        else:
            base_response = self._generate_contextual_response(message, mood_analysis, user_profile)
        
        # Adicionar toque empático baseado no humor detectado
        empathetic_response = self._add_empathetic_touch(
            base_response, mood_analysis, user_profile
        )
        
        # Personalizar com nome do usuário se disponível
        if user_profile and user_profile.get('user_name'):
            user_name = user_profile['user_name']
            # Inserir nome ocasionalmente para mais proximidade
            if random.random() < 0.3 and 'você' in empathetic_response:  # 30% das vezes
                empathetic_response = empathetic_response.replace('você', f'{user_name}', 1)
        
        print(f"[DEBUG] Humor detectado: {mood_analysis['primary_mood']} (intensidade: {mood_analysis['intensity']})")
        return empathetic_response
    
    def _generate_contextual_response(self, message: str, mood_analysis: dict, user_profile: dict = None) -> str:
        """Gerar resposta contextual baseada na análise de humor"""
        primary_mood = mood_analysis['primary_mood']
        intensity = mood_analysis['intensity']
        
        # Respostas baseadas no humor principal
        mood_responses = {
            'very_happy': [
                "Nossa, que alegria contagiante! 🌟 Me conta mais sobre isso!",
                "Adorei ver você assim tão animado(a)! ✨ Compartilha essa energia comigo!",
                "Que maravilha! Sua felicidade está radiante! 😊 O que aconteceu de bom?",
                "Uau! Tô sentindo toda essa positividade daqui! 💫 Me fala mais!"
            ],
            'happy': [
                "Que bom te ver bem! 😊 Como posso te ajudar hoje?",
                "Adorei seu astral! ✨ No que posso colaborar?",
                "Que energia boa! 🌟 Estou aqui pra conversar!",
                "Fico feliz em perceber que você está bem! �"
            ],
            'very_sad': [
                "Sinto muito que esteja passando por isso... 💙 Estou aqui para ouvir você.",
                "Deve estar sendo realmente difícil... 😌 Quer desabafar comigo?",
                "Meu coração se aperta vendo você assim... 💜 Como posso ajudar?",
                "Você não está sozinho(a) nisso... 🤗 Vamos conversar?"
            ],
            'sad': [
                "Percebo que você não está muito bem... 💙 Quer conversar sobre isso?",
                "Às vezes é difícil mesmo... 😌 Estou aqui se precisar desabafar.",
                "Sinto que algo te incomoda... 💜 Posso te escutar.",
                "Todo mundo tem dias difíceis... 🌙 Como posso te apoiar?"
            ],
            'needs_support': [
                "Claro que posso te ajudar! � Me explica melhor o que está acontecendo?",
                "Estou aqui pra isso mesmo! 🤝 Qual é a dificuldade?",
                "Vamos resolver isso juntos! ✨ Me conta mais detalhes?",
                "Pode contar comigo! 💝 O que você precisa?"
            ],
            'excited': [
                "Nossa, que empolgação! 🎉 Me contamina com esse entusiasmo!",
                "Adorei essa energia! ⚡ O que te deixou assim tão animado(a)?",
                "Que animação é essa?! 🌟 Quero saber tudo!",
                "Uau! Tô sentindo toda essa emoção! � Me conta!"
            ],
            'confused': [
                "Entendo que pode ser confuso mesmo... 🤔 Vamos esclarecer isso juntos?",
                "Às vezes as coisas ficam meio embaralhadas na cabeça, né? 💭 Posso ajudar?",
                "É normal ficar confuso às vezes... 🌀 Que tal conversarmos sobre isso?",
                "Vamos destrinchar isso com calma? 🧩 Estou aqui pra ajudar!"
            ],
            'energetic': [
                "Que energia incrível! ⚡ Adorei esse pique!",
                "Nossa, que disposição! 🌟 Me conta o que te motiva assim!",
                "Adorei esse ânimo! 🚀 Vamos canalizar essa energia!",
                "Que vitalidade! 💪 Me fala o que está te inspirando!"
            ],
            'curious': [
                "Que interessante! 🤔 Adorei sua curiosidade!",
                "Boa pergunta! 💭 Vamos explorar isso juntos?",
                "Curioso mesmo! 🔍 Me conta mais sobre o que te intriga!",
                "Que reflexão bacana! 🌟 Vamos pensar sobre isso!"
            ]
        }
        
        if primary_mood in mood_responses:
            return random.choice(mood_responses[primary_mood])
        
        # Resposta padrão neutra
        return "Interessante! Me conte mais sobre isso! 😊"
    
    def _add_empathetic_touch(self, base_response: str, mood_analysis: dict, user_profile: dict = None) -> str:
        """Adicionar toque empático baseado no humor e intensidade"""
        primary_mood = mood_analysis['primary_mood']
        intensity = mood_analysis['intensity']
        
        # Adicionar conectores empáticos baseados no humor
        empathy_connectors = {
            'very_happy': ["Que alegria!", "Nossa!", "Adorei!", "Que maravilha!"],
            'happy': ["Que bom!", "Fico feliz!", "Legal!", "Bacana!"],
            'very_sad': ["Puxa vida...", "Sinto muito...", "Que difícil...", "Compreendo..."],
            'sad': ["Entendo...", "Imagino...", "Realmente...", "É complicado..."],
            'needs_support': ["Claro!", "É claro!", "Sem problema!", "Vamos lá!"],
            'excited': ["Uau!", "Incrível!", "Que demais!", "Fantástico!"],
            'confused': ["Entendo...", "Faz sentido...", "Realmente...", "É compreensível..."],
            'energetic': ["Que energia!", "Adorei!", "Que ânimo!", "Fantástico!"],
            'curious': ["Interessante!", "Que legal!", "Bacana!", "Boa pergunta!"]
        }
        
        # Adicionar intensificadores baseados na intensidade
        intensity_modifiers = {
            5: ["totalmente", "completamente", "absolutamente", "extremamente"],
            4: ["muito", "bastante", "bem", "super"],
            3: ["meio", "um pouco", "razoavelmente", "consideravelmente"],
            2: ["", "um tanto", "levemente", "minimamente"],
            1: ["", "", "talvez", "possivelmente"]
        }
        
        # Escolher conector empático apropriado se não houver já
        if primary_mood in empathy_connectors:
            connector = random.choice(empathy_connectors[primary_mood])
            if connector and not any(emp in base_response for emp in empathy_connectors[primary_mood]):
                base_response = f"{connector} {base_response}"
        
        # Adicionar suporte emocional específico para moods negativos intensos
        if primary_mood in ['very_sad', 'sad'] and intensity >= 3:
            supportive_additions = [
                " Você não está sozinho(a) nisso! 💙",
                " Estou aqui para te apoiar! 🤗",
                " Vamos passar por isso juntos! 💜",
                " Pode contar comigo sempre! 🌟"
            ]
            if not any(phrase in base_response for phrase in ["sozinho", "apoiar", "juntos", "contar"]):
                base_response += random.choice(supportive_additions)
        
        # Adicionar celebração para moods muito positivos
        elif primary_mood in ['very_happy', 'excited'] and intensity >= 4:
            celebratory_additions = [
                " Que conquista! 🎉",
                " Merece toda essa alegria! ✨",
                " Continue assim! 🌟",
                " Que momento especial! 💫"
            ]
            if not any(phrase in base_response for phrase in ["conquista", "merece", "continue", "especial"]):
                base_response += random.choice(celebratory_additions)
        
        return base_response

    def create_casual_templates(self) -> Dict[str, List[str]]:
        """🎭 Templates específicos para conversas casuais do dia a dia"""
        return {
            'morning_greetings': [
                "Bom dia! Como você acordou hoje? 🌅",
                "Oi! Dormiu bem? Como tá sendo o início do dia? ☀️",
                "Bom dia! Que energia você traz hoje? ✨",
                "Oi! Como tá começando esse dia aí? 🌸"
            ],
            'afternoon_greetings': [
                "Boa tarde! Como tá sendo o dia? 🌞",
                "Oi! Tudo bem por aí nessa tarde? 🌻",
                "Boa tarde! O dia tá corrido ou tranquilo? 💫",
                "E aí! Como andam as coisas hoje? 🌟"
            ],
            'evening_greetings': [
                "Boa noite! Como foi o dia? 🌙",
                "Oi! Chegando em casa agora? ✨",
                "Boa noite! Conseguiu relaxar hoje? 🌸",
                "E aí! Como tá sendo a noite? 💙"
            ],
            'weather_chat': [
                "Nossa, e esse tempo aí? Como tá? 🌤️",
                "Que clima temos hoje! Tá agradável aí? 🌈",
                "E esse tempo? Tá influenciando seu humor? ☀️",
                "Como tá o dia aí? Sol, chuva, nublado? 🌦️"
            ],
            'weekend_plans': [
                "E aí, que planos pro fim de semana? 🎉",
                "Já pensou no que vai fazer no sábado e domingo? 🌟",
                "Fim de semana chegando! Algum plano especial? ✨",
                "Weekend mood ativado? O que anda planejando? 🎊"
            ],
            'daily_check_in': [
                "E aí, como tá o humor hoje? 😊",
                "Conta aí, como você tá se sentindo? 💙",
                "Como anda o coração hoje? 💜",
                "Me fala como você está! 🌟"
            ],
            'food_talk': [
                "E a comida? Já comeu algo gostoso hoje? 🍽️",
                "Que tal uma conversa sobre comida? Tá com fome? 😋",
                "Almoçou algo bom? Me fala da sua comida favorita! 🥘",
                "Vamos falar de comida! Qual seu prato do momento? 🍕"
            ],
            'work_study_life': [
                "Como andam os estudos/trabalho hoje? 📚",
                "Tá corrido esse período? Como você anda lidando? 💪",
                "E essa vida acadêmica/profissional? Tudo certo? ⭐",
                "Como tá sendo conciliar tudo? Me conta! 🎯"
            ],
            'hobbies_interests': [
                "E aí, o que anda te interessando ultimamente? 🎨",
                "Tem algum hobby novo ou projeto pessoal? 🛠️",
                "O que você anda fazendo pra relaxar? 🎵",
                "Me conta sobre seus interesses atuais! 🌟"
            ],
            'casual_compliments': [
                "Gosto muito de conversar contigo! 💝",
                "Você tem uma energia muito boa! ✨",
                "Adorei nosso papo de hoje! 😊",
                "Sua forma de ver as coisas é interessante! 🌟"
            ],
            'supportive_phrases': [
                "Tô aqui se precisar de alguma coisa! 🤗",
                "Qualquer coisa, me chama que a gente conversa! 💙",
                "Você não está sozinho(a) nisso! 💜",
                "Estamos juntos nessa jornada! ✨"
            ],
            'transition_phrases': [
                "E por falar nisso...",
                "Ah, isso me lembrou de uma coisa...",
                "Falando nisso...",
                "Mudando um pouco de assunto...",
                "Isso que você falou me fez pensar...",
                "Aproveitando o gancho..."
            ]
        }
    
    def get_casual_response_by_context(self, context: str, user_profile: dict = None) -> str:
        """🎯 Obter resposta casual específica por contexto"""
        templates = self.create_casual_templates()
        
        if context in templates:
            base_response = random.choice(templates[context])
            
            # Personalizar com informações do usuário se disponível
            if user_profile and user_profile.get('user_name') and random.random() < 0.4:
                user_name = user_profile['user_name']
                # Adicionar nome de forma natural
                if "você" in base_response:
                    base_response = base_response.replace("você", f"{user_name}", 1)
            
            return base_response
        
        return self.generate_human_response("conversa casual", user_profile)
    
    def detect_casual_context(self, message: str) -> str:
        """🔍 Detectar contexto casual específico da mensagem"""
        message_lower = message.lower()
        
        # Contextos baseados em horário e saudações
        if any(greeting in message_lower for greeting in ['bom dia', 'bom-dia', 'morning']):
            return 'morning_greetings'
        elif any(greeting in message_lower for greeting in ['boa tarde', 'boa-tarde', 'afternoon']):
            return 'afternoon_greetings'
        elif any(greeting in message_lower for greeting in ['boa noite', 'boa-noite', 'evening']):
            return 'evening_greetings'
        
        # Contextos temáticos
        elif any(weather in message_lower for weather in ['tempo', 'clima', 'chuva', 'sol', 'frio', 'calor']):
            return 'weather_chat'
        elif any(weekend in message_lower for weekend in ['fim de semana', 'sábado', 'domingo', 'weekend', 'final de semana']):
            return 'weekend_plans'
        elif any(food in message_lower for food in ['comida', 'almoço', 'jantar', 'fome', 'comer', 'delicious']):
            return 'food_talk'
        elif any(work in message_lower for work in ['trabalho', 'estudo', 'faculdade', 'escola', 'job', 'study']):
            return 'work_study_life'
        elif any(hobby in message_lower for hobby in ['hobby', 'interesse', 'gosto', 'adoro', 'paixão', 'curtir']):
            return 'hobbies_interests'
        elif any(check in message_lower for check in ['como está', 'como vai', 'tudo bem', 'que tal']):
            return 'daily_check_in'
        
        return 'general_casual'
    
    def enhance_conversation_flow(self, message: str, response: str, user_profile: dict = None) -> str:
        """🌊 Melhorar o fluxo da conversa com conectores naturais"""
        templates = self.create_casual_templates()
        
        # Adicionar conectores de transição ocasionalmente
        if random.random() < 0.3 and len(response.split()) > 5:
            connector = random.choice(templates['transition_phrases'])
            # Inserir conector no meio da resposta para fluidez
            words = response.split()
            middle = len(words) // 2
            words.insert(middle, connector)
            response = ' '.join(words)
        
        # Adicionar frases de apoio para conversas emocionais
        if any(emotion in message.lower() for emotion in ['triste', 'preocupado', 'ansioso', 'difícil']):
            if random.random() < 0.5:
                supportive = random.choice(templates['supportive_phrases'])
                response += f" {supportive}"
        
        # Adicionar elogios casuais ocasionalmente
        elif any(positive in message.lower() for positive in ['obrigado', 'adorei', 'legal', 'incrível']):
            if random.random() < 0.4:
                compliment = random.choice(templates['casual_compliments'])
                response += f" {compliment}"
        
        return response
        
        return f"{connector} {base_response} {ending}"

    def add_conversation_warmth(self, response: str) -> str:
        """Adicionar calor humano à resposta"""
        # Pequenas expressões que tornam a conversa mais próxima
        warm_additions = [
            "😊", "✨", "🌟", "💫", "🌸", "💝", "😄", "🌺", "💖", "😌"
        ]
        
        # Frases que criam proximidade
        proximity_phrases = [
            "Gosto de conversar contigo!",
            "É sempre bom trocar ideias assim!",
            "Adoro essa nossa conversa!",
            "Que legal poder falar sobre isso!",
            "É um prazer conhecer você melhor!"
        ]
        
        # Adicionar calor ocasionalmente
        if random.random() < 0.2:  # 20% das vezes
            warmth = random.choice(proximity_phrases)
            response += f" {warmth}"
        
        # Adicionar emoji se não houver
        if not any(emoji in response for emoji in warm_additions):
            emoji = random.choice(warm_additions)
            response += f" {emoji}"
        
        return response

    def optimize_for_natural_flow(self, response: str, previous_messages: List[str] = None) -> str:
        """Otimizar resposta para fluxo natural da conversa"""
        # Evitar repetições das últimas 3 mensagens
        if previous_messages:
            recent_messages = previous_messages[-3:]
            # Implementar lógica para evitar repetições
            for msg in recent_messages:
                # Se a resposta é muito similar, tentar uma variação
                if self._similarity_score(response, msg) > 0.7:
                    response = self._create_variation(response)
        
        # Ajustar tom baseado no fluxo da conversa
        response = self._adjust_conversational_tone(response)
        
        return response

    def _similarity_score(self, text1: str, text2: str) -> float:
        """Calcular similaridade entre duas strings"""
        # Implementação simples de similaridade
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0

    def _create_variation(self, response: str) -> str:
        """Criar uma variação da resposta para evitar repetição"""
        variations = {
            "Como você está?": ["Tudo bem contigo?", "Como anda?", "Como tem passado?"],
            "Que interessante!": ["Que bacana!", "Que legal!", "Nossa, interessante!"],
            "Entendi": ["Ah, saquei!", "Compreendo", "Faz sentido"],
            "Obrigada": ["Valeu!", "Muito obrigada!", "Brigadão!"]
        }
        
        for original, alternativas in variations.items():
            if original.lower() in response.lower():
                return response.replace(original, random.choice(alternativas))
        
        return response

    def _adjust_conversational_tone(self, response: str) -> str:
        """Ajustar tom da conversa para ser mais natural"""
        # Tornar menos formal
        formal_replacements = {
            "Você poderia": "Você pode",
            "Gostaria de": "Quer",
            "Por favor": "Por favor",
            "Certamente": "Claro",
            "Evidentemente": "Óbvio",
            "Naturalmente": "Claro"
        }
        
        for formal, casual in formal_replacements.items():
            response = response.replace(formal, casual)
        
        return response