"""
CRUD Service for Users
Handles all database operations for user data
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

from backend.auth import password as password_utils

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/users.json')


def hash_password(password: str) -> str:
    """Hash a password with a per-user random salt (PBKDF2-HMAC-SHA256)."""
    return password_utils.hash_password(password)


def set_password_hash(user_id: str, password_hash: str) -> bool:
    """
    Replace the stored hash for one user, leaving every other field alone.

    Used to transparently upgrade a legacy unsalted hash after the user has
    successfully authenticated with it.
    """
    users = load_users()
    for user in users:
        if user.get('user_id') == user_id:
            user['password_hash'] = password_hash
            save_users(users)
            return True
    return False

def load_users() -> List[Dict]:
    """Load all users from JSON file"""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_users(users: List[Dict]) -> None:
    """Save users to JSON file"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def get_all_users() -> List[Dict]:
    """Get all active users (excluding password hashes)"""
    users = load_users()
    active_users = [u for u in users if u.get('is_active', True)]
    # Remove password hash for security
    return [{k: v for k, v in u.items() if k != 'password_hash'} for u in active_users]

def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get user by ID (excluding password hash)"""
    users = load_users()
    for user in users:
        if user['user_id'] == user_id and user.get('is_active', True):
            return {k: v for k, v in user.items() if k != 'password_hash'}
    return None

def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username (including password hash for authentication)"""
    users = load_users()
    for user in users:
        if user['username'] == username and user.get('is_active', True):
            return user
    return None

def create_user(user_data: Dict) -> Dict:
    """Create a new user"""
    users = load_users()
    
    # Check if username exists
    if any(u['username'] == user_data['username'] for u in users):
        raise ValueError("Username already exists")
    
    # Generate user ID
    user_ids = [u['user_id'] for u in users]
    max_id = max([int(uid.replace('U', '')) for uid in user_ids if uid.startswith('U')], default=0)
    user_data['user_id'] = f'U{str(max_id + 1).zfill(3)}'
    
    # Hash password
    if 'password' in user_data:
        user_data['password_hash'] = hash_password(user_data['password'])
        del user_data['password']
    
    # Add timestamps
    now = datetime.now().isoformat()
    user_data['created_at'] = now
    user_data['is_active'] = True
    
    users.append(user_data)
    save_users(users)
    
    # Return without password hash
    return {k: v for k, v in user_data.items() if k != 'password_hash'}

def update_user(user_id: str, user_data: Dict) -> Optional[Dict]:
    """Update existing user"""
    users = load_users()
    
    for i, user in enumerate(users):
        if user['user_id'] == user_id:
            user_data['user_id'] = user_id
            user_data['created_at'] = user.get('created_at', datetime.now().isoformat())
            
            # Update password if provided
            if 'password' in user_data:
                user_data['password_hash'] = hash_password(user_data['password'])
                del user_data['password']
            else:
                user_data['password_hash'] = user['password_hash']
            
            user_data['is_active'] = user_data.get('is_active', True)
            
            users[i] = user_data
            save_users(users)
            
            # Return without password hash
            return {k: v for k, v in user_data.items() if k != 'password_hash'}
    
    return None

def delete_user(user_id: str) -> bool:
    """Soft delete user (set is_active to False)"""
    users = load_users()
    
    for user in users:
        if user['user_id'] == user_id:
            user['is_active'] = False
            save_users(users)
            return True
    
    return False
