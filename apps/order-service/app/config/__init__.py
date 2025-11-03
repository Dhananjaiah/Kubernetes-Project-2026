"""
Order Service Configuration
"""
import os


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'postgres-service')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'ecommerce')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Service URLs
    PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://backend-service:5000')
    INVENTORY_SERVICE_URL = os.getenv('INVENTORY_SERVICE_URL', 'http://inventory-service:5003')
    
    DEBUG = False
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    API_TITLE = 'E-Commerce Order Service'
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
