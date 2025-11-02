"""
API Gateway Configuration
"""
import os


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Microservices URLs
    PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://backend-service:5000')
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:5001')
    ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL', 'http://order-service:5002')
    INVENTORY_SERVICE_URL = os.getenv('INVENTORY_SERVICE_URL', 'http://inventory-service:5003')
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    
    DEBUG = False
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    API_TITLE = 'E-Commerce API Gateway'
    API_VERSION = 'v1'
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Timeout for microservice calls
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))


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
