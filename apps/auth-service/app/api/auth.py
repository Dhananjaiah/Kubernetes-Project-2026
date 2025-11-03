"""
Authentication API endpoints
"""
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os

from app.services.database import DatabaseService
from app.services.auth_service import AuthService
from app.config import get_config

auth_bp = Blueprint('auth', __name__)


def get_auth_service() -> AuthService:
    """Get auth service instance"""
    config = get_config(os.getenv('FLASK_ENV', 'development'))
    db_service = DatabaseService(config)
    return AuthService(db_service)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    Body:
        username: Username (required)
        email: Email address (required)
        password: Password (required)
        full_name: Full name (optional)
    Returns:
        201: User created
        400: Invalid input or user already exists
        500: Internal server error
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'username' not in data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Missing required fields: username, email, password'}), 400
        
        # Validate password strength (basic)
        if len(data['password']) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        auth_service = get_auth_service()
        user = auth_service.register_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            full_name=data.get('full_name', '')
        )
        
        if user:
            return jsonify({
                'message': 'User registered successfully',
                'user': user.to_dict()
            }), 201
        else:
            return jsonify({'error': 'Username or email already exists'}), 400
    except Exception as e:
        current_app.logger.error(f"Error registering user: {e}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and get JWT tokens
    ---
    Body:
        username: Username (required)
        password: Password (required)
    Returns:
        200: Authentication successful with tokens
        401: Invalid credentials
        500: Internal server error
    """
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Missing username or password'}), 400
        
        auth_service = get_auth_service()
        result = auth_service.authenticate(
            username=data['username'],
            password=data['password']
        )
        
        if result:
            return jsonify({
                'message': 'Login successful',
                'access_token': result['access_token'],
                'refresh_token': result['refresh_token'],
                'user': result['user']
            }), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        current_app.logger.error(f"Error during login: {e}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current user information (requires JWT token)
    ---
    Headers:
        Authorization: Bearer <access_token>
    Returns:
        200: User information
        401: Unauthorized
        500: Internal server error
    """
    try:
        identity = get_jwt_identity()
        user_id = identity.get('user_id')
        
        auth_service = get_auth_service()
        user = auth_service.get_user_by_id(user_id)
        
        if user:
            return jsonify(user.to_dict()), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching user: {e}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/validate', methods=['POST'])
@jwt_required()
def validate_token():
    """
    Validate JWT token
    ---
    Headers:
        Authorization: Bearer <access_token>
    Returns:
        200: Token is valid
        401: Token is invalid
    """
    try:
        identity = get_jwt_identity()
        return jsonify({
            'valid': True,
            'user_id': identity.get('user_id'),
            'username': identity.get('username')
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error validating token: {e}")
        return jsonify({'error': str(e)}), 500
