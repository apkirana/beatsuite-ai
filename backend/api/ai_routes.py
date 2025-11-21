"""
AI Assistant API routes
Gemini AI integration endpoints
"""

from flask import Blueprint, request, jsonify
from backend.auth.decorators import login_required, role_required
from backend.ai.gemini_service import gemini_service
from backend.api.monitoring_routes import load_room_data, save_room_data
from datetime import datetime
import logging
import os

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


@ai_bp.route('/optimize-adaptive/<room_id>', methods=['POST'])
@role_required(['admin', 'nurse'])
def optimize_environment_adaptive(room_id):
    """
    Get AI recommendations using adaptive rules system
    """
    try:
        rooms = load_room_data()
        
        if room_id not in rooms:
            return jsonify({'error': 'Room not found'}), 404
        
        room_data = rooms[room_id]
        current_env = room_data.get('current_ai_settings', {})
        
        # Use adaptive optimization
        optimization = gemini_service.optimize_environment_adaptive(room_data, current_env)
        
        return jsonify({
            'success': True,
            'room_id': room_id,
            'optimization': optimization,
            'adaptive_rules': True
        })
        
    except Exception as e:
        logger.error(f"Error in adaptive environment optimization: {e}")
        return jsonify({'error': 'Adaptive optimization failed'}), 500


@ai_bp.route('/rules/status', methods=['GET'])
@login_required
def adaptive_rules_status():
    """
    Get status of adaptive rules system
    """
    try:
        rules_count = len(gemini_service.adaptive_rules.get('adaptive_rules', []))
        
        return jsonify({
            'success': True,
            'adaptive_rules_enabled': rules_count > 0,
            'rules_count': rules_count,
            'ai_available': gemini_service.is_available()
        })
        
    except Exception as e:
        logger.error(f"Error getting rules status: {e}")
        return jsonify({'error': 'Status check failed'}), 500
        
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


@ai_bp.route('/chat/<room_id>', methods=['POST'])
@login_required
def voice_chat(room_id):
    """
    Voice chat with AI assistant for specific room
    Optimized for voice conversations with shorter, more natural responses
    """
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        context_type = data.get('context', 'voice_conversation')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get room context
        rooms = load_room_data()
        if room_id not in rooms:
            return jsonify({'error': 'Room not found'}), 404
        
        room_context = rooms[room_id]
        
        # Get patient vitals with defaults
        vitals = room_context.get('vitals', {})
        patient_name = room_context.get('patient_name', 'Patient')
        
        # Create detailed patient profile for personalization
        patient_profile = {
            'name': patient_name,
            'room': room_id,
            'heart_rate': vitals.get('heart_rate', 'Normal'),
            'temperature': vitals.get('temperature', 'Normal'),
            'spo2': vitals.get('spo2', 'Normal'),
            'movement': vitals.get('movement_level', 'Normal'),
            'pain_level': vitals.get('pain_level', 'None reported'),
            'sleep_quality': vitals.get('sleep_quality', 'Normal'),
            'age': room_context.get('age', 'Adult'),
            'condition': room_context.get('condition', 'General care'),
            'admission_reason': room_context.get('admission_reason', 'Monitoring'),
            'allergies': room_context.get('allergies', 'None known'),
            'medications': room_context.get('medications', []),
            'last_checkup': room_context.get('last_checkup', 'Earlier today')
        }
        
        # Create highly personalized voice prompt
        voice_prompt = f"""
You are Dr. AI, {patient_name}'s personal healthcare assistant. You know {patient_name} well and have been monitoring their care.

PATIENT CONTEXT - {patient_name} (Room {room_id}):
• Current Health: {patient_profile['condition']}
• Admission: {patient_profile['admission_reason']}
• Age Group: {patient_profile['age']}
• Allergies: {patient_profile['allergies']}
• Current Medications: {', '.join(patient_profile['medications']) if patient_profile['medications'] else 'None currently'}

CURRENT VITALS (Live monitoring):
• Heart Rate: {patient_profile['heart_rate']} BPM
• Temperature: {patient_profile['temperature']}°F  
• Blood Oxygen: {patient_profile['spo2']}%
• Activity Level: {patient_profile['movement']}
• Pain Level: {patient_profile['pain_level']}
• Sleep Quality: {patient_profile['sleep_quality']}
• Last Assessment: {patient_profile['last_checkup']}

ROOM ENVIRONMENT (Auto-adjusted for {patient_name}'s comfort):
• Lighting: {room_context.get('light_brightness', 50)}% brightness ({room_context.get('light_color', 'neutral')} tone)
• Music Therapy: {room_context.get('music_volume', 30)}% volume ({room_context.get('music_type', 'ambient')} style)
• Climate: {room_context.get('room_temperature', 72)}°F

CONVERSATION HISTORY (Recent context):
{chr(10).join([f"• {patient_name}: {conv['message']} → Dr. AI: {conv['response']}" for conv in room_context.get('conversation_history', [])[-3:]]) if room_context.get('conversation_history') else "• This is your first conversation with " + patient_name + " today."}

{patient_name} just said: "{message}"

Respond as their caring, knowledgeable healthcare assistant who:
1. Addresses them BY NAME ({patient_name})
2. References their specific health status when relevant
3. Remembers their condition and care plan
4. Speaks naturally as if you've been caring for them
5. Offers personalized medical guidance based on their profile
6. Asks specific follow-up questions about their condition
7. Builds on previous conversations and shows continuity

Keep responses under 3 sentences, warm and professional. You know {patient_name}'s history and current needs.
"""
        
        # Get AI response using chat assistant
        ai_response = gemini_service.chat_assistant(voice_prompt, room_context)
        
        # Store conversation in history
        conversation_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'response': ai_response
        }
        
        # Update conversation history (keep last 10 entries)
        conversation_history = room_context.get('conversation_history', [])
        conversation_history.append(conversation_entry)
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
            
        room_context['conversation_history'] = conversation_history
        rooms[room_id] = room_context
        
        # Save updated room data with conversation history
        save_room_data(rooms)
        
        # Log the voice conversation
        logger.info(f"Voice chat in {room_id} - User: {message[:50]}... | AI: {ai_response[:50]}...")
        
        return jsonify({
            'success': True,
            'user_message': message,
            'ai_response': ai_response,
            'room_id': room_id,
            'context': context_type
        })
        
    except Exception as e:
        logger.error(f"Error in voice chat for room {room_id}: {e}")
        return jsonify({
            'success': False, 
            'error': 'Voice chat temporarily unavailable. Please try again.'
        }), 500


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


@ai_bp.route('/live/token', methods=['POST'])
@login_required
def get_live_token():
    """
    Get API token for Gemini Live WebSocket connection
    Used by frontend to establish real-time voice chat
    """
    try:
        data = request.get_json()
        room_id = data.get('room_id')
        
        if not room_id:
            return jsonify({'error': 'room_id required'}), 400
        
        # Get API key from environment
        api_key = os.environ.get('GOOGLE_API_KEY')
        
        if not api_key:
            return jsonify({
                'error': 'API key not configured',
                'message': 'GOOGLE_API_KEY environment variable is not set. Please configure your API key.',
                'help': 'Get your API key from https://makersuite.google.com/app/apikey'
            }), 503
        
        # Validate API key format (basic check)
        if not api_key.startswith('AI') or len(api_key) < 20:
            return jsonify({
                'error': 'Invalid API key format',
                'message': 'The API key appears to be invalid. Please check your GOOGLE_API_KEY.'
            }), 503
        
        logger.info(f"Providing Gemini Live API token for room: {room_id}")
        
        # Return the API key for WebSocket connection
        # Note: In production, you might want to create session-specific tokens
        return jsonify({
            'success': True,
            'token': api_key,
            'room_id': room_id,
            'endpoint': 'wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent'
        })
        
    except Exception as e:
        logger.error(f"Error getting live token: {e}")
        return jsonify({'error': str(e)}), 500
