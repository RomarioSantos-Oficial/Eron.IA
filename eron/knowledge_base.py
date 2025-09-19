import os
import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory

class KnowledgeBase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.initialize_db()
    
    def initialize_db(self):
        conn = sqlite3.connect(os.path.join(self.db_path, 'knowledge.db'))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                response TEXT,
                feedback TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_all_feedback(self):
        conn = sqlite3.connect(os.path.join(self.db_path, 'knowledge.db'))
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM feedback ORDER BY timestamp DESC')
        feedbacks = cursor.fetchall()
        
        conn.close()
        return feedbacks

# Criar uma instância do KnowledgeBase
knowledge_base = KnowledgeBase(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'memoria'))
from eron.memory import EronMemory
from eron.sensitive_memory import SensitiveMemory
from eron.check import check_age
from werkzeug.utils import secure_filename
import requests
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

memory = EronMemory()
sensitive_memory = SensitiveMemory()

# --- NOVO: Função para obter a resposta da IA do LM Studio ---
def get_llm_response(user_message, user_profile=None):
    try:
        api_url = os.getenv("LM_STUDIO_API_URL")
        if not api_url:
            print("Erro: A URL da API do LM Studio não foi encontrada.")
            return None

        headers = {"Content-Type": "application/json"}
        payload = {
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        response_json = response.json()
        if 'choices' in response_json and len(response_json['choices']) > 0:
            return response_json['choices'][0]['message']['content'].strip()
        
        return None

    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com o servidor LM Studio: {e}")
        return None
        
@app.route('/')
def index():
    if not 'age_verified' in session:
        return redirect(url_for('verify_age'))

    user_profile_db = getattr(app, 'user_profile_db', None)
    
    user_id = session.get('user_id')
    profile = {}
    if user_id and user_profile_db:
        profile = user_profile_db.get_profile(user_id) or {}
    
    user_name = profile.get('user_name', session.get('user_name', 'Usuário'))
    user_age = profile.get('user_age', session.get('user_age', 'desconhecida'))
    user_gender = profile.get('user_gender', session.get('user_gender', 'outro'))
    bot_name = profile.get('bot_name', session.get('bot_name', 'Eron'))
    bot_gender = profile.get('bot_gender', session.get('bot_gender', 'outro'))

    feedbacks = knowledge_base.get_all_feedback()
    
    return render_template('index.html', 
        user_name=user_name,
        user_age=user_age,
        user_gender=user_gender,
        bot_name=bot_name,
        bot_gender=bot_gender,
        feedbacks=feedbacks
    )

@app.route('/verify-age', methods=['GET', 'POST'])
def verify_age():
    if request.method == 'POST':
        idade_str = request.form.get('idade')
        try:
            idade = int(idade_str)
            if idade >= 18:
                session['age_verified'] = True
                return redirect(url_for('index'))
            else:
                return render_template('age.html', error="Você deve ter 18 anos ou mais para acessar.")
        except (ValueError, TypeError):
            return render_template('age.html', error="Idade inválida.")
    return render_template('age.html', error=None)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if not session.get('age_verified'):
        return redirect(url_for('verify_age'))
    
    user_profile_db = getattr(app, 'user_profile_db', None)
    user_id = session.get('user_id') or 'anon_user'
    
    profile = {}
    if user_profile_db:
        profile = user_profile_db.get_profile(user_id) or {}

    user_name = profile.get('user_name', session.get('user_name', 'Usuário'))
    bot_name = profile.get('bot_name', session.get('bot_name', 'Eron'))
    
    if request.method == 'POST':
        user_message = request.form['message']
        response = get_llm_response(user_message, user_profile=profile)
        if not response:
            response = "Desculpe, não consegui me conectar com a IA no momento. Por favor, verifique se o servidor do LM Studio está rodando."
        
        memory.save_message(user_message, response)
        return redirect(url_for('chat'))

    messages = memory.get_all_messages()
    return render_template('chat.html', messages=messages, user_name=user_name, bot_name=bot_name)

@app.route('/personalizar', methods=['GET', 'POST'])
def personalizar():
    if not session.get('age_verified'):
        return redirect(url_for('verify_age'))
    
    user_id = session.get('user_id') or 'anon_user'
    
    user_profile_db = getattr(app, 'user_profile_db', None)
    
    profile = {}
    if user_profile_db:
        profile = user_profile_db.get_profile(user_id) or {}

    if request.method == 'POST':
        user_name = request.form.get('user_name', '')
        user_age = request.form.get('user_age', '')
        user_gender = request.form.get('user_gender', '')
        bot_name = request.form.get('bot_name', '')
        bot_gender = request.form.get('bot_gender', '')
        bot_avatar = request.form.get('bot_avatar', '')
        
        if user_profile_db:
            user_profile_db.save_profile(user_id=user_id, user_name=user_name, user_age=user_age, user_gender=user_gender, bot_name=bot_name, bot_gender=bot_gender, bot_avatar=bot_avatar)
        
        return redirect(url_for('index'))

    user_name = profile.get('user_name', '')
    user_age = profile.get('user_age', '')
    user_gender = profile.get('user_gender', '')
    bot_name = profile.get('bot_name', '')
    bot_gender = profile.get('bot_gender', '')
    
    return render_template(
        'personalize.html',
        user_name=user_name,
        user_age=user_age,
        user_gender=user_gender,
        bot_name=bot_name,
        bot_gender=bot_gender
    )

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('static/bot_avatars', filename)

if __name__ == '__main__':
    from eron.user_profile_db import UserProfileDB
    user_profile_db = UserProfileDB()
    app.user_profile_db = user_profile_db
    app.run(debug=True, use_reloader=False)