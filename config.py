"""
Configurações da aplicação Flask.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.resolve()


class Config:
    """Configuração base."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Database
    # Usa caminho absoluto para evitar problemas
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR.absolute() / "instance" / "dashboard.db"}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Print para debug (remover depois)
    _DB_PATH = BASE_DIR.absolute() / "instance" / "dashboard.db"
    
    # Upload
    UPLOAD_FOLDER = BASE_DIR / 'data' / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json'}
    
    # Cache
    CACHE_TYPE = 'SimpleCache'  # Use 'RedisCache' para produção
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos
    
    # APIs Externas
    AWESOMEAPI_BASE_URL = 'https://economia.awesomeapi.com.br'
    BRASILAPI_BASE_URL = 'https://brasilapi.com.br/api'
    
    # Scheduler (APScheduler)
    SCHEDULER_API_ENABLED = False
    
    # Data files
    DATA_DIR = BASE_DIR / 'data'
    CSV_DIR = DATA_DIR / 'csv'
    JSON_DIR = DATA_DIR / 'json'

    # Celery
    CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
    CELERY_RESULT_BACKEND = 'rpc://'


class DevelopmentConfig(Config):
    """Configuração de desenvolvimento."""
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'


class ProductionConfig(Config):
    """Configuração de produção."""
    DEBUG = False
    TESTING = False
    
    # Use Redis em produção
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    CACHE_REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    CACHE_REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    # Database - sobrescreve se DATABASE_URL estiver definida
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        Config.SQLALCHEMY_DATABASE_URI  # fallback para SQLite
    )


class TestingConfig(Config):
    """Configuração para testes."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Mapeamento de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

