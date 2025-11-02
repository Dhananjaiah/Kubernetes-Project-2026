"""
Product API endpoints
"""
from flask import Blueprint, jsonify, request, current_app
import os

from app.services.database import DatabaseService
from app.services.product_service import ProductService
from app.config import get_config

products_bp = Blueprint('products', __name__)


def get_product_service() -> ProductService:
    """Get product service instance"""
    config = get_config(os.getenv('FLASK_ENV', 'development'))
    db_service = DatabaseService(config)
    return ProductService(db_service)


@products_bp.route('/products', methods=['GET'])
def get_products():
    """
    Get all products
    ---
    Returns:
        200: List of products
        500: Internal server error
    """
    try:
        product_service = get_product_service()
        products = product_service.get_all_products()
        return jsonify([p.to_dict() for p in products]), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching products: {e}")
        return jsonify({'error': str(e)}), 500


@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id: int):
    """
    Get a specific product by ID
    ---
    Parameters:
        product_id: Product ID
    Returns:
        200: Product details
        404: Product not found
        500: Internal server error
    """
    try:
        product_service = get_product_service()
        product = product_service.get_product_by_id(product_id)
        
        if product:
            return jsonify(product.to_dict()), 200
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching product {product_id}: {e}")
        return jsonify({'error': str(e)}), 500


@products_bp.route('/products', methods=['POST'])
def create_product():
    """
    Create a new product
    ---
    Body:
        name: Product name (required)
        description: Product description
        price: Product price (required)
        stock: Stock quantity (required)
    Returns:
        201: Product created
        400: Invalid input
        500: Internal server error
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'name' not in data or 'price' not in data or 'stock' not in data:
            return jsonify({'error': 'Missing required fields: name, price, stock'}), 400
        
        product_service = get_product_service()
        product = product_service.create_product(
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            stock=int(data['stock'])
        )
        
        return jsonify(product.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating product: {e}")
        return jsonify({'error': str(e)}), 500


@products_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id: int):
    """
    Update an existing product
    ---
    Parameters:
        product_id: Product ID
    Body:
        name: Product name (optional)
        description: Product description (optional)
        price: Product price (optional)
        stock: Stock quantity (optional)
    Returns:
        200: Product updated
        404: Product not found
        500: Internal server error
    """
    try:
        data = request.get_json()
        
        product_service = get_product_service()
        product = product_service.update_product(
            product_id=product_id,
            name=data.get('name'),
            description=data.get('description'),
            price=float(data['price']) if 'price' in data else None,
            stock=int(data['stock']) if 'stock' in data else None
        )
        
        if product:
            return jsonify(product.to_dict()), 200
        else:
            return jsonify({'error': 'Product not found'}), 404
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Error updating product {product_id}: {e}")
        return jsonify({'error': str(e)}), 500


@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id: int):
    """
    Delete a product
    ---
    Parameters:
        product_id: Product ID
    Returns:
        204: Product deleted
        404: Product not found
        500: Internal server error
    """
    try:
        product_service = get_product_service()
        deleted = product_service.delete_product(product_id)
        
        if deleted:
            return '', 204
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error deleting product {product_id}: {e}")
        return jsonify({'error': str(e)}), 500


@products_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get product statistics
    ---
    Returns:
        200: Statistics
        500: Internal server error
    """
    try:
        product_service = get_product_service()
        stats = product_service.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching stats: {e}")
        return jsonify({'error': str(e)}), 500
