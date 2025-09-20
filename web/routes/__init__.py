"""
Web Routes - Blueprints da Aplicação Flask
"""

from .auth import auth_bp
from .main import main_bp  
from .chat import chat_bp
from .config import config_bp

def register_blueprints(app):
    """Registrar todos os blueprints na aplicação"""
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(config_bp, url_prefix='/config')

__all__ = ['auth_bp', 'main_bp', 'chat_bp', 'config_bp', 'register_blueprints']