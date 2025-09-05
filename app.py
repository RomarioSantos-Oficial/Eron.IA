from eron.user_profile_db import UserProfileDB
user_profile_db = UserProfileDB()
import os
from eron.knowledge_base import KnowledgeBase
knowledge_base = KnowledgeBase(os.path.join(os.path.dirname(__file__), 'memoria'))
from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory
from eron.memory import EronMemory
from eron.sensitive_memory import SensitiveMemory
from eron.check import check_age
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = os.urandom(24)

memory = EronMemory()
sensitive_memory = SensitiveMemory()


# Personalização do usuário e bot

@app.route('/personalize', methods=['GET', 'POST'])
def personalize():
    user_id = request.cookies.get('user_id') or os.urandom(8).hex()
    profile = user_profile_db.get_profile(user_id)
    if request.method == 'POST':
        user_name = request.form['user_name']
        user_age = request.form['user_age']
        user_gender = request.form['user_gender']
        bot_name = request.form['bot_name']
        bot_gender = request.form['bot_gender']
        bot_avatar = request.files.get('bot_avatar')
        # Checagem de idade já aqui
        try:
            idade = int(user_age)
            if idade < 18:
                return render_template('personalize.html', error='Acesso apenas para maiores de 18 anos.', **(profile or {}))
        except ValueError:
            return render_template('personalize.html', error='Idade inválida.', **(profile or {}))
        if bot_avatar and bot_avatar.filename:
            filename = secure_filename(bot_name + '_' + bot_avatar.filename)
            avatar_dir = os.path.join('static', 'bot_avatars')
            os.makedirs(avatar_dir, exist_ok=True)
            avatar_path = os.path.join(avatar_dir, filename)
            bot_avatar.save(avatar_path)
            bot_avatar_url = '/' + avatar_path.replace('\\', '/').replace('static/', 'static/')
        else:
            if bot_gender == 'feminino':
                bot_avatar_url = '/static/bot_avatars/default_feminino.png'
            elif bot_gender == 'masculino':
                bot_avatar_url = '/static/bot_avatars/default_masculino.png'
            else:
                bot_avatar_url = '/static/bot_avatars/default_outro.png'
        # Salva perfil no banco
        user_profile_db.save_profile(user_id, user_name, user_age, user_gender, bot_name, bot_gender, bot_avatar_url)
        resp = redirect(url_for('index'))
        resp.set_cookie('user_id', user_id, max_age=60*60*24*365)
        return resp
    # GET: se já existe perfil, redireciona para o chat
    if profile:
        return redirect(url_for('index'))
    return render_template('personalize.html', **(profile or {}))


# Função auxiliar para detectar tema
def detect_tema(mensagem):
    temas = {
        'relacionamento': ['namoro', 'casamento', 'relacionamento', 'amor', 'ficante', 'paquera'],
        'filmes': ['filme', 'cinema', 'ator', 'atriz', 'diretor', 'série', 'temporada'],
        'conhecimento_geral': ['história', 'ciência', 'geografia', 'matemática', 'física', 'química', 'biologia'],
        'conteudo_18': ['sexo', 'pornô', 'nude', 'conteúdo adulto', '+18', 'erótico'],
    }
    mensagem_lower = mensagem.lower()
    for tema, palavras in temas.items():
        for palavra in palavras:
            if palavra in mensagem_lower:
                return tema
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    user_id = request.cookies.get('user_id')
    profile = user_profile_db.get_profile(user_id) if user_id else None
    if not profile:
        return redirect(url_for('personalize'))
    messages = memory.get_all_messages()
    feedbacks = {}
    if request.method == 'POST':
        # Feedback do usuário
        if 'feedback' in request.form:
            pergunta = request.form.get('feedback_pergunta')
            resposta = request.form.get('feedback_resposta')
            feedback = request.form.get('feedback')
            user_name = profile.get('user_name', 'Você')
            tema = None
            if pergunta:
                tema = detect_tema(pergunta)
            knowledge_base.save_feedback(pergunta, resposta, user_name, feedback, tema=tema)
            # Salva feedback para exibir na interface
            feedbacks[(pergunta, resposta)] = feedback
            messages = memory.get_all_messages()
        else:
            user_message = request.form['message']
            bot_name = profile.get('bot_name', 'Eron')
            user_name = profile.get('user_name', 'Você')
            bot_gender = profile.get('bot_gender', 'outro')
            tema = detect_tema(user_message)
            resposta = knowledge_base.search_answer(user_message, tema=tema)
            if resposta:
                eron_response = resposta
            else:
                eron_response = "Desculpe, ainda não sei responder isso, mas estou aprendendo! Se quiser, tente perguntar de outra forma ou aguarde novas atualizações."
                knowledge_base.save_qa(user_message, eron_response, contexto=tema, autor=user_name, tema=tema)
            # Salva histórico personalizado por usuário
            knowledge_base.save_conversa(user_name, user_message, eron_response, tema=tema)
            memory.save_message(user_message, eron_response)
            messages = memory.get_all_messages()
    else:
        feedbacks = {}
    return render_template(
        'chat.html',
        messages=messages,
        user_name=profile.get('user_name', 'Você'),
        bot_name=profile.get('bot_name', 'Eron'),
        user_gender=profile.get('user_gender', 'outro'),
        bot_gender=profile.get('bot_gender', 'outro'),
        user_age=profile.get('user_age', ''),
        bot_avatar=profile.get('bot_avatar', '/static/bot_avatars/default_outro.png'),
        feedbacks=feedbacks
    )




@app.route('/alterar_nomes', methods=['GET', 'POST'])
def alterar_nomes():
    if request.method == 'POST':
        session['user_name'] = request.form['user_name']
        session['user_age'] = request.form.get('user_age', session.get('user_age', ''))
        session['user_gender'] = request.form.get('user_gender', session.get('user_gender', ''))
        session['bot_name'] = request.form['bot_name']
        session['bot_gender'] = request.form.get('bot_gender', session.get('bot_gender', ''))
        return redirect(url_for('index'))
    return render_template(
        'personalize.html',
        user_name=session.get('user_name', ''),
        user_age=session.get('user_age', ''),
        user_gender=session.get('user_gender', ''),
        bot_name=session.get('bot_name', ''),
        bot_gender=session.get('bot_gender', ''),
    )

if __name__ == '__main__':
    app.run(debug=True)
