import os
import requests
import json
import uuid
import hashlib
import re
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory, flash, jsonify
from werkzeug.utils import secure_filename
from functools import wraps

from src.knowledge_base import KnowledgeBase
from src.memory import EronMemory
from src.fast_learning import FastLearningSystem
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
fast_learning = FastLearningSystem()
sensitive_memory = SensitiveMemory()
email_service = EmailService()
emotion_system = EmotionSystem()
preferences_manager = PreferencesManager()

# Inicializar Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-super-secret-key-for-dev')  # Carregar do .env
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

def detect_and_save_personalization(user_message, user_id):
    """
    Detecta se o usuário está fornecendo informações de personalização e salva automaticamente
    
    SISTEMA DE PERSONALIZAÇÃO ERON:
    - Nome padrão do bot: ERON (maiúsculo)  
    - Exemplo de personalização: "Joana" (quando usuário personaliza nome)
    - Opções disponíveis: nome do bot, gênero, personalidade, estilo linguagem, tópicos
    """
    user_profile_db = getattr(app, 'user_profile_db', None)
    if not user_profile_db:
        return False
    
    message_lower = user_message.lower().strip()
    updates = {}
    
    # Detectar nome do usuário
    name_patterns = [
        r"meu nome é (\w+)",
        r"me chamo (\w+)", 
        r"sou (\w+)",
        r"pode me chamar de (\w+)",
        r"^(\w+)$"  # Resposta de uma palavra apenas
    ]
    
    for pattern in name_patterns:
        import re
        match = re.search(pattern, message_lower)
        if match:
            name = match.group(1).capitalize()
            if len(name) > 1 and name not in ['não', 'sim', 'ok', 'obrigado', 'obrigada']:
                updates['user_name'] = name
                break
    
    # Detectar nome do assistente 
    bot_name_patterns = [
        r"se chame (\w+)",
        r"seu nome seja (\w+)",
        r"te chamar de (\w+)",
        r"quero que se chame (\w+)"
    ]
    
    for pattern in bot_name_patterns:
        match = re.search(pattern, message_lower)
        if match:
            bot_name = match.group(1).capitalize()
            if len(bot_name) > 1:
                updates['bot_name'] = bot_name
                break
    
    # Detectar personalidade do bot
    personality_patterns = {
        'amigável': ['amigável', 'amigo', 'amiga', 'legal', 'bacana', 'gentil'],
        'formal': ['formal', 'profissional', 'sério', 'séria', 'educado'],
        'casual': ['casual', 'descontraído', 'descontraída', 'relaxado', 'relaxada', 'informal'],
        'divertido': ['divertido', 'divertida', 'engraçado', 'engraçada', 'brincalhão', 'alegre'],
        'intelectual': ['intelectual', 'sábio', 'sábia', 'inteligente', 'culto', 'erudito']
    }
    
    for personality, keywords in personality_patterns.items():
        if any(keyword in message_lower for keyword in keywords):
            updates['bot_personality'] = personality
            break
    
    # Detectar estilo de linguagem
    language_patterns = {
        'simples': ['simples', 'fácil', 'direto', 'básico'],
        'técnico': ['técnico', 'detalhado', 'específico', 'científico'],
        'coloquial': ['coloquial', 'gírias', 'informal', 'descontraído'],
        'eloquente': ['eloquente', 'sofisticado', 'elegante', 'refinado']
    }
    
    for language, keywords in language_patterns.items():
        if any(keyword in message_lower for keyword in keywords):
            updates['bot_language'] = language
            break
    
    # Detectar tópicos de interesse (separados por vírgula)
    topics_patterns = [
        r"gosto de (.*)",
        r"me interesso por (.*)",
        r"quero falar sobre (.*)",
        r"meus interesses são (.*)",
        r"tópicos favoritos são (.*)"
    ]
    
    for pattern in topics_patterns:
        match = re.search(pattern, message_lower)
        if match:
            topics = match.group(1).strip()
            if len(topics) > 2:
                updates['preferred_topics'] = topics
                break
    
    # Se encontrou informações para salvar
    if updates:
        try:
            print(f"[DEBUG] Salvando automaticamente: {updates}")
            user_profile_db.save_profile(user_id=user_id, **updates)
            return True
        except Exception as e:
            print(f"[DEBUG] Erro ao salvar personalização automática: {e}")
            return False
    
    return False

def get_llm_response(user_message, user_profile=None, user_id=None):
    try:
        api_url = os.getenv("LM_STUDIO_API_URL")
        if not api_url:
            print("Erro: A URL da API do LM Studio não foi encontrada.")
            return None
        
        # SEMPRE consultar o banco de dados antes de responder
        if not user_profile and user_id:
            user_profile = get_or_create_user_profile(user_id)
        elif not user_profile:
            print("[DEBUG] Nenhum perfil fornecido e nenhum user_id para consulta")
            user_profile = {}
        
        # VERIFICAÇÃO ESPECÍFICA: Se perguntarem sobre o nome, responder diretamente com o nome da personalização
        message_lower = user_message.lower().strip()
        name_questions = [
            'qual é seu nome', 'qual seu nome', 'como você se chama', 'qual é o seu nome',
            'seu nome é', 'você se chama', 'como te chamo', 'qual o seu nome'
        ]
        
        if any(question in message_lower for question in name_questions):
            bot_name = user_profile.get('bot_name', 'ERON') if user_profile else 'ERON'
            if bot_name and bot_name != '':
                return f"Meu nome é {bot_name}! 😊"
            else:
                return "Ainda não tenho um nome personalizado. Como você gostaria que eu me chamasse?"
        
        # Verificar se a personalização está completa
        personalization_complete, missing_info = check_personalization_complete(user_profile)
        
        print(f"[DEBUG] Personalização completa: {personalization_complete}")
        if not personalization_complete:
            print(f"[DEBUG] Informações faltando: {missing_info}")
        
        # Se personalização incompleta, pedir informações automaticamente
        if not personalization_complete and isinstance(missing_info, list):
            if 'seu nome' in missing_info:
                return "Olá! Ainda não me disseram como você gostaria de ser chamado. Qual é o seu nome?"
            elif 'nome do assistente' in missing_info:
                return "E quanto a mim? Como você gostaria que eu me chamasse?"
            elif 'personalidade do assistente' in missing_info:
                return "Como você gostaria que eu me comportasse? Posso ser mais formal, casual, amigável... qual você prefere?"
            else:
                return f"Para te atender melhor, preciso saber: {', '.join(missing_info[:2])}. Pode me contar?"
        
        # FORÇAR uso do nome do banco - SOLUÇÃO À PROVA DE FALHAS
        bot_name = user_profile.get('bot_name', 'ERON') if user_profile else 'ERON'
        user_name = user_profile.get('user_name', 'usuário') if user_profile else 'usuário'
        
        # Se o nome ainda for padrão, procurar no banco novamente
        if bot_name in ['ERON', '', None]:
            # Busca direta no banco para garantir que pegue o nome correto
            user_profile_db = getattr(app, 'user_profile_db', None)
            if user_profile_db and user_id:
                fresh_profile = user_profile_db.get_profile(user_id)
                if fresh_profile and fresh_profile.get('bot_name') and fresh_profile.get('bot_name') != 'ERON':
                    bot_name = fresh_profile.get('bot_name')
                    user_profile = fresh_profile  # Atualizar o perfil com dados frescos
                    print(f"[DEBUG] Nome do bot encontrado no banco: '{bot_name}'")
        
        print(f"[DEBUG] Nome FINAL do bot que será usado: '{bot_name}'")
        
        # Personalização completa - usar informações do banco
        user_id = user_profile.get('user_id') if user_profile else user_id
        user_preferences = preferences_manager.get_preferences(user_id) if user_id else None

        # Aplicar preferências ao prompt
        style_instructions = ""
        if user_preferences:
            chat_prefs = user_preferences.get('chat', {})
            
            # Estilo da mensagem
            style = chat_prefs.get('message_style', 'casual')
            length = chat_prefs.get('response_length', 'medium')
            emojis = chat_prefs.get('include_emojis', False)
            
            style_map = {
                'casual': 'casual e descontraído',
                'formal': 'formal e profissional',
                'friendly': 'amigável e acolhedor'
            }
            
            length_map = {
                'short': 'de forma concisa e direta',
                'medium': 'com nível moderado de detalhes',
                'long': 'de forma detalhada e abrangente'
            }
            
            style_instructions = f"\nPor favor, responda {style_map.get(style, '')} e {length_map.get(length, '')}."
            if emojis:
                style_instructions += " Sinta-se à vontade para usar emojis apropriados."
            
        # Obter estado emocional atual do bot
        bot_emotion_state = emotion_system.get_bot_emotion(user_id) if user_id else None
        
        # Detectar emoção do usuário
        user_emotion = None
        if user_id:
            user_emotion, confidence = emotion_system.detect_user_emotion(user_id, user_message)
        
        # Obter contexto recente das conversas para continuidade
        recent_context = ""
        if user_id:
            full_context = memory.get_recent_context(user_id, limit=5)
            
            # Filtrar conversas de personalização antigas e respostas problemáticas para evitar confusão
            filtered_lines = []
            context_lines = full_context.split('\n') if full_context else []
            
            for line in context_lines:
                # Pular linhas que são perguntas de personalização antigas
                if any(phrase in line.lower() for phrase in [
                    'como você gostaria que eu me chamasse',
                    'para te atender melhor, preciso saber',
                    'nome do assistente',
                    'estilo de linguagem'
                ]):
                    continue
                
                # Pular respostas problemáticas que começam com o nome do bot
                if any(phrase in line for phrase in [
                    'Eu me chamo Maya',
                    'Eu me chamo Aina', 
                    'Eu me chamo ERON',
                    'Eu me chamo '
                ]):
                    # Remover apenas a parte problemática, manter o resto da resposta
                    if 'A capital do Brasil' in line or 'capital do Brasil' in line:
                        # Manter apenas a parte da resposta que responde à pergunta
                        line = line.split('A capital do Brasil')[0] + 'A capital do Brasil' + line.split('A capital do Brasil')[1] if 'A capital do Brasil' in line else line
                        line = line.replace('Eu me chamo Maya 💖', '').replace('Eu me chamo Aina 💖', '').replace('Eu me chamo ERON 💖', '').strip()
                        if line.startswith('A capital') or line.startswith('É ') or len(line.strip()) > 10:
                            filtered_lines.append(line)
                    elif len(line.replace('Eu me chamo Maya 💖', '').replace('Eu me chamo Aina 💖', '').replace('Eu me chamo ERON 💖', '').strip()) > 10:
                        # Se sobrar conteúdo útil após remover a apresentação, manter
                        cleaned_line = line.replace('Eu me chamo Maya 💖', '').replace('Eu me chamo Aina 💖', '').replace('Eu me chamo ERON 💖', '').strip()
                        filtered_lines.append(cleaned_line)
                    continue
                
                filtered_lines.append(line)
            
            recent_context = '\n'.join(filtered_lines)
            print(f"[DEBUG] Contexto filtrado: {recent_context[:100]}...")
        
        
        # Obter informações de personalização do perfil do usuário
        bot_name = user_profile.get('bot_name', 'ERON') if user_profile else 'ERON'
        user_name = user_profile.get('user_name', 'usuário') if user_profile else 'usuário'
        bot_gender = user_profile.get('bot_gender', 'outro') if user_profile else 'outro'
        bot_personality = user_profile.get('bot_personality', 'amigável') if user_profile else 'amigável'
        bot_language = user_profile.get('bot_language', 'informal') if user_profile else 'informal'
        preferred_topics = user_profile.get('preferred_topics', '') if user_profile else ''
        
        # Tratar caso especial de finish_personalization
        if bot_personality == 'finish_personalization':
            bot_personality = 'amigável'  # Usar personalidade padrão
            print(f"[DEBUG] Convertendo finish_personalization para personalidade padrão: amigável")
        
        # Debug: Imprimir informações do perfil
        print(f"[DEBUG] Perfil do usuário: {user_profile}")
        print(f"[DEBUG] Nome do bot extraído: '{bot_name}'")
        print(f"[DEBUG] Nome do usuário extraído: '{user_name}'")
        
        # 🚀 OTIMIZAÇÕES PARA QWEN2.5-4B
        optimization_hints = fast_learning.optimize_for_qwen(user_message, user_profile)
        
        # Construir instruções de personalização OTIMIZADAS PARA QWEN
        personality_instructions = f"""<|im_start|>system
Você é um assistente IA inteligente e personalizado. Use as informações abaixo para responder de forma natural e contextualizada:

📋 PERFIL ATUAL:
• Nome: {bot_name}
• Falando com: {user_name}
• Gênero: {bot_gender}  
• Personalidade: {bot_personality}
• Estilo: {bot_language}

🎯 DIRETRIZES DE RESPOSTA:
• Responda de forma natural e conversacional
• Use o nome do usuário quando apropriado
• Mantenha consistência com sua personalidade
• Seja útil e preciso nas informações

🧠 OTIMIZAÇÕES DE APRENDIZADO:
{chr(10).join(f'• {hint}' for hint in optimization_hints) if optimization_hints else '• Resposta baseada no perfil atual'}

IMPORTANTE SOBRE PERSONALIZAÇÃO:
- Se o usuário pedir para mudar seu nome, aceite imediatamente
- Se disser "quero que se chame [nome]", responda: "Perfeito! Agora me chamo [nome]!"
- Seja flexível e adaptável às preferências do usuário
- Seu nome atual é: {bot_name}
- NUNCA mencione seu nome nas conversas EXCETO quando perguntado diretamente
- SOMENTE quando perguntarem "qual é seu nome?" ou "como você se chama?", responda: "Meu nome é {bot_name}"
- Se te chamarem pelo nome seguido de uma pergunta (ex: "Maya, qual é..."), responda APENAS a pergunta SEM se apresentar
- NUNCA comece respostas com seu nome ou se apresente desnecessariamente
- Responda perguntas normais SEM mencionar seu nome
<|im_end|>"""

        if preferred_topics:
            personality_instructions += f"\n- Tópicos preferidos: {preferred_topics}"
            
        if recent_context:
            personality_instructions += f"\n\nCONVERSAS ANTERIORES:\n{recent_context}"
            
        print(f"[DEBUG] Instruções FORÇADAS para IA:")
        print(personality_instructions)

        # Verificar acesso a conteúdo sensível
        has_mature_access = user_profile.get('has_mature_access', False) if user_profile else False
        
        if has_mature_access:
            system_message = f"""{personality_instructions}

Você é uma companheira romântica em um ambiente privado.
            
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
            system_message = f"""{personality_instructions}

Você é um assistente amigável. Mantenha todas as interações apropriadas para menores de idade, evitando qualquer conteúdo sexual ou sugestivo."""

        # Adicionar instruções de estilo ao system_message
        system_message = system_message + style_instructions

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
    
    # Acessa a instância do banco de dados do aplicativo Flask
    user_profile_db = getattr(app, 'user_profile_db', None)
    if not user_profile_db:
        # Se não encontrar, tenta criar uma nova instância (fallback)
        from src.user_profile_db import UserProfileDB
        user_profile_db = UserProfileDB()
        app.user_profile_db = user_profile_db

    return user_profile_db.get_profile(user_id) or {}

def check_personalization_complete(user_profile):
    """Verifica se o usuário tem personalização completa"""
    if not user_profile:
        return False, "Perfil não encontrado"
    
    # Campos obrigatórios para personalização completa
    required_fields = {
        'bot_name': 'nome do assistente',
        'user_name': 'seu nome', 
        'bot_personality': 'personalidade do assistente',
        'bot_language': 'estilo de linguagem'
    }
    
    missing_fields = []
    for field, description in required_fields.items():
        value = user_profile.get(field, '')
        
        # Verificações especiais para cada campo
        if field == 'bot_name':
            if not value or value in ['', 'Eron', 'ERON']:
                missing_fields.append(description)
        elif field == 'user_name':
            if not value or value in ['', 'usuário', 'Usuário']:
                missing_fields.append(description)
        elif field == 'bot_personality':
            # Aceitar finish_personalization como válido
            if not value or value in ['', 'finish_personalization']:
                # Se for finish_personalization, usar personalidade padrão
                if value == 'finish_personalization':
                    continue  # Não adicionar como campo faltando
                else:
                    missing_fields.append(description)
        elif field == 'bot_language':
            if not value or value == '':
                missing_fields.append(description)
    
    if missing_fields:
        return False, missing_fields
    
    return True, "Personalização completa"

def get_or_create_user_profile(user_id, platform="web"):
    """Obtém o perfil do usuário ou cria um novo se não existir"""
    profile = get_user_profile(user_id)
    
    if not profile:
        # Criar novo perfil básico
        user_profile_db = getattr(app, 'user_profile_db', None)
        if user_profile_db:
            basic_profile = {
                'user_id': user_id,
                'username': f'{platform}_{user_id}',
                'password_hash': '',
                'email': '',
                'user_name': '',
                'user_age': '18',
                'user_gender': 'outro',
                'bot_name': '',
                'bot_gender': 'outro',
                'bot_avatar': '',
                'has_mature_access': False,
                'bot_personality': '',
                'bot_language': '',
                'preferred_topics': ''
            }
            try:
                user_profile_db.save_profile(**basic_profile)
                profile = basic_profile
            except Exception as e:
                print(f"Erro ao criar perfil básico: {e}")
                profile = basic_profile
    
    return profile

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
            
            # Se não tiver idade, vai para a personalização
            if not profile.get('user_age'):
                flash('Bem-vindo! Por favor, complete seu perfil.', 'info')
                return redirect(url_for('personalizar'))
            
            # Se tiver idade, vai para o chat
            return redirect(url_for('chat'))
            
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
        profile = {
            'user_id': user_id,
            'username': username,
            'password_hash': hash_password(password),
            'email': email,
            'user_name': username,
            'user_age': '',
            'user_gender': 'outro',
            'bot_name': 'Eron',
            'bot_gender': 'outro',
            'bot_avatar': '',
            'has_mature_access': False
        }
        
        try:
            user_profile_db.save_profile(**profile)
            session.permanent = True
            session['user_id'] = user_id
            flash('Cadastro realizado com sucesso! Agora, personalize seu perfil.', 'success')
            return redirect(url_for('personalizar'))
        except Exception as e:
            return render_template('register.html', error=f'Erro ao salvar perfil: {e}')
    
    return render_template('register.html')

@app.route('/')
def index():
    if 'user_id' in session:
        profile = get_user_profile(session['user_id'])
        # Se o usuário está logado, mas não completou a personalização, redirecione
        if not profile.get('user_age'):
            return redirect(url_for('personalizar'))
        return redirect(url_for('chat'))
    return render_template('landing.html')



@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    user_id = session.get('user_id')
    print(f"[DEBUG CHAT] User ID da sessão: {user_id}")  # Debug
    profile = get_user_profile(user_id)
    print(f"[DEBUG CHAT] Perfil carregado: {profile}")  # Debug

    # Se o perfil não estiver completo, redireciona para a personalização
    if not profile.get('user_age'):
        flash('Por favor, complete seu perfil antes de acessar o chat.', 'warning')
        return redirect(url_for('personalizar'))

    user_name = profile.get('user_name', 'Usuário')
    bot_name = profile.get('bot_name', 'Eron')
    
    # Obter preferências emocionais
    emotion_preferences = emotion_system.get_emotion_preferences(user_id)
    
    if request.method == 'POST':
        user_message = request.form['message']
        
        # DETECTAR E SALVAR AUTOMATICAMENTE informações de personalização
        personalization_saved = detect_and_save_personalization(user_message, user_id)
        if personalization_saved:
            print(f"[DEBUG] Personalização detectada e salva! Recarregando perfil...")
            # FORÇAR recarga completa do perfil
            user_profile_db = getattr(app, 'user_profile_db', None) 
            if user_profile_db:
                profile = user_profile_db.get_profile(user_id)
                print(f"[DEBUG] Perfil recarregado após personalização: {profile}")
            else:
                profile = get_user_profile(user_id)
        
        # Detectar emoção do usuário se habilitado
        if emotion_preferences['emotion_detection_enabled']:
            user_emotion, confidence = emotion_system.detect_user_emotion(user_id, user_message)
            
            # Ajustar emoção do bot com base na emoção do usuário
            if confidence > 0.5:
                compatible_emotions = emotion_preferences['preferred_emotions']
                if not compatible_emotions:
                    compatible_emotions = [e.value for e in Emotion]
                    
                if user_emotion == Emotion.HAPPY.value:
                    bot_emotion = Emotion.HAPPY.value if Emotion.HAPPY.value in compatible_emotions else Emotion.CALM.value
                elif user_emotion == Emotion.SAD.value:
                    bot_emotion = Emotion.CALM.value if Emotion.CALM.value in compatible_emotions else Emotion.NEUTRAL.value
                elif user_emotion == Emotion.ANGRY.value:
                    bot_emotion = Emotion.CALM.value if Emotion.CALM.value in compatible_emotions else Emotion.NEUTRAL.value
                else:
                    bot_emotion = compatible_emotions[0] if compatible_emotions else Emotion.NEUTRAL.value
                    
                emotion_system.set_bot_emotion(
                    user_id=user_id,
                    emotion=Emotion(bot_emotion),
                    intensity=emotion_preferences['emotional_range'],
                    trigger=f"Resposta à emoção do usuário: {user_emotion}"
                )
        
        # Usar o perfil atualizado para gerar resposta
        response = get_llm_response(user_message, user_profile=profile, user_id=user_id)
        if not response:
            response = "Desculpe, não consegui me conectar com a IA no momento. Por favor, verifique se o servidor do LM Studio está rodando."
        
        # Salvar na memória com user_id
        memory.save_message(user_message, response, user_id)
        
        # 🧠 APRENDIZADO ACELERADO: Salvar padrões de resposta
        fast_learning.learn_response_pattern(user_id, user_message, response)
        
        # Salvar contexto inteligente para futuras conversas
        topic = fast_learning._extract_main_topic(user_message)
        context_data = f"{user_message[:100]}... → {response[:100]}..."
        fast_learning.save_smart_context(user_id, topic, context_data, importance=1.5)
        
        return redirect(url_for('chat'))

    # Carregar mensagens específicas do usuário
    messages = memory.get_all_messages(user_id)
    bot_emotion = emotion_system.get_bot_emotion(user_id)
    return render_template('chat.html', 
        messages=messages, 
        user_name=user_name, 
        bot_name=bot_name,
        bot_emotion=bot_emotion
    )

@app.route('/feedback', methods=['POST'])
def feedback():
    """Endpoint para receber feedback do usuário sobre respostas"""
    data = request.get_json()
    message_id = data.get('message_id')
    feedback_type = data.get('feedback')  # 'positive' ou 'negative'
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não logado'})
    
    user_id = session['user_id']
    
    # Salvar feedback no sistema de aprendizado acelerado
    try:
        with sqlite3.connect('memoria/eron_memory.db') as conn:
            message_data = conn.execute(
                'SELECT user_message, eron_response FROM messages WHERE id = ? AND user_id = ?',
                (message_id, user_id)
            ).fetchone()
            
            if message_data:
                # Aprender com o feedback
                fast_learning.learn_response_pattern(
                    user_id, 
                    message_data[0], 
                    message_data[1], 
                    user_feedback=feedback_type
                )
                
                return jsonify({'success': True, 'message': 'Feedback recebido!'})
            else:
                return jsonify({'success': False, 'error': 'Mensagem não encontrada'})
                
    except Exception as e:
        print(f"Erro ao processar feedback: {e}")
        return jsonify({'success': False, 'error': 'Erro interno'})

@app.route('/emotions', methods=['GET', 'POST'])
@login_required
def manage_emotions():
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
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    profile = get_user_profile(user_id)

    if request.method == 'POST':
        user_name = request.form.get('user_name', '')
        user_age = request.form.get('user_age', '')
        user_gender = request.form.get('user_gender', '')
        bot_name = request.form.get('bot_name', '')
        bot_gender = request.form.get('bot_gender', '')
        bot_avatar = request.form.get('bot_avatar', '')
        bot_personality = request.form.get('bot_personality', 'amigavel')
        bot_language = request.form.get('bot_language', 'informal')
        preferred_topics = request.form.getlist('preferred_topics')
        
        # Salvar avatar se foi enviado
        if 'bot_avatar' in request.files:
            file = request.files['bot_avatar']
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join('static', 'bot_avatars', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                bot_avatar = filename
        
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
                has_mature_access=has_mature_access,
                bot_personality=bot_personality,
                bot_language=bot_language,
                preferred_topics=','.join(preferred_topics) if preferred_topics else ''
            )
            
            flash('Personalização salva com sucesso!', 'success')
        
        return redirect(url_for('index'))

    # Lista de avatares disponíveis
    avatar_dir = os.path.join('static', 'bot_avatars')
    avatars = []
    if os.path.exists(avatar_dir):
        avatars = [f for f in os.listdir(avatar_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    return render_template(
        'personalize.html',
        user_name=profile.get('user_name', ''),
        user_age=profile.get('user_age', ''),
        user_gender=profile.get('user_gender', ''),
        bot_name=profile.get('bot_name', ''),
        bot_gender=profile.get('bot_gender', ''),
        bot_avatar=profile.get('bot_avatar', ''),
        bot_personality=profile.get('bot_personality', 'amigavel'),
        bot_language=profile.get('bot_language', 'informal'),
        preferred_topics=profile.get('preferred_topics', '').split(',') if profile.get('preferred_topics') else [],
        avatars=avatars
    )

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('static/bot_avatars', filename)

@app.route('/debug-profile')
@login_required
def debug_profile():
    """Rota de debug para verificar o perfil do usuário"""
    user_id = session.get('user_id')
    profile = get_user_profile(user_id)
    
    return f"""
    <h1>Debug do Perfil</h1>
    <p><strong>User ID:</strong> {user_id}</p>
    <p><strong>Perfil completo:</strong> {profile}</p>
    <p><strong>Nome do bot:</strong> {profile.get('bot_name', 'NÃO ENCONTRADO')}</p>
    <p><strong>Nome do usuário:</strong> {profile.get('user_name', 'NÃO ENCONTRADO')}</p>
    <a href="/chat">Voltar ao chat</a>
    """

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    from src.user_profile_db import UserProfileDB
    user_profile_db = UserProfileDB()
    app.user_profile_db = user_profile_db
    app.run(debug=True, use_reloader=False)