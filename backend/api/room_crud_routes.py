"""
Room Management CRUD API Routes
Provides REST API endpoints for room management
"""
from flask import Blueprint, request, jsonify, session
from backend.auth.decorators import login_required, role_required
from backend.services import room_service

rooms_crud_bp = Blueprint('rooms_crud', __name__, url_prefix='/api/rooms-manage')

@rooms_crud_bp.route('', methods=['GET'])
@login_required
def get_rooms():
    """Get all rooms"""
    try:
        rooms = room_service.get_all_rooms()
        return jsonify({'success': True, 'rooms': rooms}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@rooms_crud_bp.route('/<room_id>', methods=['GET'])
@login_required
def get_room(room_id):
    """Get room by ID"""
    try:
        room = room_service.get_room_by_id(room_id)
        if room:
            return jsonify({'success': True, 'room': room}), 200
        return jsonify({'success': False, 'error': 'Room not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@rooms_crud_bp.route('/available', methods=['GET'])
@login_required
def get_available_rooms():
    """Get all available rooms"""
    try:
        rooms = room_service.get_available_rooms()
        return jsonify({'success': True, 'rooms': rooms}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@rooms_crud_bp.route('/occupied', methods=['GET'])
@login_required
def get_occupied_rooms():
    """Get all occupied rooms"""
    try:
        rooms = room_service.get_occupied_rooms()
        return jsonify({'success': True, 'rooms': rooms}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@rooms_crud_bp.route('', methods=['POST'])
@role_required(['admin'])
def create_room():
    """Create new room"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['room_number', 'floor', 'ward', 'room_type', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        room = room_service.create_room(data)
        return jsonify({'success': True, 'room': room, 'message': 'Room created successfully'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@rooms_crud_bp.route('/<room_id>', methods=['PUT'])
@role_required(['admin', 'nurse'])
def update_room(room_id):
    """Update existing room"""
    try:
        data = request.get_json()
        room = room_service.update_room(room_id, data)
        
        if room:
            return jsonify({'success': True, 'room': room, 'message': 'Room updated successfully'}), 200
        return jsonify({'success': False, 'error': 'Room not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@rooms_crud_bp.route('/<room_id>/status', methods=['PATCH'])
@role_required(['admin', 'nurse'])
def update_room_status(room_id):
    """Update room status"""
    try:
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'success': False, 'error': 'Missing status field'}), 400
        
        room = room_service.update_room_status(
            room_id, 
            data['status'], 
            data.get('patient_id')
        )
        
        if room:
            return jsonify({'success': True, 'room': room, 'message': 'Room status updated'}), 200
        return jsonify({'success': False, 'error': 'Room not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@rooms_crud_bp.route('/<room_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_room(room_id):
    """Delete room (soft delete)"""
    try:
        success = room_service.delete_room(room_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Room deleted successfully'}), 200
        return jsonify({'success': False, 'error': 'Room not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
