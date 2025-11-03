"""
WSGI entry point for Order Service
"""
import os
import time
from app import create_app
from app.services.database import DatabaseService
from app.services.order_service import OrderService
from app.config import get_config

app = create_app()

if __name__ != '__main__':
    app.logger.info("Initializing order service database...")
    time.sleep(5)
    
    config = get_config(os.getenv('FLASK_ENV', 'development'))
    db_service = DatabaseService(config)
    order_service = OrderService(db_service, config.PRODUCT_SERVICE_URL, config.INVENTORY_SERVICE_URL)
    
    if order_service.init_tables():
        app.logger.info("Order database initialized successfully")
    else:
        app.logger.warning("Order database initialization failed")

if __name__ == '__main__':
    app.logger.info("Starting order service development server...")
    app.run(host='0.0.0.0', port=5002, debug=True)
