"""
Inventory API endpoints
"""
from flask import Blueprint, jsonify, request, current_app
import os

from app.services.database import DatabaseService
from app.services.inventory_service import InventoryService
from app.config import get_config

inventory_bp = Blueprint('inventory', __name__)


def get_inventory_service() -> InventoryService:
    """Get inventory service instance"""
    config = get_config(os.getenv('FLASK_ENV', 'development'))
    db_service = DatabaseService(config)
    return InventoryService(db_service)


@inventory_bp.route('/inventory', methods=['GET'])
def get_all_inventory():
    """Get all inventory items"""
    try:
        inventory_service = get_inventory_service()
        items = inventory_service.get_all_inventory()
        return jsonify([item.to_dict() for item in items]), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching inventory: {e}")
        return jsonify({'error': str(e)}), 500


@inventory_bp.route('/inventory/<int:product_id>', methods=['GET'])
def get_inventory(product_id: int):
    """Get inventory for a specific product"""
    try:
        inventory_service = get_inventory_service()
        item = inventory_service.get_inventory_by_product_id(product_id)
        
        if item:
            return jsonify(item.to_dict()), 200
        else:
            return jsonify({'error': 'Inventory not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching inventory: {e}")
        return jsonify({'error': str(e)}), 500


@inventory_bp.route('/inventory/<int:product_id>', methods=['PUT'])
def update_inventory(product_id: int):
    """Update inventory quantity"""
    try:
        data = request.get_json()
        
        if not data or 'quantity' not in data:
            return jsonify({'error': 'Missing quantity field'}), 400
        
        inventory_service = get_inventory_service()
        item = inventory_service.update_inventory(
            product_id=product_id,
            quantity=int(data['quantity']),
            warehouse_location=data.get('warehouse_location', '')
        )
        
        return jsonify(item.to_dict()), 200
    except Exception as e:
        current_app.logger.error(f"Error updating inventory: {e}")
        return jsonify({'error': str(e)}), 500


@inventory_bp.route('/inventory/<int:product_id>/reserve', methods=['POST'])
def reserve_inventory(product_id: int):
    """Reserve inventory for an order"""
    try:
        data = request.get_json()
        
        if not data or 'quantity' not in data:
            return jsonify({'error': 'Missing quantity field'}), 400
        
        inventory_service = get_inventory_service()
        success = inventory_service.reserve_inventory(product_id, int(data['quantity']))
        
        if success:
            return jsonify({'message': 'Inventory reserved successfully'}), 200
        else:
            return jsonify({'error': 'Insufficient inventory'}), 400
    except Exception as e:
        current_app.logger.error(f"Error reserving inventory: {e}")
        return jsonify({'error': str(e)}), 500


@inventory_bp.route('/inventory/<int:product_id>/release', methods=['POST'])
def release_inventory(product_id: int):
    """Release reserved inventory"""
    try:
        data = request.get_json()
        
        if not data or 'quantity' not in data:
            return jsonify({'error': 'Missing quantity field'}), 400
        
        inventory_service = get_inventory_service()
        success = inventory_service.release_inventory(product_id, int(data['quantity']))
        
        if success:
            return jsonify({'message': 'Inventory released successfully'}), 200
        else:
            return jsonify({'error': 'Failed to release inventory'}), 400
    except Exception as e:
        current_app.logger.error(f"Error releasing inventory: {e}")
        return jsonify({'error': str(e)}), 500


@inventory_bp.route('/inventory/<int:product_id>/adjust', methods=['POST'])
def adjust_inventory(product_id: int):
    """Adjust inventory (positive or negative adjustment)"""
    try:
        data = request.get_json()
        
        if not data or 'adjustment' not in data:
            return jsonify({'error': 'Missing adjustment field'}), 400
        
        inventory_service = get_inventory_service()
        item = inventory_service.adjust_inventory(product_id, int(data['adjustment']))
        
        if item:
            return jsonify(item.to_dict()), 200
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error adjusting inventory: {e}")
        return jsonify({'error': str(e)}), 500
