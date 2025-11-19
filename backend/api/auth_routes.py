"""
Authentication routes (login, logout)
"""

from flask import Blueprint, request, jsonify, make_response
from backend.auth.auth_service import auth_service
from backend.services import user_service
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login endpoint
    Expected JSON: {"username": "...", "password": "..."}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Invalid request body'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Get user from service
        user_data = user_service.get_user_by_username(username)
        
        if not user_data:
            logger.warning(f"Login attempt with unknown username: {username}")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not auth_service.verify_password(password, user_data['password_hash']):
            logger.warning(f"Failed login attempt for user: {username}")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create session
        session_token = auth_service.create_session(user_data['user_id'], user_data)
        
        # Create response with session cookie
        response = make_response(jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'user_id': user_data['user_id'],
                'username': user_data['username'],
                'role': user_data['role'],
                'full_name': user_data['full_name']
            }
        }))
        
        # Set secure cookie
        response.set_cookie(
            'session_token',
            session_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite='Lax',
            max_age=8*60*60  # 8 hours
        )
        
        logger.info(f"User logged in: {username} ({user_data['role']})")
        return response
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    try:
        session_token = request.cookies.get('session_token')
        
        if session_token:
            auth_service.destroy_session(session_token)
        
        response = make_response(jsonify({
            'success': True,
            'message': 'Logout successful'
        }))
        
        # Clear cookie
        response.set_cookie('session_token', '', expires=0)
        
        return response
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user info"""
    session_token = request.cookies.get('session_token')
    
    if not session_token:
        return jsonify({'error': 'Not authenticated'}), 401
    
    session_data = auth_service.get_session(session_token)
    
    if not session_data:
        return jsonify({'error': 'Invalid session'}), 401
    
    return jsonify({
        'user': {
            'user_id': session_data['user_id'],
            'username': session_data['username'],
            'role': session_data['role'],
            'full_name': session_data['full_name']
        }
    })


@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Quick authentication check"""
    session_token = request.cookies.get('session_token')
    
    if not session_token:
        logger.debug("No session token in cookies")
        return jsonify({'authenticated': False}), 200
    
    session_data = auth_service.get_session(session_token)
    
    is_authenticated = session_data is not None
    logger.debug(f"Auth check: token={session_token[:20]}..., authenticated={is_authenticated}")
    
    return jsonify({
        'authenticated': is_authenticated,
        'user': {
            'username': session_data['username'],
            'role': session_data['role']
        } if session_data else None
    })
