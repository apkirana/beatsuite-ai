"""
Room management API routes
"""

from flask import Blueprint, request, jsonify
from backend.auth.decorators import login_required, role_required
from backend.core.ai_engine import process_patient_update
from backend.core.smartwatch import smartwatch_manager
from backend.core.iot_controller import apply_ai_settings_to_room
from datetime import datetime
import json
import os
import logging

logger = logging.getLogger(__name__)

room_bp = Blueprint('rooms', __name__, url_prefix='/api/rooms')


def load_room_data():
    """Load room monitoring data from file"""
    data_file = os.path.join(os.path.dirname(__file__), '../../backend/data/room_monitoring.json')
    try:
        with open(data_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading room data: {e}")
        return {}


def save_room_data(rooms):
    """Save room monitoring data to file"""
    data_file = os.path.join(os.path.dirname(__file__), '../../backend/data/room_monitoring.json')
    try:
        with open(data_file, 'w') as f:
            json.dump(rooms, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving room data: {e}")
        return False


@room_bp.route('', methods=['GET'])
@room_bp.route('/', methods=['GET'])
@login_required
def get_all_rooms():
    """Get list of all rooms"""
    try:
        rooms = load_room_data()
        
        # Filter based on user role
        user_role = request.current_user.get('role')
        
        if user_role == 'family':
            # Family members only see their assigned rooms
            # In production, filter based on actual assignments
            rooms = {k: v for k, v in rooms.items() if k in ['room_101']}
        
        room_list = []
        for room_id, data in rooms.items():
            # Get live smartwatch data if available
            patient_id = data.get('patient_id')
            vitals = {
                'heart_rate': data.get('heart_rate', 70),
                'temperature': data.get('temperature', 98.6),
                'respiratory_rate': data.get('respiratory_rate', 16),
                'spo2': data.get('oxygen_level', 98),
                'blood_pressure': data.get('blood_pressure', '120/80')
            }
            
            # Try to get fresh data from smartwatch
            if patient_id and data.get('ai_is_active'):
                try:
                    sw_data = smartwatch_manager.get_patient_data(patient_id)
                    if sw_data:
                        vitals['heart_rate'] = int(sw_data.get('heart_rate', vitals['heart_rate']))
                        vitals['temperature'] = round(sw_data.get('temperature', vitals['temperature']), 1)
                        vitals['respiratory_rate'] = int(sw_data.get('respiratory_rate', vitals['respiratory_rate']))
                        vitals['spo2'] = int(sw_data.get('spo2', vitals['spo2']))
                except Exception as e:
                    logger.warning(f"Failed to get smartwatch data for {patient_id}: {e}")
            
            room_list.append({
                'room_id': room_id,
                'room_number': room_id.replace('_', ' ').title(),
                'patient_name': data.get('patient_name'),
                'ai_control_active': data.get('ai_is_active', False),
                'patient_status': data.get('patient_status'),
                'vitals': vitals,
                'current_state': {
                    'sleep_stage': data.get('sleep_stage', 'AWAKE').upper().replace('_', ' '),
                    'pain_detected': data.get('pain_detected', False),
                    'movement_level': data.get('movement_level', 'low')
                },
                'environment': data.get('current_ai_settings', {})
            })
        
        return jsonify({'rooms': room_list}), 200
        
    except Exception as e:
        logger.error(f"Error fetching rooms: {e}")
        return jsonify({'error': 'Failed to fetch rooms'}), 500


@room_bp.route('/<room_id>', methods=['GET'])
@login_required
def get_room_data(room_id):
    """Get detailed room data with live AI updates"""
    try:
        rooms = load_room_data()
        
        if room_id not in rooms:
            return jsonify({'error': f'Room {room_id} not found'}), 404
        
        room = rooms[room_id]
        patient_id = room.get('patient_id')
        
        # If AI is active, get fresh smartwatch data and update
        if room['ai_is_active'] and patient_id:
            try:
                # Get smartwatch data
                smartwatch_data = smartwatch_manager.get_patient_data(patient_id)
                
                if smartwatch_data:
                    # Process through AI
                    ai_output = process_patient_update(patient_id, smartwatch_data)
                    
                    # Apply to IoT
                    apply_ai_settings_to_room(room_id, ai_output)
                    
                    # Update room data
                    room['current_ai_settings'] = {
                        'light_hex_color': ai_output['light']['color_hex'],
                        'light_brightness': ai_output['light']['brightness'],
                        'music_playlist_id': ai_output['music']['playlist_id'],
                        'music_volume': ai_output['music']['volume'],
                        'temperature': room['current_ai_settings'].get('temperature', 72),
                        'ai_reasoning': ai_output['ai_reasoning']
                    }
                    
                    # Update vitals
                    patient_state = ai_output['patient_state']
                    room['heart_rate'] = patient_state['heart_rate']
                    room['oxygen_level'] = patient_state['oxygen_level']
                    room['sleep_stage'] = patient_state['sleep_stage']
                    room['pain_detected'] = patient_state['pain_detected']
                    room['last_updated'] = datetime.now().isoformat()
                    
                    logger.info(f"AI updated {room_id}: {patient_state['sleep_stage']}")
            
            except Exception as e:
                logger.error(f"Error in AI loop: {e}")
        
        # Format the response to match frontend expectations
        response = {
            'room_id': room_id,
            'room_number': room_id.replace('_', ' ').title(),
            'patient_name': room.get('patient_name'),
            'ai_control_active': room.get('ai_is_active', False),
            'vitals': {
                'heart_rate': room.get('heart_rate', 70),
                'temperature': room.get('temperature', 98.6),
                'respiratory_rate': room.get('respiratory_rate', 16),
                'spo2': room.get('oxygen_level', 98),
                'blood_pressure': room.get('blood_pressure', '120/80')
            },
            'current_state': {
                'sleep_stage': room.get('sleep_stage', 'AWAKE').upper().replace('_', ' '),
                'pain_detected': room.get('pain_detected', False),
                'movement_level': room.get('movement_level', 'low')
            },
            'environment': {
                'light_level': room.get('current_ai_settings', {}).get('light_brightness', 50),
                'light_color': room.get('current_ai_settings', {}).get('light_hex_color', '#FFE4B5'),
                'music_volume': room.get('current_ai_settings', {}).get('music_volume', 30),
                'music_type': room.get('current_ai_settings', {}).get('music_playlist_id', 'relaxing')
            },
            'ai_insights': {
                'sleep_quality': room.get('current_ai_settings', {}).get('ai_reasoning', 'Monitoring patient comfort'),
                'circadian_status': f"Last updated: {room.get('last_updated', 'N/A')}"
            }
        }
        
        return jsonify({'room': response}), 200
        
    except Exception as e:
        logger.error(f"Error getting room data: {e}")
        return jsonify({'error': 'Failed to fetch room data'}), 500


@room_bp.route('/<room_id>/override', methods=['POST'])
@role_required(['admin', 'nurse'])
def set_override(room_id):
    """Set manual override for room"""
    try:
        rooms = load_room_data()
        
        if room_id not in rooms:
            return jsonify({'error': f'Room {room_id} not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Invalid request body'}), 400
        
        brightness = data.get('brightness')
        volume = data.get('volume')
        
        logger.info(f"OVERRIDE for {room_id} by {request.current_user['username']}: B={brightness}, V={volume}")
        
        # Update room and save
        room = rooms[room_id]
        room['ai_is_active'] = False
        room['ai_mode'] = 'manual_override'
        room['manual_overrides'] = {
            'is_active': True,
            'brightness': float(brightness) if brightness is not None else 0.5,
            'volume': float(volume) if volume is not None else 0.2,
            'overridden_by': request.current_user['username'],
            'overridden_at': datetime.now().isoformat()
        }
        
        # Save changes
        save_room_data(rooms)
        
        return jsonify({
            'success': True,
            'message': 'Manual override activated',
            'ai_control_active': False
        }), 200
        
    except Exception as e:
        logger.error(f"Error setting override: {e}")
        return jsonify({'error': 'Failed to set override'}), 500


@room_bp.route('/<room_id>/resume', methods=['POST'])
@role_required(['admin', 'nurse'])
def resume_ai(room_id):
    """Resume AI control for room"""
    try:
        rooms = load_room_data()
        
        if room_id not in rooms:
            return jsonify({'error': f'Room {room_id} not found'}), 404
        
        logger.info(f"RESUME AI for {room_id} by {request.current_user['username']}")
        
        room = rooms[room_id]
        room['ai_is_active'] = True
        room['ai_mode'] = 'automatic'
        if 'manual_overrides' in room:
            room['manual_overrides']['is_active'] = False
        room['last_updated'] = datetime.now().isoformat()
        
        # Save changes
        save_room_data(rooms)
        
        return jsonify({
            'success': True,
            'message': 'AI control resumed',
            'ai_control_active': True
        }), 200
        
    except Exception as e:
        logger.error(f"Error resuming AI: {e}")
        return jsonify({'error': 'Failed to resume AI'}), 500
