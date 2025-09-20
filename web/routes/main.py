"""
Blueprint principal - Páginas principais e navegação
"""
from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps

# Criar blueprint
main_bp = Blueprint('main', __name__)

def login_required(f):
    """Decorador para páginas que requerem login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/')
def landing():
    """Página inicial (landing page)"""
    if 'user_id' in session:
        return redirect(url_for('main.index'))
    return render_template('landing.html')

@main_bp.route('/dashboard')
@login_required
def index():
    """Dashboard principal (página inicial após login)"""
    return render_template('index.html')

@main_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Servir arquivos de upload"""
    from flask import send_from_directory
    import os
    return send_from_directory(os.path.join(os.getcwd(), 'uploads'), filename)

@main_bp.route('/debug-profile')
@login_required
def debug_profile():
    """Debug de perfil do usuário"""
    user_id = session.get('user_id')
    
    try:
        from src.user_profile_db import UserProfileDB
        profile_db = UserProfileDB()
        profile = profile_db.get_profile(user_id)
        
        debug_info = {
            'user_id': user_id,
            'profile': profile,
            'session': dict(session)
        }
        
        return f"<pre>{str(debug_info)}</pre>"
    
    except Exception as e:
        return f"<pre>Erro: {str(e)}</pre>"