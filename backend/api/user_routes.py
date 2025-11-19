"""
User CRUD API Routes
Provides REST API endpoints for user management
"""
from flask import Blueprint, request, jsonify, session
from backend.auth.decorators import login_required, role_required
from backend.services import user_service

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('', methods=['GET'])
@role_required(['admin'])
def get_users():
    """Get all users (admin only)"""
    try:
        users = user_service.get_all_users()
        return jsonify({'success': True, 'users': users}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@users_bp.route('/<user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """Get user by ID"""
    try:
        # Users can only view their own profile unless they're admin
        current_user_id = session.get('user_id')
        current_role = session.get('role')
        
        if current_role != 'admin' and current_user_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        user = user_service.get_user_by_id(user_id)
        if user:
            return jsonify({'success': True, 'user': user}), 200
        return jsonify({'success': False, 'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@users_bp.route('', methods=['POST'])
@role_required(['admin'])
def create_user():
    """Create new user (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'password', 'role', 'full_name', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        user = user_service.create_user(data)
        return jsonify({'success': True, 'user': user, 'message': 'User created successfully'}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@users_bp.route('/<user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """Update existing user"""
    try:
        # Users can only update their own profile unless they're admin
        current_user_id = session.get('user_id')
        current_role = session.get('role')
        
        if current_role != 'admin' and current_user_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Non-admin users cannot change their role
        if current_role != 'admin' and 'role' in data:
            del data['role']
        
        user = user_service.update_user(user_id, data)
        
        if user:
            return jsonify({'success': True, 'user': user, 'message': 'User updated successfully'}), 200
        return jsonify({'success': False, 'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@users_bp.route('/<user_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_user(user_id):
    """Delete user (soft delete, admin only)"""
    try:
        success = user_service.delete_user(user_id)
        
        if success:
            return jsonify({'success': True, 'message': 'User deleted successfully'}), 200
        return jsonify({'success': False, 'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
