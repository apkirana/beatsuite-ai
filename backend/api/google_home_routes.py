"""
Google Home / Google Assistant Integration
Webhook for Google Actions fulfillment
"""

from flask import Blueprint, request, jsonify
import logging
from backend.api.monitoring_routes import load_room_data, save_room_data
from backend.core.iot_controller import iot_manager
from datetime import datetime

logger = logging.getLogger(__name__)

google_home_bp = Blueprint('google_home', __name__, url_prefix='/api/google-home')


@google_home_bp.route('/fulfillment', methods=['POST'])
def google_home_fulfillment():
    """
    Google Home webhook fulfillment endpoint
    Handles requests from Google Assistant Actions
    """
    try:
        req = request.get_json(silent=True, force=True)
        logger.info(f"Google Home request: {req}")
        
        # Extract intent information
        query_result = req.get('queryResult', {})
        intent_name = query_result.get('intent', {}).get('displayName', '')
        parameters = query_result.get('parameters', {})
        
        logger.info(f"Intent: {intent_name}, Parameters: {parameters}")
        
        # Route to appropriate handler
        if intent_name == 'GetRoomStatus':
            response = handle_get_room_status(parameters)
        elif intent_name == 'ControlLight':
            response = handle_control_light(parameters)
        elif intent_name == 'ControlMusic':
            response = handle_control_music(parameters)
        elif intent_name == 'GetPatientVitals':
            response = handle_get_patient_vitals(parameters)
        elif intent_name == 'EnableAI':
            response = handle_enable_ai(parameters)
        elif intent_name == 'DisableAI':
            response = handle_disable_ai(parameters)
        else:
            response = {
                'fulfillmentText': "I'm not sure how to help with that. I can control lights, music, check patient status, or manage AI control."
            }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in Google Home fulfillment: {e}")
        return jsonify({
            'fulfillmentText': f"Sorry, I encountered an error: {str(e)}"
        }), 500


def handle_get_room_status(parameters):
    """Get status of a specific room"""
    room_number = parameters.get('room_number', parameters.get('number'))
    
    if not room_number:
        return {
            'fulfillmentText': 'Which room number would you like to check?'
        }
    
    room_id = f"room_{room_number}"
    rooms = load_room_data()
    
    if room_id not in rooms:
        return {
            'fulfillmentText': f'Room {room_number} not found in the system.'
        }
    
    room = rooms[room_id]
    patient_name = room.get('patient_name', 'Patient')
    
    # Get vitals
    heart_rate = room.get('heart_rate', 'unknown')
    temperature = room.get('temperature', 'unknown')
    spo2 = room.get('spo2', 'unknown')
    sleep_stage = room.get('sleep_stage', 'unknown')
    
    # Get AI status
    ai_active = room.get('ai_is_active', False)
    ai_status = 'active' if ai_active else 'inactive'
    
    response_text = f"Room {room_number}, patient {patient_name}. "
    response_text += f"Heart rate: {heart_rate} BPM, Temperature: {temperature} degrees, Oxygen: {spo2}%, "
    response_text += f"Sleep stage: {sleep_stage}. AI control is {ai_status}."
    
    return {
        'fulfillmentText': response_text
    }


def handle_control_light(parameters):
    """Control room lighting"""
    room_number = parameters.get('room_number', parameters.get('number'))
    action = parameters.get('action', '').lower()  # on, off, dim, brighten
    brightness = parameters.get('brightness')  # 0-100
    color = parameters.get('color')  # blue, warm, cool, etc.
    
    if not room_number:
        return {
            'fulfillmentText': 'Which room would you like to control?'
        }
    
    room_id = f"room_{room_number}"
    rooms = load_room_data()
    
    if room_id not in rooms:
        return {
            'fulfillmentText': f'Room {room_number} not found.'
        }
    
    # Color mapping
    color_map = {
        'blue': '#4A90E2',
        'warm': '#FFD93D',
        'cool': '#E3F4FF',
        'white': '#FFFFFF',
        'red': '#FF6B6B',
        'green': '#6BCF7F',
        'purple': '#9B6BFF'
    }
    
    # Set defaults
    hex_color = '#FFD93D'  # Warm default
    brightness_level = 0.5
    
    # Process action
    if action == 'off':
        brightness_level = 0
    elif action == 'on':
        brightness_level = 0.7
    elif action == 'dim':
        brightness_level = 0.3
    elif action == 'brighten':
        brightness_level = 0.9
    
    # Override with specific brightness
    if brightness is not None:
        brightness_level = float(brightness) / 100.0
    
    # Set color if specified
    if color and color.lower() in color_map:
        hex_color = color_map[color.lower()]
    
    # Apply settings
    success = iot_manager.light_controller.set_color_and_brightness(room_id, hex_color, brightness_level)
    
    # Update room data
    room = rooms[room_id]
    room['current_ai_settings'] = room.get('current_ai_settings', {})
    room['current_ai_settings']['light_hex_color'] = hex_color
    room['current_ai_settings']['light_brightness'] = brightness_level
    room['manual_overrides'] = room.get('manual_overrides', {})
    room['manual_overrides']['is_active'] = True
    room['ai_is_active'] = False
    room['last_updated'] = datetime.now().isoformat()
    save_room_data(rooms)
    
    response_text = f"Room {room_number} lights "
    if action:
        response_text += f"{action}. "
    if brightness is not None:
        response_text += f"Brightness set to {brightness}%. "
    if color:
        response_text += f"Color set to {color}."
    
    return {
        'fulfillmentText': response_text
    }


def handle_control_music(parameters):
    """Control room music"""
    room_number = parameters.get('room_number', parameters.get('number'))
    action = parameters.get('action', '').lower()  # play, stop, pause, louder, softer
    volume = parameters.get('volume')  # 0-100
    
    if not room_number:
        return {
            'fulfillmentText': 'Which room would you like to control?'
        }
    
    room_id = f"room_{room_number}"
    rooms = load_room_data()
    
    if room_id not in rooms:
        return {
            'fulfillmentText': f'Room {room_number} not found.'
        }
    
    # Set defaults
    volume_level = 0.5
    playlist = 'calm'
    
    # Process action
    if action == 'stop' or action == 'off':
        volume_level = 0
    elif action == 'play' or action == 'on':
        volume_level = 0.4
    elif action == 'louder' or action == 'increase':
        volume_level = 0.7
    elif action == 'softer' or action == 'decrease':
        volume_level = 0.2
    
    # Override with specific volume
    if volume is not None:
        volume_level = float(volume) / 100.0
    
    # Apply settings
    success = iot_manager.audio_controller.play_playlist(room_id, playlist, volume_level)
    
    # Update room data
    room = rooms[room_id]
    room['current_ai_settings'] = room.get('current_ai_settings', {})
    room['current_ai_settings']['music_volume'] = volume_level
    room['manual_overrides'] = room.get('manual_overrides', {})
    room['manual_overrides']['is_active'] = True
    room['ai_is_active'] = False
    room['last_updated'] = datetime.now().isoformat()
    save_room_data(rooms)
    
    response_text = f"Room {room_number} music "
    if action:
        response_text += f"{action}. "
    if volume is not None:
        response_text += f"Volume set to {volume}%."
    
    return {
        'fulfillmentText': response_text
    }


def handle_get_patient_vitals(parameters):
    """Get patient vital signs"""
    room_number = parameters.get('room_number', parameters.get('number'))
    
    if not room_number:
        return {
            'fulfillmentText': 'Which patient would you like to check?'
        }
    
    room_id = f"room_{room_number}"
    rooms = load_room_data()
    
    if room_id not in rooms:
        return {
            'fulfillmentText': f'Room {room_number} not found.'
        }
    
    room = rooms[room_id]
    patient_name = room.get('patient_name', 'Patient')
    heart_rate = room.get('heart_rate', 'unknown')
    temperature = room.get('temperature', 'unknown')
    respiratory_rate = room.get('respiratory_rate', 'unknown')
    spo2 = room.get('spo2', 'unknown')
    blood_pressure = room.get('blood_pressure', 'unknown')
    
    response_text = f"{patient_name} in room {room_number}: "
    response_text += f"Heart rate {heart_rate} BPM, "
    response_text += f"Temperature {temperature} degrees Celsius, "
    response_text += f"Respiratory rate {respiratory_rate} breaths per minute, "
    response_text += f"Oxygen saturation {spo2}%, "
    response_text += f"Blood pressure {blood_pressure}."
    
    return {
        'fulfillmentText': response_text
    }


def handle_enable_ai(parameters):
    """Enable AI control for a room"""
    room_number = parameters.get('room_number', parameters.get('number'))
    
    if not room_number:
        return {
            'fulfillmentText': 'Which room should have AI control enabled?'
        }
    
    room_id = f"room_{room_number}"
    rooms = load_room_data()
    
    if room_id not in rooms:
        return {
            'fulfillmentText': f'Room {room_number} not found.'
        }
    
    room = rooms[room_id]
    room['ai_is_active'] = True
    room['ai_mode'] = 'automatic'
    if 'manual_overrides' in room:
        room['manual_overrides']['is_active'] = False
    room['last_updated'] = datetime.now().isoformat()
    
    save_room_data(rooms)
    
    return {
        'fulfillmentText': f'AI control enabled for room {room_number}. The system will now automatically adjust lighting and music based on patient needs.'
    }


def handle_disable_ai(parameters):
    """Disable AI control for a room"""
    room_number = parameters.get('room_number', parameters.get('number'))
    
    if not room_number:
        return {
            'fulfillmentText': 'Which room should have AI control disabled?'
        }
    
    room_id = f"room_{room_number}"
    rooms = load_room_data()
    
    if room_id not in rooms:
        return {
            'fulfillmentText': f'Room {room_number} not found.'
        }
    
    room = rooms[room_id]
    room['ai_is_active'] = False
    room['ai_mode'] = 'manual'
    if 'manual_overrides' not in room:
        room['manual_overrides'] = {}
    room['manual_overrides']['is_active'] = True
    room['last_updated'] = datetime.now().isoformat()
    
    save_room_data(rooms)
    
    return {
        'fulfillmentText': f'AI control disabled for room {room_number}. You can now manually control the environment.'
    }


# Health check endpoint for testing
@google_home_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for Google Home integration"""
    return jsonify({
        'status': 'healthy',
        'service': 'Google Home Integration',
        'version': '1.0'
    })
