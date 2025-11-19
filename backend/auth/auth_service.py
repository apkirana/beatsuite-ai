"""
Authentication Service
Handles user login, logout, and session management
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging
from backend.services import user_service

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service with session management"""
    
    def __init__(self):
        self.sessions = {}  # In production, use Redis or database
        self.session_timeout = timedelta(hours=8)
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 (use bcrypt in production)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return self.hash_password(password) == hashed
    
    def create_session(self, user_id: str, user_data: Dict) -> str:
        """Create a new session and return session token"""
        session_token = secrets.token_urlsafe(32)
        
        self.sessions[session_token] = {
            'user_id': user_id,
            'username': user_data.get('username'),
            'role': user_data.get('role'),
            'full_name': user_data.get('full_name'),
            'created_at': datetime.now(),
            'expires_at': datetime.now() + self.session_timeout,
            'last_activity': datetime.now()
        }
        
        logger.info(f"Session created for user: {user_id}")
        return session_token
    
    def get_session(self, session_token: str) -> Optional[Dict]:
        """Get session data if valid"""
        if not session_token or session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        
        # Check if session expired
        if datetime.now() > session['expires_at']:
            del self.sessions[session_token]
            logger.info(f"Session expired for user: {session['user_id']}")
            return None
        
        # Update last activity
        session['last_activity'] = datetime.now()
        return session
    
    def destroy_session(self, session_token: str) -> bool:
        """Destroy a session (logout)"""
        if session_token in self.sessions:
            user_id = self.sessions[session_token]['user_id']
            del self.sessions[session_token]
            logger.info(f"Session destroyed for user: {user_id}")
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        now = datetime.now()
        expired = [
            token for token, session in self.sessions.items()
            if now > session['expires_at']
        ]
        
        for token in expired:
            del self.sessions[token]
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")


# Singleton instance
auth_service = AuthService()
