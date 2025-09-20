"""
Factory de Aplicação Flask
Configuração centralizada da aplicação web
"""
from flask import Flask
from core.preferences import PreferencesManager as get_config_service
from .routes import register_blueprints

def create_app(config_name: str = 'default') -> Flask:
    """Criar instância da aplicação Flask"""
    app = Flask(__name__)
    
    # Carregar configurações
    config_service = get_config_service()
    
    # Configurações básicas
    app.config['SECRET_KEY'] = config_service.get('security.secret_key', 'dev-secret-key')
    app.config['DEBUG'] = config_service.get('app.debug', False)
    
    # Registrar blueprints
    register_blueprints(app)
    
    return app
