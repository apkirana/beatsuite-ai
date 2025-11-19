"""
Testing API Routes
Provides synthetic data generation and testing endpoints for development
"""
from flask import Blueprint, request, jsonify
from backend.auth.decorators import login_required, role_required
from backend.core.smartwatch import smartwatch_manager
from backend.core.ai_engine import BeatSuiteAI
from backend.core.iot_controller import SmartLightController, SmartAudioController
import random
from datetime import datetime

test_bp = Blueprint('test', __name__, url_prefix='/api/test')

# Initialize controllers
ai_engine = BeatSuiteAI()
light_controller = SmartLightController('simulated')
audio_controller = SmartAudioController('simulated')


@test_bp.route('/synthetic-data/<patient_id>', methods=['GET'])
@login_required
def generate_synthetic_data(patient_id):
    """
    Generate synthetic patient data for testing
    
    Query parameters:
    - scenario: 'normal', 'sleeping', 'pain', 'morning_wake', 'evening_rest'
    """
    scenario = request.args.get('scenario', 'normal')
    
    # Base vitals
    data = {
        'patient_id': patient_id,
        'timestamp': datetime.now().isoformat()
    }
    
    # Scenario-based synthetic data
    if scenario == 'normal':
        data.update({
            'heart_rate': random.randint(65, 85),
            'spo2': random.randint(97, 100),
            'movement': round(random.uniform(0.3, 0.6), 2),
            'temperature': round(random.uniform(97.5, 98.9), 1),
            'respiratory_rate': random.randint(14, 18),
            'blood_pressure_systolic': random.randint(110, 130),
            'blood_pressure_diastolic': random.randint(70, 85),
            'state': 'awake and comfortable'
        })
    
    elif scenario == 'sleeping':
        data.update({
            'heart_rate': random.randint(50, 65),
            'spo2': random.randint(96, 99),
            'movement': round(random.uniform(0.0, 0.2), 2),
            'temperature': round(random.uniform(97.0, 98.2), 1),
            'respiratory_rate': random.randint(12, 16),
            'blood_pressure_systolic': random.randint(100, 120),
            'blood_pressure_diastolic': random.randint(60, 75),
            'state': 'deep sleep'
        })
    
    elif scenario == 'pain':
        data.update({
            'heart_rate': random.randint(95, 120),
            'spo2': random.randint(94, 97),
            'movement': round(random.uniform(0.6, 0.9), 2),
            'temperature': round(random.uniform(98.5, 99.8), 1),
            'respiratory_rate': random.randint(18, 24),
            'blood_pressure_systolic': random.randint(130, 150),
            'blood_pressure_diastolic': random.randint(85, 95),
            'state': 'distressed - possible pain'
        })
    
    elif scenario == 'morning_wake':
        data.update({
            'heart_rate': random.randint(70, 85),
            'spo2': random.randint(97, 100),
            'movement': round(random.uniform(0.4, 0.7), 2),
            'temperature': round(random.uniform(97.8, 98.6), 1),
            'respiratory_rate': random.randint(15, 19),
            'blood_pressure_systolic': random.randint(115, 135),
            'blood_pressure_diastolic': random.randint(72, 88),
            'state': 'waking up'
        })
    
    elif scenario == 'evening_rest':
        data.update({
            'heart_rate': random.randint(60, 75),
            'spo2': random.randint(96, 99),
            'movement': round(random.uniform(0.1, 0.3), 2),
            'temperature': round(random.uniform(97.5, 98.4), 1),
            'respiratory_rate': random.randint(13, 17),
            'blood_pressure_systolic': random.randint(105, 125),
            'blood_pressure_diastolic': random.randint(65, 80),
            'state': 'relaxing for sleep'
        })
    
    return jsonify({
        'success': True,
        'data': data,
        'scenario': scenario
    }), 200


@test_bp.route('/simulate-ai-adjustment/<patient_id>', methods=['POST'])
@role_required(['admin', 'nurse'])
def simulate_ai_adjustment(patient_id):
    """
    Simulate AI auto-adjustment based on patient data
    
    POST body:
    {
        "heart_rate": 70,
        "movement": 0.3,
        "spo2": 98,
        "scenario": "optional"
    }
    """
    data = request.get_json()
    
    # Use provided data or generate scenario-based data
    if 'scenario' in data:
        # Generate synthetic data for scenario
        scenario = data['scenario']
        response = generate_synthetic_data(patient_id)
        smartwatch_data = response[0].get_json()['data']
    else:
        # Use provided vitals
        smartwatch_data = {
            'heart_rate': data.get('heart_rate', 70),
            'movement': data.get('movement', 0.3),
            'spo2': data.get('spo2', 98),
            'timestamp': datetime.now()
        }
    
    # Process through AI engine
    ai_recommendations = ai_engine.process_smartwatch_data(patient_id, smartwatch_data)
    
    # Apply to virtual environment
    light_settings = ai_recommendations['light']
    music_settings = ai_recommendations['music']
    
    # Simulate IoT control
    light_controller.set_color_and_brightness(
        patient_id,
        light_settings['color_hex'],
        light_settings['brightness']
    )
    
    audio_controller.play_playlist(
        patient_id,
        music_settings['playlist_id'],
        music_settings['volume']
    )
    
    return jsonify({
        'success': True,
        'patient_id': patient_id,
        'input_data': smartwatch_data,
        'ai_analysis': ai_recommendations['patient_state'],
        'environment_adjustments': {
            'light': light_settings,
            'music': music_settings
        },
        'ai_reasoning': ai_recommendations['ai_reasoning']
    }), 200


@test_bp.route('/environment-status/<room_id>', methods=['GET'])
@login_required
def get_environment_status(room_id):
    """
    Get current virtual environment status
    """
    light_state = light_controller.current_state.get(room_id, {})
    audio_state = audio_controller.current_state.get(room_id, {})
    
    return jsonify({
        'success': True,
        'room_id': room_id,
        'light': light_state,
        'audio': audio_state,
        'timestamp': datetime.now().isoformat()
    }), 200


@test_bp.route('/scenarios', methods=['GET'])
def list_scenarios():
    """
    List all available test scenarios
    """
    scenarios = {
        'normal': {
            'description': 'Normal awake state with healthy vitals',
            'expected_environment': 'Neutral lighting, ambient music'
        },
        'sleeping': {
            'description': 'Deep sleep with low heart rate and movement',
            'expected_environment': 'Dim amber light, sleep binaural beats'
        },
        'pain': {
            'description': 'Elevated heart rate and movement indicating pain/discomfort',
            'expected_environment': 'Red light therapy, healing frequencies'
        },
        'morning_wake': {
            'description': 'Morning wake-up phase with increasing activity',
            'expected_environment': 'Blue-enriched light, energizing music'
        },
        'evening_rest': {
            'description': 'Evening wind-down phase preparing for sleep',
            'expected_environment': 'Warm light, calming music'
        }
    }
    
    return jsonify({
        'success': True,
        'scenarios': scenarios,
        'usage': {
            'generate_data': '/api/test/synthetic-data/<patient_id>?scenario=<scenario_name>',
            'simulate_ai': 'POST /api/test/simulate-ai-adjustment/<patient_id> with {scenario: <scenario_name>}'
        }
    }), 200


@test_bp.route('/batch-simulation/<patient_id>', methods=['POST'])
@role_required(['admin', 'nurse'])
def batch_simulation(patient_id):
    """
    Run multiple scenarios in sequence to test AI adaptations
    
    POST body:
    {
        "scenarios": ["normal", "evening_rest", "sleeping", "pain"],
        "interval_seconds": 2
    }
    """
    data = request.get_json()
    scenarios = data.get('scenarios', ['normal', 'sleeping', 'pain'])
    
    results = []
    for scenario in scenarios:
        # Generate data
        synthetic_data_response = generate_synthetic_data(patient_id)
        synthetic_data = synthetic_data_response[0].get_json()['data']
        
        # Process with AI
        smartwatch_data = {
            'heart_rate': synthetic_data['heart_rate'],
            'movement': synthetic_data['movement'],
            'spo2': synthetic_data['spo2'],
            'timestamp': datetime.now()
        }
        
        ai_recommendations = ai_engine.process_smartwatch_data(patient_id, smartwatch_data)
        
        results.append({
            'scenario': scenario,
            'patient_state': synthetic_data['state'],
            'vitals': {
                'heart_rate': synthetic_data['heart_rate'],
                'spo2': synthetic_data['spo2'],
                'movement': synthetic_data['movement']
            },
            'ai_recommendations': {
                'light': ai_recommendations['light'],
                'music': ai_recommendations['music'],
                'reasoning': ai_recommendations['ai_reasoning']
            }
        })
    
    return jsonify({
        'success': True,
        'patient_id': patient_id,
        'results': results
    }), 200
