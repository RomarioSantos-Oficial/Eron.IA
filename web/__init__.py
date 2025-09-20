"""
Web - Interface Web e Blueprints Flask
Componentes para a aplicação web
"""

from .app_factory import create_app
from .routes import register_blueprints

__all__ = ['create_app', 'register_blueprints']