"""
Configuration management for different environments
"""
import os


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'postgres-service')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'ecommerce')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    
    # Database connection string
    DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Application settings
    DEBUG = False
    TESTING = False
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    # API settings
    API_TITLE = 'E-Commerce Backend API'
    API_VERSION = 'v1'
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Rate limiting
    RATE_LIMIT = os.getenv('RATE_LIMIT', '100 per minute')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENVIRONMENT = 'development'


class StagingConfig(Config):
    """Staging configuration"""
    ENVIRONMENT = 'staging'


class ProductionConfig(Config):
    """Production configuration"""
    ENVIRONMENT = 'production'
    # In production, ensure SECRET_KEY is set via environment variable
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in production")


config_by_name = {
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name='default'):
    """Get configuration by name"""
    return config_by_name.get(config_name, DevelopmentConfig)
