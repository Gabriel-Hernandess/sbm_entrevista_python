"""
Inicialização da aplicação Flask.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

# Inicializa extensões
db = SQLAlchemy()
cache = Cache()

def create_app(config_name='default'):
    """
    Factory pattern para criar a aplicação Flask.
    
    Args:
        config_name: Nome da configuração (development, production, testing)
    """
    app = Flask(__name__)
    
    # Carrega configuração
    from config import config
    app.config.from_object(config[config_name])
    
    # Inicializa extensões
    db.init_app(app)
    cache.init_app(app)
    
    # Cria diretórios necessários
    app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)
    
    # Cria diretório instance para o banco de dados SQLite
    from pathlib import Path
    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)
    
    # Registra blueprints
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.api import api_bp
    from app.blueprints.relatorio import relatorio_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(relatorio_bp)

    return app