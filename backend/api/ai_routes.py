"""
AI Assistant API routes
Gemini AI integration endpoints
"""

from flask import Blueprint, request, jsonify
from backend.auth.decorators import login_required, role_required
from backend.ai.gemini_service import gemini_service
from backend.api.room_routes import load_room_data
import logging

logger = logging.getLogger(__name__)

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')


@ai_bp.route('/analyze/<room_id>', methods=['GET'])
@login_required
def analyze_patient(room_id):
    """
    AI analysis of patient vitals
    """
    try:
        rooms = load_room_data()
        
        if room_id not in rooms:
            return jsonify({'error': 'Room not found'}), 404
        
        room_data = rooms[room_id]
        
        # Get AI analysis
        analysis = gemini_service.analyze_patient_vitals(room_data)
        
        return jsonify({
            'success': True,
            'room_id': room_id,
            'patient_name': room_data.get('patient_name'),
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Error in AI analysis: {e}")
        return jsonify({'error': 'Analysis failed'}), 500


@ai_bp.route('/summary/<room_id>', methods=['GET'])
@login_required
def generate_summary(room_id):
    """
    Generate AI health summary for patient
    """
    try:
        rooms = load_room_data()
        
        if room_id not in rooms:
            return jsonify({'error': 'Room not found'}), 404
        
        room_data = rooms[room_id]
        patient_name = room_data.get('patient_name', 'Patient')
        
        # Generate summary
        summary = gemini_service.generate_health_summary(patient_name, room_data)
        
        return jsonify({
            'success': True,
            'room_id': room_id,
            'patient_name': patient_name,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return jsonify({'error': 'Summary generation failed'}), 500


@ai_bp.route('/optimize/<room_id>', methods=['POST'])
@role_required(['admin', 'nurse'])
def optimize_environment(room_id):
    """
    Get AI recommendations for room environment
    """
    try:
        rooms = load_room_data()
        
        if room_id not in rooms:
            return jsonify({'error': 'Room not found'}), 404
        
        room_data = rooms[room_id]
        current_env = room_data.get('current_ai_settings', {})
        
        # Get AI optimization
        optimization = gemini_service.optimize_environment(room_data, current_env)
        
        return jsonify({
            'success': True,
            'room_id': room_id,
            'optimization': optimization
        })
        
    except Exception as e:
        logger.error(f"Error in environment optimization: {e}")
        return jsonify({'error': 'Optimization failed'}), 500


@ai_bp.route('/chat', methods=['POST'])
@login_required
def chat_assistant():
    """
    Chat with AI assistant about patient care
    """
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        room_id = data.get('room_id')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Get context if room_id provided
        context = {}
        if room_id:
            rooms = load_room_data()
            if room_id in rooms:
                context = rooms[room_id]
        
        # Get AI response
        answer = gemini_service.chat_assistant(question, context)
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': answer,
            'room_id': room_id
        })
        
    except Exception as e:
        logger.error(f"Error in chat assistant: {e}")
        return jsonify({'error': 'Chat failed'}), 500


@ai_bp.route('/status', methods=['GET'])
@login_required
def ai_status():
    """
    Check if Gemini AI is available
    """
    available = gemini_service.is_available()
    
    return jsonify({
        'ai_enabled': available,
        'provider': 'gemini-pro' if available else 'fallback',
        'message': 'Gemini AI is active' if available else 'Using fallback AI rules'
    })
