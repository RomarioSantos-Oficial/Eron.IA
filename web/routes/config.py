"""
Blueprint de configurações - Preferências, personalização, emoções
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from functools import wraps

# Criar blueprint
config_bp = Blueprint('config', __name__)

def login_required(f):
    """Decorador para páginas que requerem login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@config_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    """Página de preferências"""
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        try:
            from core.preferences import PreferencesManager
            preferences_manager = PreferencesManager()
            
            # Coletar dados do formulário
            preferences_data = {
                'chat_style': request.form.get('chat_style', 'casual'),
                'response_length': request.form.get('response_length', 'medium'),
                'emoji_usage': request.form.get('emoji_usage', 'moderate'),
                'formality': request.form.get('formality', 'informal'),
                'creativity': request.form.get('creativity', 'balanced'),
                'memory_level': request.form.get('memory_level', 'full')
            }
            
            # Salvar preferências
            success = True
            for pref_key, pref_value in preferences_data.items():
                if not preferences_manager.set_preference(user_id, pref_key, pref_value):
                    success = False
                    break
            
            if success:
                flash('Preferências salvas com sucesso!', 'success')
            else:
                flash('Erro ao salvar algumas preferências', 'error')
                
        except Exception as e:
            flash('Erro interno ao salvar preferências', 'error')
        
        return redirect(url_for('config.preferences'))
    
    # GET - carregar preferências atuais
    try:
        from core.preferences import PreferencesManager
        preferences_manager = PreferencesManager()
        current_preferences = preferences_manager.get_all_preferences(user_id)
    except:
        current_preferences = {}
    
    return render_template('preferences.html', preferences=current_preferences)

@config_bp.route('/emotions', methods=['GET', 'POST'])
@login_required
def emotions():
    """Página de configurações de emoções"""
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        try:
            from core.emotion_system import EmotionSystem
            emotion_system = EmotionSystem()
            
            # Configurações de emoção
            emotion_settings = {
                'detection_enabled': request.form.get('detection_enabled') == 'on',
                'detection_sensitivity': request.form.get('detection_sensitivity', 'medium'),
                'response_emotional': request.form.get('response_emotional') == 'on',
                'emotion_memory': request.form.get('emotion_memory') == 'on'
            }
            
            # Salvar configurações
            success = emotion_system.save_user_settings(user_id, emotion_settings)
            
            if success:
                flash('Configurações de emoção salvas!', 'success')
            else:
                flash('Erro ao salvar configurações', 'error')
                
        except Exception as e:
            flash('Erro interno ao salvar configurações de emoção', 'error')
        
        return redirect(url_for('config.emotions'))
    
    # GET - carregar configurações atuais
    try:
        from core.emotion_system import EmotionSystem
        emotion_system = EmotionSystem()
        emotion_data = {
            'settings': emotion_system.get_user_settings(user_id),
            'current_emotion': emotion_system.get_current_emotion(user_id),
            'recent_emotions': emotion_system.get_recent_emotions(user_id, limit=10)
        }
    except:
        emotion_data = {'settings': {}, 'current_emotion': None, 'recent_emotions': []}
    
    return render_template('emotions.html', emotion_data=emotion_data)

@config_bp.route('/personalizar', methods=['GET', 'POST'])
@login_required
def personalize():
    """Página de personalização do bot"""
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        try:
            from core.user_profile_db import UserProfileDB
            profile_db = UserProfileDB()
            
            # Dados de personalização
            profile_data = {
                'user_name': request.form.get('user_name', ''),
                'user_age': request.form.get('user_age', ''),
                'user_gender': request.form.get('user_gender', ''),
                'bot_name': request.form.get('bot_name', 'Eron'),
                'bot_gender': request.form.get('bot_gender', 'feminine'),
                'personality': request.form.get('personality', 'friendly'),
                'language': request.form.get('language', 'portuguese'),
                'interests': request.form.getlist('interests')
            }
            
            # Salvar perfil
            success = profile_db.update_profile(user_id, profile_data)
            
            if success:
                flash('Personalização salva com sucesso!', 'success')
            else:
                flash('Erro ao salvar personalização', 'error')
                
        except Exception as e:
            flash('Erro interno ao salvar personalização', 'error')
        
        return redirect(url_for('config.personalize'))
    
    # GET - carregar dados atuais
    try:
        from core.user_profile_db import UserProfileDB
        profile_db = UserProfileDB()
        current_profile = profile_db.get_profile(user_id)
    except:
        current_profile = {}
    
    return render_template('personalize.html', profile=current_profile)
