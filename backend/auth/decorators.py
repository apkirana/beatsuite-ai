"""
Authentication decorators for protecting routes
"""

from functools import wraps
from flask import request, jsonify, session
from backend.auth.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)


def login_required(f):
    """Decorator to require authentication for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for session token in cookie or header
        session_token = request.cookies.get('session_token') or \
                       request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not session_token:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Validate session
        session_data = auth_service.get_session(session_token)
        if not session_data:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        # Attach user data to request
        request.current_user = session_data
        
        return f(*args, **kwargs)
    
    return decorated_function


def role_required(required_roles):
    """Decorator to require specific role(s)
    
    Usage:
        @role_required(['admin'])
        @role_required(['admin', 'nurse'])
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check for session token
            session_token = request.cookies.get('session_token') or \
                           request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not session_token:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Validate session
            session_data = auth_service.get_session(session_token)
            if not session_data:
                return jsonify({'error': 'Invalid or expired session'}), 401
            
            # Check role
            user_role = session_data.get('role')
            if user_role not in required_roles:
                logger.warning(f"User {session_data.get('user_id')} (role: {user_role}) attempted to access {f.__name__} - Required: {required_roles}")
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            # Attach user data to request
            request.current_user = session_data
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator
