"""
Blueprint de autenticação - Login, registro, recuperação de senha
"""
import hashlib
import sqlite3
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from functools import wraps

from src.email_service import EmailService

# Criar blueprint
auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    """Hash da senha usando SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_users_table():
    """Criar tabela de usuários se não existir"""
    conn = sqlite3.connect('memoria/eron_memory.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            reset_token TEXT,
            reset_token_expires TEXT
        )
    ''')
    conn.commit()
    conn.close()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email e senha são obrigatórios', 'error')
            return render_template('login.html')
        
        # Verificar credenciais
        conn = sqlite3.connect('memoria/eron_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and user[1] == hash_password(password):
            session.permanent = True
            session['user_id'] = user[0]
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Email ou senha incorretos', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validações
        if not all([username, email, password, confirm_password]):
            flash('Todos os campos são obrigatórios', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('As senhas não coincidem', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres', 'error')
            return render_template('register.html')
        
        try:
            create_users_table()
            
            # Verificar se usuário já existe
            conn = sqlite3.connect('memoria/eron_memory.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE email = ? OR username = ?', (email, username))
            existing_user = cursor.fetchone()
            
            if existing_user:
                flash('Email ou nome de usuário já cadastrado', 'error')
                conn.close()
                return render_template('register.html')
            
            # Criar novo usuário
            user_id = str(uuid.uuid4())
            hashed_password = hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (id, username, email, password)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, email, hashed_password))
            conn.commit()
            conn.close()
            
            # Login automático
            session.permanent = True
            session['user_id'] = user_id
            flash('Conta criada com sucesso!', 'success')
            return redirect(url_for('main.index'))
            
        except sqlite3.IntegrityError:
            flash('Email ou nome de usuário já cadastrado', 'error')
        except Exception as e:
            flash('Erro ao criar conta. Tente novamente.', 'error')
    
    return render_template('register.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Recuperação de senha"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Email é obrigatório', 'error')
            return render_template('reset_request.html')
        
        try:
            conn = sqlite3.connect('memoria/eron_memory.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            
            if user:
                # Gerar token de reset
                reset_token = str(uuid.uuid4())
                expires = datetime.now() + timedelta(hours=1)
                
                cursor.execute('''
                    UPDATE users 
                    SET reset_token = ?, reset_token_expires = ?
                    WHERE email = ?
                ''', (reset_token, expires.isoformat(), email))
                conn.commit()
                
                # Enviar email
                email_service = EmailService()
                reset_link = request.url_root + 'reset-password/' + reset_token
                
                email_sent = email_service.send_password_reset(email, reset_link)
                
                if email_sent:
                    flash('Email de recuperação enviado!', 'success')
                else:
                    flash('Erro ao enviar email. Tente novamente.', 'error')
            else:
                # Por segurança, sempre mostrar mensagem de sucesso
                flash('Se o email existir, você receberá instruções de recuperação', 'info')
            
            conn.close()
            
        except Exception as e:
            flash('Erro interno. Tente novamente.', 'error')
    
    return render_template('reset_request.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset de senha com token"""
    # Verificar token válido
    conn = sqlite3.connect('memoria/eron_memory.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, reset_token_expires FROM users 
        WHERE reset_token = ?
    ''', (token,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        flash('Token inválido ou expirado', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    # Verificar se token não expirou
    expires = datetime.fromisoformat(user[1])
    if datetime.now() > expires:
        conn.close()
        flash('Token expirado. Solicite um novo link de recuperação.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('Todos os campos são obrigatórios', 'error')
            return render_template('reset_password.html')
        
        if password != confirm_password:
            flash('As senhas não coincidem', 'error')
            return render_template('reset_password.html')
        
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres', 'error')
            return render_template('reset_password.html')
        
        try:
            # Atualizar senha
            hashed_password = hash_password(password)
            cursor.execute('''
                UPDATE users 
                SET password = ?, reset_token = NULL, reset_token_expires = NULL
                WHERE id = ?
            ''', (hashed_password, user[0]))
            conn.commit()
            conn.close()
            
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            flash('Erro ao alterar senha. Tente novamente.', 'error')
    
    conn.close()
    return render_template('reset_password.html')

@auth_bp.route('/logout')
def logout():
    """Logout do usuário"""
    session.pop('user_id', None)
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('main.landing'))