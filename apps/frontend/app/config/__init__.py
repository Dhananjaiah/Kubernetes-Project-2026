"""
Frontend Service Configuration
"""
import os


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # API Gateway URL
    API_GATEWAY_URL = os.getenv('API_GATEWAY_URL', 'http://api-gateway:5004')
    
    # Direct service URLs (fallback)
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend-service:5000')
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:5001')
    ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL', 'http://order-service:5002')
    
    DEBUG = False
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')


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
