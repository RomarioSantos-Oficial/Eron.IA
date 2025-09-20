"""
Sistema de prevenção de confusão de papéis
Evita que usuários se identifiquem como assistentes e vice-versa
"""

import re
from typing import Dict, List, Tuple, Optional

class RoleConfusionPreventer:
    """Sistema para prevenir confusão de papéis na conversa"""
    
    def __init__(self):
        # Frases que indicam que o usuário pode estar se confundindo
        self.user_confusion_patterns = [
            r"me chamo \w+",
            r"meu nome é \w+",
            r"eu sou \w+",
            r"como posso te ajudar",
            r"em que posso ajudar",
            r"posso te ajudar",
            r"sou seu assistente",
            r"sou sua assistente",
            r"estou aqui para ajudar",
            r"pode me perguntar",
            r"faça sua pergunta"
        ]
        
        # Frases que o bot deve evitar para não se confundir
        self.bot_confusion_patterns = [
            r"qual é meu nome",
            r"como me chamo",
            r"quem sou eu",
            r"me ajude",
            r"não sei meu nome",
            r"preciso de ajuda"
        ]
        
        # Respostas para corrigir confusão do usuário
        self.correction_responses = [
            "😊 Acho que houve uma confusão! Eu sou o assistente aqui. Você é o usuário que está conversando comigo. Como posso ajudar você hoje?",
            "🤔 Parece que trocamos os papéis! Eu que sou seu assistente IA. Você tem alguma pergunta ou precisa de ajuda com algo?",
            "😄 Que fofo, mas eu que sou o assistente! Você é meu usuário. O que você gostaria de saber ou conversar hoje?",
            "🔄 Vamos reorganizar: EU sou o assistente IA, VOCÊ é quem faz as perguntas. Qual é sua dúvida?",
            "✨ Inversão detectada! Eu sou quem te ajuda. Você tem alguma pergunta ou curiosidade para mim?"
        ]
    
    def detect_user_confusion(self, message: str) -> bool:
        """
        Detecta se o usuário está se confundindo e agindo como assistente
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            bool: True se detectar confusão
        """
        message_lower = message.lower().strip()
        
        # Verificar padrões de confusão
        for pattern in self.user_confusion_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return True
        
        # Verificar se começa como resposta de assistente
        assistant_starts = [
            "olá! eu sou",
            "oi! sou",
            "me chamo",
            "meu nome é",
            "estou aqui para",
            "como posso ajudar",
            "em que posso ajudar"
        ]
        
        for start in assistant_starts:
            if message_lower.startswith(start):
                return True
                
        return False
    
    def get_confusion_correction(self, user_name: str = "usuário") -> str:
        """
        Retorna uma resposta para corrigir a confusão de papéis
        
        Args:
            user_name: Nome do usuário (se disponível)
            
        Returns:
            str: Resposta de correção
        """
        import random
        
        correction = random.choice(self.correction_responses)
        
        # Personalizar com o nome do usuário se disponível
        if user_name and user_name != "usuário":
            correction = correction.replace("Você", f"{user_name}, você")
            correction = correction.replace("você", f"{user_name}")
        
        return correction
    
    def prevent_bot_confusion(self, bot_response: str, bot_name: str, user_name: str) -> str:
        """
        Verifica e corrige respostas do bot que possam causar confusão
        
        Args:
            bot_response: Resposta gerada pelo bot
            bot_name: Nome do bot
            user_name: Nome do usuário
            
        Returns:
            str: Resposta corrigida
        """
        # Garantir que o bot se identifica corretamente
        response_lower = bot_response.lower()
        
        # Se o bot mencionar seu próprio nome incorretamente
        wrong_identifications = [
            f"me chamo {user_name}",
            f"meu nome é {user_name}",
            f"eu sou {user_name}"
        ]
        
        for wrong in wrong_identifications:
            if wrong.lower() in response_lower:
                bot_response = bot_response.replace(wrong, f"Meu nome é {bot_name}")
        
        # Garantir que não comece com confusão
        confusion_starts = [
            "qual é meu nome",
            "como me chamo",
            "quem sou eu"
        ]
        
        for start in confusion_starts:
            if bot_response.lower().startswith(start):
                bot_response = f"Meu nome é {bot_name}! {bot_response}"
        
        return bot_response
    
    def analyze_conversation_context(self, recent_messages: List[Dict]) -> Dict:
        """
        Analisa o contexto recente para detectar padrões de confusão
        
        Args:
            recent_messages: Lista de mensagens recentes
            
        Returns:
            Dict: Análise do contexto
        """
        confusion_count = 0
        role_switches = 0
        
        for i, msg in enumerate(recent_messages):
            if self.detect_user_confusion(msg.get('content', '')):
                confusion_count += 1
                
            # Detectar mudanças bruscas de papel
            if i > 0:
                prev_msg = recent_messages[i-1]
                if (msg.get('sender') == 'user' and 
                    prev_msg.get('sender') == 'user' and
                    self.detect_user_confusion(msg.get('content', ''))):
                    role_switches += 1
        
        return {
            'confusion_detected': confusion_count > 0,
            'confusion_count': confusion_count,
            'role_switches': role_switches,
            'needs_clarification': confusion_count > 2 or role_switches > 1
        }
    
    def generate_clarification_message(self, bot_name: str, user_name: str = "usuário") -> str:
        """
        Gera mensagem de esclarecimento sobre papéis
        
        Args:
            bot_name: Nome do bot
            user_name: Nome do usuário
            
        Returns:
            str: Mensagem de esclarecimento
        """
        clarification = f"""
🎭 *Vamos esclarecer nossos papéis:*

👤 **VOCÊ ({user_name}):**
• Faz perguntas
• Pede ajuda
• Conversa comigo
• É o usuário

🤖 **EU ({bot_name}):**
• Respondo perguntas
• Ofereço ajuda
• Converso com você
• Sou o assistente IA

✅ Agora que está claro, o que você gostaria de saber?
        """.strip()
        
        return clarification

class ConversationManager:
    """Gerenciador avançado de conversas com prevenção de confusão"""
    
    def __init__(self):
        self.confusion_preventer = RoleConfusionPreventer()
        self.conversation_state = {}
    
    def process_user_message(self, user_id: str, message: str, user_profile: Dict) -> Tuple[str, bool]:
        """
        Processa mensagem do usuário com verificação de confusão
        
        Args:
            user_id: ID do usuário
            message: Mensagem do usuário
            user_profile: Perfil do usuário
            
        Returns:
            Tuple[str, bool]: (resposta, confusão_detectada)
        """
        bot_name = user_profile.get('bot_name', 'ERON')
        user_name = user_profile.get('user_name', 'usuário')
        
        # Verificar confusão
        confusion_detected = self.confusion_preventer.detect_user_confusion(message)
        
        if confusion_detected:
            # Incrementar contador de confusão
            if user_id not in self.conversation_state:
                self.conversation_state[user_id] = {'confusion_count': 0}
            
            self.conversation_state[user_id]['confusion_count'] += 1
            
            # Se muita confusão, dar esclarecimento completo
            if self.conversation_state[user_id]['confusion_count'] > 2:
                response = self.confusion_preventer.generate_clarification_message(bot_name, user_name)
                self.conversation_state[user_id]['confusion_count'] = 0  # Reset após esclarecimento
            else:
                response = self.confusion_preventer.get_confusion_correction(user_name)
            
            return response, True
        
        return "", False
    
    def process_bot_response(self, response: str, user_profile: Dict) -> str:
        """
        Processa resposta do bot para evitar confusão
        
        Args:
            response: Resposta do bot
            user_profile: Perfil do usuário
            
        Returns:
            str: Resposta corrigida
        """
        bot_name = user_profile.get('bot_name', 'ERON')
        user_name = user_profile.get('user_name', 'usuário')
        
        return self.confusion_preventer.prevent_bot_confusion(response, bot_name, user_name)

# Instância global para uso
conversation_manager = ConversationManager()
