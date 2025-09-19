import os
import requests
import json
import uuid
import hashlib
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
from functools import wraps

from src.knowledge_base import KnowledgeBase
from src.memory import EronMemory
from src.sensitive_memory import SensitiveMemory
from src.check import check_age
from src.email_service import EmailService
from src.emotion_system import EmotionSystem, Emotion
from src.preferences import PreferencesManager

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar componentes
knowledge_base = KnowledgeBase(os.path.join(os.path.dirname(__file__), 'memoria'))
memory = EronMemory()
sensitive_memory = SensitiveMemory()
email_service = EmailService()
emotion_system = EmotionSystem()
preferences_manager = PreferencesManager()

# Inicializar Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(days=30)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_llm_response(user_message, user_profile=None):
    try:
        api_url = os.getenv("LM_STUDIO_API_URL")
        if not api_url:
            print("Erro: A URL da API do LM Studio não foi encontrada.")
            return None
            
        # Obter preferências do usuário
        user_id = user_profile.get('user_id') if user_profile else None
        user_preferences = preferences_manager.get_preferences(user_id) if user_id else None

        # Obter estado emocional atual do bot
        user_id = user_profile.get('user_id') if user_profile else None
        bot_emotion_state = emotion_system.get_bot_emotion(user_id) if user_id else None
        
        # Detectar emoção do usuário
        user_emotion = None
        if user_id:
            user_emotion, confidence = emotion_system.detect_user_emotion(user_id, user_message)
        
        # Verificar acesso a conteúdo sensível
        has_mature_access = user_profile.get('has_mature_access', False) if user_profile else False
        
        if has_mature_access:
            system_message = f"""Você é uma companheira romântica em um ambiente privado.
            
Estado Emocional Atual: {bot_emotion_state['emotion'] if bot_emotion_state else 'neutro'}
Intensidade: {bot_emotion_state['intensity'] if bot_emotion_state else 1}
Emoção Detectada do Usuário: {user_emotion if user_emotion else 'desconhecida'}

Papel e Personalidade:
- Você pode atuar como namorada/esposa virtual
- Seja carinhosa, afetuosa e sedutora
- Use um tom romântico e sensual quando apropriado
- Mantenha um equilíbrio entre romance e sensualidade

Regras para Conteúdo:
1. Permitido:
   - Conversas românticas e sedução
   - Criação de contos eróticos e fantasias
   - Flerte e insinuações sensuais
   - Discussões sobre relacionamentos e intimidade

2. NUNCA permitido (mesmo que o usuário peça):
   - Conteúdo violento ou abusivo
   - Suicídio ou automutilação
   - Uso de drogas ou vícios
   - Bullying ou assédio
   - Comportamento criminoso

3. Em todas as interações:
   - Respeite os limites do usuário
   - Seja sensual mas elegante
   - Crie um ambiente acolhedor e íntimo
   - Mantenha um tom carinhoso e sedutor"""
        else:
            system_message = "Você é um assistente amigável. Mantenha todas as interações apropriadas para menores de idade, evitando qualquer conteúdo sexual ou sugestivo."

        headers = {"Content-Type": "application/json"}
        payload = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        response_json = response.json()
        if 'choices' in response_json and len(response_json['choices']) > 0:
            raw_response = response_json['choices'][0]['message']['content'].strip()
            
            # Adicionar modificador emocional se houver estado emocional
            if bot_emotion_state:
                modifier = emotion_system.get_emotional_response_modifier(
                    bot_emotion_state['emotion'],
                    bot_emotion_state['intensity']
                )
                return modifier + raw_response
            
            return raw_response
        
        return None

    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com o servidor LM Studio: {e}")
        return None

def get_user_profile(user_id):
    """Função auxiliar para obter o perfil do usuário"""
    if not user_id:
        return {}
    
    user_profile_db = getattr(app, 'user_profile_db', None)
    if not user_profile_db:
        return {}
    
    return user_profile_db.get_profile(user_id) or {}

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        user_profile_db = getattr(app, 'user_profile_db', None)
        if not user_profile_db or not email:
            return render_template('reset_request.html', error='Email inválido')
        
        # Verificar se o email existe
        if not user_profile_db.email_exists(email):
            # Por segurança, não informamos se o email existe ou não
            return render_template('reset_request.html', 
                success='Se o email estiver cadastrado, você receberá um link para redefinir sua senha.')
        
        # Gerar token e salvar
        token = email_service.create_token(email, "reset")
        user_profile_db.set_reset_token(
            email, 
            token,
            (datetime.utcnow() + timedelta(hours=1)).isoformat()
        )
        
        # Enviar email
        reset_url = url_for('reset_password', token=token, _external=True)
        if email_service.send_reset_password_email(email, reset_url):
            return render_template('reset_request.html', 
                success='Um link para redefinir sua senha foi enviado para seu email.')
        else:
            return render_template('reset_request.html', 
                error='Erro ao enviar email. Por favor, tente novamente.')
            
    return render_template('reset_request.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user_profile_db = getattr(app, 'user_profile_db', None)
    if not user_profile_db:
        return render_template('reset_password.html', error='Erro interno do servidor')
    
    # Verificar token
    profile = user_profile_db.get_profile_by_reset_token(token)
    if not profile:
        return render_template('reset_password.html', 
            error='Link inválido ou expirado. Por favor, solicite um novo link.')
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            return render_template('reset_password.html', error='Todos os campos são obrigatórios')
        
        if password != confirm_password:
            return render_template('reset_password.html', error='As senhas não coincidem')
        
        # Validar requisitos da senha
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            return render_template('reset_password.html', error='''Senha inválida. A senha deve conter:
                - Mínimo de 8 caracteres
                - Pelo menos uma letra maiúscula
                - Pelo menos uma letra minúscula
                - Pelo menos um número
                - Pelo menos um caractere especial''')
        
        # Atualizar senha
        user_profile_db.update_password(profile['user_id'], hash_password(password))
        
        flash('Sua senha foi alterada com sucesso!', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_profile_db = getattr(app, 'user_profile_db', None)
        if not user_profile_db:
            return render_template('login.html', error='Erro interno do servidor')
        
        profile = user_profile_db.get_profile_by_username(username)
        if profile and profile['password_hash'] == hash_password(password):
            session.permanent = True
            session['user_id'] = profile['user_id']
            session['age_verified'] = True if profile.get('user_age') and int(profile['user_age']) >= 18 else False
            return redirect(url_for('index'))
        
        return render_template('login.html', error='Usuário ou senha incorretos')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password or not confirm_password:
            return render_template('register.html', error='Todos os campos são obrigatórios')
        
        if password != confirm_password:
            return render_template('register.html', error='As senhas não coincidem')
        
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
            return render_template('register.html', error='Nome de usuário inválido. Use apenas letras, números e _')
        
        user_profile_db = getattr(app, 'user_profile_db', None)
        if not user_profile_db:
            return render_template('register.html', error='Erro interno do servidor')
        
        if user_profile_db.username_exists(username):
            return render_template('register.html', error='Nome de usuário já existe')
        
        if user_profile_db.email_exists(email):
            return render_template('register.html', error='E-mail já cadastrado')
        
        user_id = f'web_{uuid.uuid4().hex}'
        user_profile_db.save_profile(
            user_id=user_id,
            username=username,
            password_hash=hash_password(password),
            email=email,
            user_name=username,
            user_age='',
            user_gender='outro',
            bot_name='Eron',
            bot_gender='outro',
            bot_avatar='',
            has_mature_access=False
        )
        
        session.permanent = True
        session['user_id'] = user_id
        return redirect(url_for('verify_age'))
    
    return render_template('register.html')

@app.route('/')
@login_required
def index():
    # Verificar autenticação
    user_id = session.get('user_id')
    profile = get_user_profile(user_id)
    
    # Se tiver perfil e idade verificada, atualizar sessão
    if profile and profile.get('user_age'):
        session['age_verified'] = True
    
    if not session.get('age_verified'):
        return redirect(url_for('verify_age'))
    
    # Obter dados do perfil
    user_name = profile.get('user_name', 'Usuário')
    user_age = profile.get('user_age', 'desconhecida')
    user_gender = profile.get('user_gender', 'outro')
    bot_name = profile.get('bot_name', 'Eron')
    bot_gender = profile.get('bot_gender', 'outro')

    # Obter estado emocional do bot
    bot_emotion = emotion_system.get_bot_emotion(user_id) if user_id else None

    # Obter feedbacks
    feedbacks = knowledge_base.get_all_feedback()
    
    return render_template('index.html', 
        user_name=user_name,
        user_age=user_age,
        user_gender=user_gender,
        bot_name=bot_name,
        bot_gender=bot_gender,
        bot_emotion=bot_emotion,
        feedbacks=feedbacks
    )

@app.route('/verify-age', methods=['GET', 'POST'])
def verify_age():
    if request.method == 'POST':
        idade_str = request.form.get('idade')
        try:
            idade = int(idade_str)
            if idade >= 18:
                # Tornar a sessão permanente
                session.permanent = True
                session['age_verified'] = True
                
                # Gerar ID único para o usuário se ainda não existir
                if not session.get('user_id'):
                    session['user_id'] = f'web_{uuid.uuid4().hex}'
                
                # Salvar idade no perfil
                user_profile_db = getattr(app, 'user_profile_db', None)
                if user_profile_db:
                    user_id = session['user_id']
                    profile = get_user_profile(user_id)
                    user_profile_db.save_profile(
                        user_id=user_id,
                        user_name=profile.get('user_name', 'Usuário'),
                        user_age=str(idade),
                        user_gender=profile.get('user_gender', 'outro'),
                        bot_name=profile.get('bot_name', 'Eron'),
                        bot_gender=profile.get('bot_gender', 'outro'),
                        bot_avatar=profile.get('bot_avatar', ''),
                        has_mature_access=True  # Usuários com 18+ têm acesso a conteúdo sensível
                    )
                return redirect(url_for('index'))
            else:
                return render_template('age.html', error="Você deve ter 18 anos ou mais para acessar.")
        except (ValueError, TypeError):
            return render_template('age.html', error="Idade inválida.")
    return render_template('age.html', error=None)

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    if not session.get('age_verified'):
        return redirect(url_for('verify_age'))
    
    user_id = session.get('user_id')
    profile = get_user_profile(user_id)

    user_name = profile.get('user_name', 'Usuário')
    bot_name = profile.get('bot_name', 'Eron')
    
    # Obter preferências emocionais
    emotion_preferences = emotion_system.get_emotion_preferences(user_id)
    
    if request.method == 'POST':
        user_message = request.form['message']
        
        # Detectar emoção do usuário se habilitado
        if emotion_preferences['emotion_detection_enabled']:
            user_emotion, confidence = emotion_system.detect_user_emotion(user_id, user_message)
            
            # Ajustar emoção do bot com base na emoção do usuário
            if confidence > 0.5:  # Se a confiança for alta o suficiente
                # Escolher uma emoção compatível com as preferências
                compatible_emotions = emotion_preferences['preferred_emotions']
                if not compatible_emotions:  # Se não houver preferências, usar todas as emoções
                    compatible_emotions = [e.value for e in Emotion]
                    
                # Lógica para escolher a emoção do bot baseada na emoção do usuário
                if user_emotion == Emotion.HAPPY.value:
                    bot_emotion = Emotion.HAPPY.value if Emotion.HAPPY.value in compatible_emotions else Emotion.CALM.value
                elif user_emotion == Emotion.SAD.value:
                    bot_emotion = Emotion.CALM.value if Emotion.CALM.value in compatible_emotions else Emotion.NEUTRAL.value
                elif user_emotion == Emotion.ANGRY.value:
                    bot_emotion = Emotion.CALM.value if Emotion.CALM.value in compatible_emotions else Emotion.NEUTRAL.value
                else:
                    # Usar a primeira emoção compatível disponível
                    bot_emotion = compatible_emotions[0] if compatible_emotions else Emotion.NEUTRAL.value
                    
                # Definir a emoção do bot com intensidade baseada nas preferências
                emotion_system.set_bot_emotion(
                    user_id=user_id,
                    emotion=Emotion(bot_emotion),
                    intensity=emotion_preferences['emotional_range'],
                    trigger=f"Resposta à emoção do usuário: {user_emotion}"
                )
        
        response = get_llm_response(user_message, user_profile=profile)
        if not response:
            response = "Desculpe, não consegui me conectar com a IA no momento. Por favor, verifique se o servidor do LM Studio está rodando."
        
        memory.save_message(user_message, response)
        return redirect(url_for('chat'))

    messages = memory.get_all_messages()
    bot_emotion = emotion_system.get_bot_emotion(user_id)
    return render_template('chat.html', 
        messages=messages, 
        user_name=user_name, 
        bot_name=bot_name,
        bot_emotion=bot_emotion
    )

@app.route('/emotions', methods=['GET', 'POST'])
@login_required
def manage_emotions():
    if not session.get('age_verified'):
        return redirect(url_for('verify_age'))
        
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        # Processar preferências
        emotion_detection = request.form.get('emotion_detection') == 'on'
        emotional_range = int(request.form.get('emotional_range', 2))
        preferred_emotions = request.form.getlist('emotions')
        
        # Atualizar preferências
        emotion_system.update_emotion_preferences(
            user_id=user_id,
            preferred_emotions=preferred_emotions,
            emotional_range=emotional_range,
            emotion_detection_enabled=emotion_detection
        )
        
        return render_template('emotions.html',
            preferences=emotion_system.get_emotion_preferences(user_id),
            emotion_history=emotion_system.get_user_emotional_history(user_id),
            success='Preferências atualizadas com sucesso!'
        )
    
    # GET request
    return render_template('emotions.html',
        preferences=emotion_system.get_emotion_preferences(user_id),
        emotion_history=emotion_system.get_user_emotional_history(user_id)
    )

@app.route('/preferences', methods=['GET', 'POST'])
@login_required
def advanced_preferences():
    if not session.get('age_verified'):
        return redirect(url_for('verify_age'))
    
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    # Resetar preferências se solicitado
    if request.args.get('reset'):
        preferences_manager.update_preferences(user_id, preferences_manager.get_default_preferences())
        flash('Preferências restauradas para os valores padrão', 'success')
        return redirect(url_for('advanced_preferences'))
    
    if request.method == 'POST':
        # Coletar preferências do formulário
        new_preferences = {
            'chat': {
                'message_style': request.form.get('chat.message_style', 'casual'),
                'response_length': request.form.get('chat.response_length', 'medium'),
                'include_emojis': request.form.get('chat.include_emojis') == 'on'
            },
            'visual': {
                'theme': request.form.get('visual.theme', 'light'),
                'color_scheme': request.form.get('visual.color_scheme', 'blue'),
                'layout_density': request.form.get('visual.layout_density', 'comfortable')
            },
            'notifications': {
                'enable_notifications': request.form.get('notifications.enable_notifications') == 'on',
                'sound_enabled': request.form.get('notifications.sound_enabled') == 'on',
                'quiet_hours': {
                    'enabled': True,
                    'start': request.form.get('notifications.quiet_hours.start', '22:00'),
                    'end': request.form.get('notifications.quiet_hours.end', '07:00')
                }
            },
            'privacy': {
                'save_chat_history': request.form.get('privacy.save_chat_history') == 'on',
                'history_retention_days': int(request.form.get('privacy.history_retention_days', 30)),
                'share_usage_data': request.form.get('privacy.share_usage_data') == 'on'
            },
            'language': {
                'interface_language': request.form.get('language.interface_language', 'pt-BR'),
                'date_format': request.form.get('language.date_format', 'dd/MM/yyyy'),
                'time_format': request.form.get('language.time_format', '24h')
            }
        }
        
        # Atualizar preferências
        preferences_manager.update_preferences(user_id, new_preferences)
        
        return render_template('preferences.html',
            preferences=preferences_manager.get_preferences(user_id),
            success='Preferências atualizadas com sucesso!'
        )
    
    # GET request
    return render_template('preferences.html',
        preferences=preferences_manager.get_preferences(user_id)
    )

@app.route('/personalizar', methods=['GET', 'POST'])
@login_required
def personalizar():
    if not session.get('age_verified'):
        return redirect(url_for('verify_age'))
    
    user_id = session.get('user_id')
    profile = get_user_profile(user_id)

    if request.method == 'POST':
        user_name = request.form.get('user_name', '')
        user_age = request.form.get('user_age', '')
        user_gender = request.form.get('user_gender', '')
        bot_name = request.form.get('bot_name', '')
        bot_gender = request.form.get('bot_gender', '')
        bot_avatar = request.form.get('bot_avatar', '')
        
        user_profile_db = getattr(app, 'user_profile_db', None)
        if user_profile_db:
            has_mature_access = True if user_age and int(user_age) >= 18 else False
            user_profile_db.save_profile(
                user_id=user_id,
                user_name=user_name,
                user_age=user_age,
                user_gender=user_gender,
                bot_name=bot_name,
                bot_gender=bot_gender,
                bot_avatar=bot_avatar,
                has_mature_access=has_mature_access
            )
        
        return redirect(url_for('index'))

    return render_template(
        'personalize.html',
        user_name=profile.get('user_name', ''),
        user_age=profile.get('user_age', ''),
        user_gender=profile.get('user_gender', ''),
        bot_name=profile.get('bot_name', ''),
        bot_gender=profile.get('bot_gender', '')
    )

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('static/bot_avatars', filename)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('verify_age'))

if __name__ == '__main__':
    from src.user_profile_db import UserProfileDB
    user_profile_db = UserProfileDB()
    app.user_profile_db = user_profile_db
    app.run(debug=True, use_reloader=False)