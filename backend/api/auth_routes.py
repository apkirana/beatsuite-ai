"""
Authentication routes (login, logout)
"""

import os
import time
from collections import defaultdict
from threading import Lock

from flask import Blueprint, request, jsonify, make_response
from backend.auth.auth_service import auth_service
from backend.services import user_service
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Send cookies only over HTTPS unless explicitly disabled for local development.
COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'true').lower() != 'false'

# Throttle failed logins per client address. In-memory, so it resets on restart
# and is per-process — good enough for a single instance, but put a real rate
# limiter (or your load balancer's) in front of a multi-instance deployment.
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 300
_failed_attempts = defaultdict(list)
_attempts_lock = Lock()


def _client_key() -> str:
    """Identify the caller for throttling purposes."""
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or 'unknown'


def _is_locked_out(key: str) -> bool:
    cutoff = time.time() - LOCKOUT_SECONDS
    with _attempts_lock:
        recent = [t for t in _failed_attempts[key] if t > cutoff]
        _failed_attempts[key] = recent
        return len(recent) >= MAX_FAILED_ATTEMPTS


def _record_failure(key: str) -> None:
    with _attempts_lock:
        _failed_attempts[key].append(time.time())


def _clear_failures(key: str) -> None:
    with _attempts_lock:
        _failed_attempts.pop(key, None)


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
        
        client = _client_key()
        if _is_locked_out(client):
            logger.warning(f"Login throttled for {client}")
            return jsonify({
                'error': 'Too many failed attempts. Try again later.'
            }), 429
        
        # Get user from service
        user_data = user_service.get_user_by_username(username)
        
        # Verify password. The same generic message and the same code path are
        # used for an unknown username and a bad password, so the response does
        # not reveal which usernames exist.
        if not user_data or not auth_service.verify_password(password, user_data['password_hash']):
            _record_failure(client)
            logger.warning(f"Failed login attempt for username: {username}")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        _clear_failures(client)
        
        # Upgrade legacy or weak hashes now that we have the plaintext in hand.
        if auth_service.needs_rehash(user_data['password_hash']):
            try:
                user_service.set_password_hash(
                    user_data['user_id'], auth_service.hash_password(password)
                )
                logger.info(f"Upgraded password hash for user: {user_data['user_id']}")
            except Exception as exc:
                logger.error(f"Could not upgrade password hash: {exc}")
        
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
            secure=COOKIE_SECURE,
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
        response.set_cookie(
            'session_token', '', expires=0,
            httponly=True, secure=COOKIE_SECURE, samesite='Lax'
        )
        
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
    # Never log session tokens, even truncated — a prefix still narrows a search.
    logger.debug(f"Auth check: authenticated={is_authenticated}")
    
    return jsonify({
        'authenticated': is_authenticated,
        'user': {
            'username': session_data['username'],
            'role': session_data['role']
        } if session_data else None
    })
