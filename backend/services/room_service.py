"""
CRUD Service for Rooms
Handles all database operations for room data
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/rooms.json')

def load_rooms() -> List[Dict]:
    """Load all rooms from JSON file"""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_rooms(rooms: List[Dict]) -> None:
    """Save rooms to JSON file"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(rooms, f, indent=2)

def get_all_rooms() -> List[Dict]:
    """Get all active rooms"""
    rooms = load_rooms()
    return [r for r in rooms if r.get('is_active', True)]

def get_room_by_id(room_id: str) -> Optional[Dict]:
    """Get room by ID"""
    rooms = load_rooms()
    for room in rooms:
        if room['room_id'] == room_id and room.get('is_active', True):
            return room
    return None

def get_available_rooms() -> List[Dict]:
    """Get all available rooms"""
    rooms = get_all_rooms()
    return [r for r in rooms if r['status'] == 'available']

def get_occupied_rooms() -> List[Dict]:
    """Get all occupied rooms"""
    rooms = get_all_rooms()
    return [r for r in rooms if r['status'] == 'occupied']

def create_room(room_data: Dict) -> Dict:
    """Create a new room"""
    rooms = load_rooms()
    
    # Generate room ID if not provided
    if 'room_id' not in room_data:
        room_ids = [r['room_id'] for r in rooms]
        max_id = max([int(rid.replace('room_', '')) for rid in room_ids if rid.startswith('room_')], default=100)
        room_data['room_id'] = f'room_{max_id + 1}'
    
    # Add timestamps
    now = datetime.now().isoformat()
    room_data['created_at'] = now
    room_data['updated_at'] = now
    room_data['is_active'] = True
    
    rooms.append(room_data)
    save_rooms(rooms)
    
    return room_data

def update_room(room_id: str, room_data: Dict) -> Optional[Dict]:
    """Update existing room"""
    rooms = load_rooms()
    
    for i, room in enumerate(rooms):
        if room['room_id'] == room_id:
            room_data['room_id'] = room_id
            room_data['created_at'] = room.get('created_at', datetime.now().isoformat())
            room_data['updated_at'] = datetime.now().isoformat()
            room_data['is_active'] = room_data.get('is_active', True)
            
            rooms[i] = room_data
            save_rooms(rooms)
            return room_data
    
    return None

def delete_room(room_id: str) -> bool:
    """Soft delete room (set is_active to False)"""
    rooms = load_rooms()
    
    for room in rooms:
        if room['room_id'] == room_id:
            room['is_active'] = False
            room['updated_at'] = datetime.now().isoformat()
            save_rooms(rooms)
            return True
    
    return False

def update_room_status(room_id: str, status: str, patient_id: Optional[str] = None) -> Optional[Dict]:
    """Update room status and patient assignment"""
    rooms = load_rooms()
    
    for room in rooms:
        if room['room_id'] == room_id:
            room['status'] = status
            room['patient_id'] = patient_id
            room['updated_at'] = datetime.now().isoformat()
            save_rooms(rooms)
            return room
    
    return None
