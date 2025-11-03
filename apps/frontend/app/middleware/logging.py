"""
Logging middleware
"""
import logging
import sys
from flask import Flask, request, g
import time


def setup_logging(app: Flask):
    """Setup application logging"""
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Set log level based on environment
    log_level = logging.DEBUG if app.config.get('DEBUG') else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set Flask app logger
    app.logger.setLevel(log_level)
    
    # Add request logging middleware
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            app.logger.info(
                f"{request.method} {request.path} - {response.status_code} - {elapsed:.3f}s"
            )
        return response
    
    app.logger.info("Logging configured")
