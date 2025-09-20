"""
Sistema Web Adulto - Rotas Unificadas
Integração completa com sistema Telegram existente
Mantém funcionalidades normais para menores
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import json
import sqlite3
from datetime import datetime
import os
import sys

# Adicionar o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.adult_personality_system import AdultPersonalitySystem
    from core.adult_vocabulary_trainer import AdultVocabularyTrainer, InteractiveTrainer
    from telegram_bot.handlers.adult_integration import get_adult_personality_context
    from src.user_profile_db import UserProfileDB
    HAS_ALL_MODULES = True
except ImportError as e:
    print(f"Aviso: Algumas importações falharam - {e}")
    # Fallback para sistema de desenvolvimento
    AdultPersonalitySystem = None
    AdultVocabularyTrainer = None
    InteractiveTrainer = None
    get_adult_personality_context = None  
    UserProfileDB = None
    HAS_ALL_MODULES = False
except ImportError as e:
    print(f"Aviso: Algumas importações falharam - {e}")
    # Fallback para desenvolvimento
    AdultPersonalitySystem = None
    AdultVocabularyTrainer = None

adult_bp = Blueprint('adult', __name__, url_prefix='/adult')

class WebAdultSystem:
    """Sistema web integrado com funcionalidades adultas"""
    
    def __init__(self):
        """Inicializa o sistema web adulto"""
        try:
            self.personality_system = AdultPersonalitySystem() if AdultPersonalitySystem else None
            self.vocabulary_trainer = AdultVocabularyTrainer() if AdultVocabularyTrainer else None
            self.interactive_trainer = InteractiveTrainer() if AdultVocabularyTrainer else None
            self.user_db = UserProfileDB()
        except Exception as e:
            print(f"Erro ao inicializar WebAdultSystem: {e}")
            self.personality_system = None
            self.vocabulary_trainer = None
            self.interactive_trainer = None
            self.user_db = None
    
    def is_adult_user(self, user_id):
        """Verifica se o usuário é maior de idade"""
        try:
            if not self.user_db:
                return False
            
            profile = self.user_db.get_user_profile(user_id)
            if not profile:
                return False
            
            # Verifica idade ou configuração adulta
            birth_date = profile.get('birth_date')
            adult_enabled = profile.get('adult_mode_enabled', False)
            
            if adult_enabled and birth_date:
                from datetime import date
                today = date.today()
                birth = datetime.strptime(birth_date, '%Y-%m-%d').date()
                age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
                return age >= 18
            
            return adult_enabled
        except Exception as e:
            print(f"Erro ao verificar idade: {e}")
            return False
    
    def get_user_adult_config(self, user_id):
        """Obtém configuração adulta do usuário"""
        try:
            if not self.personality_system:
                return None
            
            config = self.personality_system.get_user_config(user_id)
            return config if config else {
                'personality': 'none',
                'intensity': 1,
                'mood': 'normal',
                'active': False
            }
        except Exception as e:
            print(f"Erro ao obter configuração: {e}")
            return None
    
    def update_user_adult_config(self, user_id, config):
        """Atualiza configuração adulta do usuário"""
        try:
            if not self.personality_system:
                return False
            
            self.personality_system.set_user_config(user_id, config)
            return True
        except Exception as e:
            print(f"Erro ao atualizar configuração: {e}")
            return False

# Instância global do sistema
web_adult_system = WebAdultSystem()

@adult_bp.before_request
def check_adult_access():
    """Middleware para verificar acesso adulto"""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Permite acesso para verificação de idade
    allowed_endpoints = ['adult.age_verification', 'adult.verify_age']
    if request.endpoint in allowed_endpoints:
        return None
    
    # Verifica se é usuário adulto
    if not web_adult_system.is_adult_user(user_id):
        return redirect(url_for('adult.age_verification'))
    
    return None

@adult_bp.route('/age_verification')
def age_verification():
    """Página de verificação de idade"""
    return render_template('adult/age_verification.html')

@adult_bp.route('/verify_age', methods=['POST'])
def verify_age():
    """Processa verificação de idade"""
    try:
        birth_date = request.form.get('birth_date')
        user_id = session.get('user_id')
        
        if not birth_date or not user_id:
            return jsonify({'error': 'Dados inválidos'}), 400
        
        # Calcula idade
        from datetime import date
        today = date.today()
        birth = datetime.strptime(birth_date, '%Y-%m-%d').date()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        
        if age < 18:
            return jsonify({
                'error': 'Acesso negado. Sistema adulto disponível apenas para maiores de 18 anos.',
                'redirect': url_for('index')
            }), 403
        
        # Atualiza perfil do usuário
        if web_adult_system.user_db:
            profile = web_adult_system.user_db.get_user_profile(user_id) or {}
            profile.update({
                'birth_date': birth_date,
                'adult_mode_enabled': True,
                'age_verified': True
            })
            web_adult_system.user_db.save_user_profile(user_id, profile)
        
        return jsonify({
            'success': True,
            'redirect': url_for('adult.dashboard')
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro na verificação: {str(e)}'}), 500

@adult_bp.route('/dashboard')
def dashboard():
    """Dashboard principal do sistema adulto"""
    user_id = session.get('user_id')
    config = web_adult_system.get_user_adult_config(user_id)
    
    return render_template('adult/dashboard.html', 
                         config=config,
                         personalities=web_adult_system.personality_system.get_personality_types() if web_adult_system.personality_system else []
                         )

@adult_bp.route('/config')
def config_page():
    """Página de configuração de personalidade"""
    user_id = session.get('user_id')
    config = web_adult_system.get_user_adult_config(user_id)
    
    personalities = []
    if web_adult_system.personality_system:
        personalities = web_adult_system.personality_system.get_personality_types()
    
    return render_template('adult/config.html',
                         config=config,
                         personalities=personalities)

@adult_bp.route('/update_config', methods=['POST'])
def update_config():
    """Atualiza configuração do usuário"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        config = {
            'personality': data.get('personality', 'none'),
            'intensity': int(data.get('intensity', 1)),
            'mood': data.get('mood', 'normal'),
            'active': data.get('active', False)
        }
        
        success = web_adult_system.update_user_adult_config(user_id, config)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Erro ao salvar configuração'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@adult_bp.route('/training')
def training_page():
    """Página de treinamento de vocabulário"""
    user_id = session.get('user_id')
    config = web_adult_system.get_user_adult_config(user_id)
    
    # Obter vocabulário atual
    vocabulary_stats = {}
    if web_adult_system.vocabulary_trainer:
        try:
            personality = config.get('personality', 'sedutora')
            vocabulary_stats = web_adult_system.vocabulary_trainer.get_vocabulary_stats(personality)
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
    
    return render_template('adult/training.html',
                         config=config,
                         vocabulary_stats=vocabulary_stats)

@adult_bp.route('/train_vocabulary', methods=['POST'])
def train_vocabulary():
    """Endpoint para treinamento de vocabulário"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        action = data.get('action')
        
        if not web_adult_system.vocabulary_trainer:
            return jsonify({'error': 'Sistema de treinamento não disponível'}), 500
        
        if action == 'quick_train':
            # Treinamento rápido
            personality = data.get('personality', 'sedutora')
            result = web_adult_system.vocabulary_trainer.batch_train_from_examples(personality)
            
            return jsonify({
                'success': True,
                'message': f'Treinamento concluído para {personality}',
                'details': result
            })
        
        elif action == 'add_word':
            # Adicionar palavra/frase
            personality = data.get('personality')
            word_type = data.get('word_type')
            word = data.get('word')
            intensity = int(data.get('intensity', 1))
            
            success = web_adult_system.vocabulary_trainer.add_vocabulary_item(
                personality, word_type, word, intensity
            )
            
            if success:
                return jsonify({'success': True, 'message': 'Vocabulário adicionado!'})
            else:
                return jsonify({'error': 'Erro ao adicionar vocabulário'}), 500
        
        elif action == 'get_suggestion':
            # Obter sugestão de resposta
            personality = data.get('personality', 'sedutora')
            context = data.get('context', '')
            
            suggestion = web_adult_system.vocabulary_trainer.generate_enhanced_prompt(
                personality, context
            )
            
            return jsonify({
                'success': True,
                'suggestion': suggestion
            })
        
        return jsonify({'error': 'Ação não reconhecida'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@adult_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submete feedback sobre respostas"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        response_text = data.get('response_text')
        rating = int(data.get('rating'))
        feedback_text = data.get('feedback_text', '')
        
        if web_adult_system.vocabulary_trainer:
            web_adult_system.vocabulary_trainer.add_feedback(
                response_text, rating, feedback_text, user_id
            )
            
            return jsonify({'success': True, 'message': 'Feedback registrado!'})
        else:
            return jsonify({'error': 'Sistema de feedback não disponível'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@adult_bp.route('/api/chat', methods=['POST'])
def adult_chat():
    """API de chat com funcionalidades adultas"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        message = data.get('message')
        if not message:
            return jsonify({'error': 'Mensagem vazia'}), 400
        
        # Obter contexto adulto
        adult_context = ""
        if web_adult_system.personality_system:
            adult_context = get_adult_personality_context(user_id)
        
        # Gerar resposta com vocabulário melhorado
        enhanced_prompt = message
        if web_adult_system.vocabulary_trainer:
            config = web_adult_system.get_user_adult_config(user_id)
            personality = config.get('personality', 'sedutora')
            enhanced_prompt = web_adult_system.vocabulary_trainer.generate_enhanced_prompt(
                personality, message
            )
        
        # Aqui você integraria com seu sistema de chat principal
        # Por enquanto, retorna uma resposta simples
        response = {
            'success': True,
            'response': f"[Modo Adulto Ativo] Resposta para: {message}",
            'enhanced_prompt': enhanced_prompt,
            'adult_context': adult_context
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@adult_bp.route('/api/status')
def status():
    """Status do sistema adulto"""
    user_id = session.get('user_id')
    config = web_adult_system.get_user_adult_config(user_id)
    
    return jsonify({
        'active': config.get('active', False) if config else False,
        'personality': config.get('personality', 'none') if config else 'none',
        'intensity': config.get('intensity', 1) if config else 1,
        'system_available': bool(web_adult_system.personality_system and web_adult_system.vocabulary_trainer)
    })

# Registrar o blueprint no app principal
def register_adult_routes(app):
    """Registra as rotas adultas no app Flask"""
    app.register_blueprint(adult_bp)
    return adult_bp