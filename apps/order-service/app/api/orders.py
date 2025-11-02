"""
Order API endpoints
"""
from flask import Blueprint, jsonify, request, current_app
import os

from app.services.database import DatabaseService
from app.services.order_service import OrderService
from app.config import get_config

orders_bp = Blueprint('orders', __name__)


def get_order_service() -> OrderService:
    """Get order service instance"""
    config = get_config(os.getenv('FLASK_ENV', 'development'))
    db_service = DatabaseService(config)
    return OrderService(db_service, config.PRODUCT_SERVICE_URL, config.INVENTORY_SERVICE_URL)


@orders_bp.route('/orders', methods=['POST'])
def create_order():
    """
    Create a new order
    Body:
        user_id: User ID (optional)
        items: List of {product_id, quantity}
        shipping_address: Shipping address
    """
    try:
        data = request.get_json()
        
        if not data or 'items' not in data or 'shipping_address' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        order_service = get_order_service()
        order = order_service.create_order(
            user_id=data.get('user_id'),
            items=data['items'],
            shipping_address=data['shipping_address']
        )
        
        if order:
            return jsonify(order.to_dict()), 201
        else:
            return jsonify({'error': 'Failed to create order'}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating order: {e}")
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id: int):
    """Get order by ID"""
    try:
        order_service = get_order_service()
        order = order_service.get_order_by_id(order_id)
        
        if order:
            return jsonify(order.to_dict()), 200
        else:
            return jsonify({'error': 'Order not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching order: {e}")
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/orders/user/<int:user_id>', methods=['GET'])
def get_user_orders(user_id: int):
    """Get all orders for a user"""
    try:
        order_service = get_order_service()
        orders = order_service.get_orders_by_user(user_id)
        return jsonify([order.to_dict() for order in orders]), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching user orders: {e}")
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id: int):
    """Update order status"""
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({'error': 'Missing status field'}), 400
        
        order_service = get_order_service()
        order = order_service.update_order_status(order_id, data['status'])
        
        if order:
            return jsonify(order.to_dict()), 200
        else:
            return jsonify({'error': 'Order not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error updating order status: {e}")
        return jsonify({'error': str(e)}), 500
