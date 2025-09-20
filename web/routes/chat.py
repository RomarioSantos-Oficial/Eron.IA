"""
Blueprint de chat - Interface de conversação e IA
"""
from flask import Blueprint, render_template, request, session, jsonify
from functools import wraps

# Criar blueprint
chat_bp = Blueprint('chat', __name__)

def login_required(f):
    """Decorador para páginas que requerem login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@chat_bp.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    """Interface principal de chat"""
    if request.method == 'POST':
        user_message = request.form.get('message', '').strip()
        user_id = session.get('user_id')
        
        if not user_message:
            return jsonify({'error': 'Mensagem vazia'}), 400
        
        try:
            # Importar função de resposta
            from app import get_llm_response
            
            # Obter resposta da IA
            response = get_llm_response(user_message, user_id, platform='web')
            
            if response:
                return jsonify({
                    'response': response,
                    'user_message': user_message
                })
            else:
                return jsonify({'error': 'Não foi possível obter resposta'}), 500
                
        except Exception as e:
            return jsonify({'error': f'Erro interno: {str(e)}'}), 500
    
    # GET request - mostrar página de chat
    return render_template('chat.html')

@chat_bp.route('/feedback', methods=['POST'])
@login_required
def feedback():
    """Endpoint para feedback de mensagens"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        feedback_type = data.get('type')  # 'positive' ou 'negative'
        message_id = data.get('message_id')
        message_content = data.get('message', '')
        
        if not feedback_type or feedback_type not in ['positive', 'negative']:
            return jsonify({'error': 'Tipo de feedback inválido'}), 400
        
        # Salvar feedback
        from src.fast_learning import FastLearningSystem
        fast_learning = FastLearningSystem()
        
        success = fast_learning.save_feedback(
            user_id=user_id,
            message_content=message_content,
            feedback_type=feedback_type,
            platform='web'
        )
        
        if success:
            return jsonify({'message': 'Feedback registrado com sucesso!'})
        else:
            return jsonify({'error': 'Erro ao salvar feedback'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500