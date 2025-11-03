"""
API Gateway routing to microservices
"""
from flask import Blueprint, request, jsonify, current_app
import requests
import os

from app.config import get_config

gateway_bp = Blueprint('gateway', __name__)


def get_service_urls():
    """Get service URLs from config"""
    config = get_config(os.getenv('FLASK_ENV', 'development'))
    return {
        'products': config.PRODUCT_SERVICE_URL,
        'auth': config.AUTH_SERVICE_URL,
        'orders': config.ORDER_SERVICE_URL,
        'inventory': config.INVENTORY_SERVICE_URL,
        'timeout': config.REQUEST_TIMEOUT
    }


def proxy_request(service_url: str, path: str, timeout: int = 10):
    """Proxy request to microservice"""
    url = f"{service_url}{path}"
    method = request.method
    headers = {k: v for k, v in request.headers if k.lower() not in ['host', 'connection']}
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=request.args, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=request.get_json(), timeout=timeout)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=request.get_json(), timeout=timeout)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            return jsonify({'error': 'Method not allowed'}), 405
        
        return jsonify(response.json() if response.content else {}), response.status_code
    except requests.exceptions.Timeout:
        current_app.logger.error(f"Timeout calling {url}")
        return jsonify({'error': 'Service timeout'}), 504
    except requests.exceptions.ConnectionError:
        current_app.logger.error(f"Connection error calling {url}")
        return jsonify({'error': 'Service unavailable'}), 503
    except Exception as e:
        current_app.logger.error(f"Error proxying request: {e}")
        return jsonify({'error': 'Internal gateway error'}), 500


# Product Service routes
@gateway_bp.route('/products', methods=['GET', 'POST'])
@gateway_bp.route('/products/<int:product_id>', methods=['GET', 'PUT', 'DELETE'])
def products(product_id=None):
    """Proxy to Product Service"""
    services = get_service_urls()
    path = f"/api/products/{product_id}" if product_id else "/api/products"
    return proxy_request(services['products'], path, services['timeout'])


@gateway_bp.route('/stats', methods=['GET'])
def stats():
    """Proxy to Product Service stats"""
    services = get_service_urls()
    return proxy_request(services['products'], '/api/stats', services['timeout'])


# Auth Service routes
@gateway_bp.route('/auth/register', methods=['POST'])
def register():
    """Proxy to Auth Service registration"""
    services = get_service_urls()
    return proxy_request(services['auth'], '/api/auth/register', services['timeout'])


@gateway_bp.route('/auth/login', methods=['POST'])
def login():
    """Proxy to Auth Service login"""
    services = get_service_urls()
    return proxy_request(services['auth'], '/api/auth/login', services['timeout'])


@gateway_bp.route('/auth/me', methods=['GET'])
def me():
    """Proxy to Auth Service current user"""
    services = get_service_urls()
    return proxy_request(services['auth'], '/api/auth/me', services['timeout'])


@gateway_bp.route('/auth/validate', methods=['POST'])
def validate():
    """Proxy to Auth Service token validation"""
    services = get_service_urls()
    return proxy_request(services['auth'], '/api/auth/validate', services['timeout'])


# Order Service routes
@gateway_bp.route('/orders', methods=['GET', 'POST'])
@gateway_bp.route('/orders/<int:order_id>', methods=['GET'])
def orders(order_id=None):
    """Proxy to Order Service"""
    services = get_service_urls()
    path = f"/api/orders/{order_id}" if order_id else "/api/orders"
    return proxy_request(services['orders'], path, services['timeout'])


@gateway_bp.route('/orders/user/<int:user_id>', methods=['GET'])
def user_orders(user_id):
    """Proxy to Order Service user orders"""
    services = get_service_urls()
    return proxy_request(services['orders'], f'/api/orders/user/{user_id}', services['timeout'])


@gateway_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
def order_status(order_id):
    """Proxy to Order Service status update"""
    services = get_service_urls()
    return proxy_request(services['orders'], f'/api/orders/{order_id}/status', services['timeout'])


# Inventory Service routes
@gateway_bp.route('/inventory', methods=['GET'])
@gateway_bp.route('/inventory/<int:product_id>', methods=['GET', 'PUT'])
def inventory(product_id=None):
    """Proxy to Inventory Service"""
    services = get_service_urls()
    path = f"/api/inventory/{product_id}" if product_id else "/api/inventory"
    return proxy_request(services['inventory'], path, services['timeout'])


@gateway_bp.route('/inventory/<int:product_id>/reserve', methods=['POST'])
def reserve_inventory(product_id):
    """Proxy to Inventory Service reserve"""
    services = get_service_urls()
    return proxy_request(services['inventory'], f'/api/inventory/{product_id}/reserve', services['timeout'])


@gateway_bp.route('/inventory/<int:product_id>/release', methods=['POST'])
def release_inventory(product_id):
    """Proxy to Inventory Service release"""
    services = get_service_urls()
    return proxy_request(services['inventory'], f'/api/inventory/{product_id}/release', services['timeout'])


@gateway_bp.route('/inventory/<int:product_id>/adjust', methods=['POST'])
def adjust_inventory(product_id):
    """Proxy to Inventory Service adjust"""
    services = get_service_urls()
    return proxy_request(services['inventory'], f'/api/inventory/{product_id}/adjust', services['timeout'])
