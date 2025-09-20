"""
Aplicação Flask principal reorganizada
"""
import os
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask

# Carregar variáveis de ambiente
load_dotenv()

def create_app():
    """Factory para criar aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.secret_key = os.getenv('SECRET_KEY', 'fallback-super-secret-key-for-dev')
    app.permanent_session_lifetime = timedelta(days=30)
    
    # Configurar upload
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
    
    # Registrar blueprints
    from web.routes.auth import auth_bp
    from web.routes.main import main_bp
    from web.routes.chat import chat_bp
    from web.routes.config import config_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(config_bp)
    
    return app

# Função get_llm_response deve ser mantida aqui para compatibilidade
def get_llm_response(user_message, user_id, platform='web'):
    """
    Função principal para obter resposta da IA
    Mantida aqui para compatibilidade com imports existentes
    """
    try:
        from src.emotion_system import EmotionSystem as AIService
        ai_service = AIService()
        
        return ai_service.get_response(
            message=user_message,
            user_id=user_id,
            platform=platform
        )
    
    except ImportError:
        # Fallback para implementação atual
        return _get_llm_response_legacy(user_message, user_id, platform)

def _get_llm_response_legacy(user_message, user_id, platform='web'):
    """Implementação legacy da função de resposta"""
    import requests
    import json
    
    try:
        # Importar componentes necessários
        from src.knowledge_base import KnowledgeBase
        from src.memory import EronMemory
        from src.fast_learning import FastLearningSystem
        from src.sensitive_memory import SensitiveMemory
        from src.emotion_system import EmotionSystem
        from src.preferences import PreferencesManager
        
        # Inicializar componentes
        knowledge_base = KnowledgeBase(os.path.join(os.path.dirname(__file__), 'memoria'))
        memory = EronMemory()
        fast_learning = FastLearningSystem()
        sensitive_memory = SensitiveMemory()
        emotion_system = EmotionSystem()
        preferences_manager = PreferencesManager()
        
        # Obter informações do usuário
        conversation_history = memory.get_conversation_history(user_id, limit=10)
        user_context = sensitive_memory.get_user_context(user_id)
        preferences = preferences_manager.get_all_preferences(user_id)
        
        # Construir prompt otimizado para Qwen
        system_prompt = f"""<|im_start|>system
Você é Eron, uma assistente IA inteligente e prestativa.

Contexto do usuário: {user_context}
Preferências: {preferences}
Plataforma: {platform}

Instruções:
- Seja natural e conversacional
- Use o contexto para personalizar respostas
- Mantenha consistência com conversas anteriores
- Responda de forma útil e informativa
<|im_end|>"""
        
        # Histórico de conversa
        messages = []
        for msg in conversation_history[-5:]:  # Últimas 5 mensagens
            messages.append(f"<|im_start|>user\n{msg.get('user_message', '')}<|im_end|>")
            messages.append(f"<|im_start|>assistant\n{msg.get('bot_response', '')}<|im_end|>")
        
        # Mensagem atual
        messages.append(f"<|im_start|>user\n{user_message}<|im_end|>")
        messages.append("<|im_start|>assistant")
        
        # Prompt completo
        full_prompt = system_prompt + "\n".join(messages)
        
        # Configurar requisição para LM Studio
        lm_studio_url = os.getenv('LM_STUDIO_API_URL', 'http://localhost:1234/v1/completions')
        
        payload = {
            "prompt": full_prompt,
            "max_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.9,
            "stream": False,
            "stop": ["<|im_end|>", "<|im_start|>"]
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Fazer requisição
        response = requests.post(lm_studio_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            bot_response = response_data.get('choices', [{}])[0].get('text', '').strip()
            
            if bot_response:
                # Salvar na memória
                memory.add_message(user_id, user_message, bot_response, platform)
                
                # Sistema de aprendizagem rápida
                fast_learning.learn_from_interaction(user_id, user_message, bot_response)
                
                # Detectar emoções
                emotion_system.detect_and_save_emotion(user_id, user_message)
                
                return bot_response
        
        return "Desculpe, não consegui processar sua mensagem. Tente novamente."
        
    except Exception as e:
        print(f"Erro em get_llm_response: {e}")
        return "Desculpe, ocorreu um erro interno. Tente novamente."

# Criar aplicação
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)