"""
Inventory Service Configuration
"""
import os


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    DB_HOST = os.getenv('DB_HOST', 'postgres-service')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'ecommerce')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    DEBUG = False
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    API_TITLE = 'E-Commerce Inventory Service'
    API_VERSION = 'v1'
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')


class DevelopmentConfig(Config):
    DEBUG = True
    ENVIRONMENT = 'development'


class StagingConfig(Config):
    ENVIRONMENT = 'staging'


class ProductionConfig(Config):
    ENVIRONMENT = 'production'


config_by_name = {
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name='default'):
    return config_by_name.get(config_name, DevelopmentConfig)
