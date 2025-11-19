"""
User model
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class User:
    """User data model"""
    user_id: str
    username: str
    password_hash: str
    role: str  # 'admin', 'nurse', 'family'
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    is_active: bool = True
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary"""
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'is_active': self.is_active
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
            data['created_at'] = self.created_at.isoformat() if self.created_at else None
            data['last_login'] = self.last_login.isoformat() if self.last_login else None
        
        return data
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        permissions = {
            'admin': ['view_all', 'edit_all', 'manage_users', 'override_ai'],
            'nurse': ['view_assigned', 'edit_assigned', 'override_ai', 'chat'],
            'family': ['view_assigned', 'chat']
        }
        
        return permission in permissions.get(self.role, [])
