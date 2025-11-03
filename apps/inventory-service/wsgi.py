"""
WSGI entry point for Inventory Service
"""
import os
import time
from app import create_app
from app.services.database import DatabaseService
from app.services.inventory_service import InventoryService
from app.config import get_config

app = create_app()

if __name__ != '__main__':
    app.logger.info("Initializing inventory service database...")
    time.sleep(5)
    
    config = get_config(os.getenv('FLASK_ENV', 'development'))
    db_service = DatabaseService(config)
    inventory_service = InventoryService(db_service)
    
    if inventory_service.init_tables():
        app.logger.info("Inventory database initialized successfully")
    else:
        app.logger.warning("Inventory database initialization failed")

if __name__ == '__main__':
    app.logger.info("Starting inventory service development server...")
    app.run(host='0.0.0.0', port=5003, debug=True)
