"""
Frontend views
"""
from flask import Blueprint, render_template, jsonify, current_app
import requests
import os

from app.config import get_config

views_bp = Blueprint('views', __name__)


def get_api_url():
    """Get API URL from config"""
    config = get_config(os.getenv('FLASK_ENV', 'development'))
    # Try API Gateway first, fall back to direct backend
    return config.API_GATEWAY_URL or config.BACKEND_URL


@views_bp.route('/')
def index():
    """Main page"""
    try:
        api_url = get_api_url()
        response = requests.get(f'{api_url}/api/products', timeout=5)
        response.raise_for_status()  # Raise exception for 4xx/5xx status codes
        data = response.json()
        # Ensure products is a list
        products = data if isinstance(data, list) else []
        backend_status = 'Connected ✓'
        status_class = ''
    except Exception as e:
        products = []
        backend_status = f'Disconnected ✗ ({str(e)})'
        status_class = 'error'
        current_app.logger.error(f"Error fetching products: {e}")
    
    config = get_config(os.getenv('FLASK_ENV', 'development'))
    environment = config.ENVIRONMENT
    
    return render_template(
        'index.html',
        products=products,
        backend_status=backend_status,
        environment=environment,
        status_class=status_class
    )


@views_bp.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'service': 'frontend'}), 200
