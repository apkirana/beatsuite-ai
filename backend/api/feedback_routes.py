"""
Feedback Collection and Memory API Routes
Endpoints for submitting feedback and retrieving memory-based recommendations
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

from backend.auth.decorators import login_required
from backend.services.feedback_service import feedback_service
from backend.services.agent_memory_service import agent_memory_service

logger = logging.getLogger(__name__)

feedback_bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')


@feedback_bp.route('/submit', methods=['POST'])
@login_required
def submit_feedback():
    """
    Submit feedback for a patient-agent interaction
    
    Request JSON:
    {
        "patient_id": "P001",
        "interaction_type": "music_suggestion|lighting|environment_control|pain_management",
        "rating": "positive|negative|neutral",
        "rating_score": 1-5 (optional),
        "user_comment": "optional comment",
        "interaction_context": {
            "action": "Played Disney Classics",
            "situation": "Patient awake during daytime",
            "timestamp": "ISO timestamp"
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['patient_id', 'interaction_type', 'rating']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        patient_id = data['patient_id']
        interaction_type = data['interaction_type']
        rating = data['rating']
        rating_score = data.get('rating_score')
        user_comment = data.get('user_comment')
        interaction_context = data.get('interaction_context', {})
        
        # Submit feedback
        result = feedback_service.submit_feedback(
            patient_id=patient_id,
            interaction_type=interaction_type,
            rating=rating,
            rating_score=rating_score,
            user_comment=user_comment,
            interaction_context=interaction_context
        )
        
        if result['success']:
            logger.info(f"Feedback submitted for patient {patient_id}: {interaction_type} - {rating}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}", exc_info=True)
        return jsonify({'error': 'Failed to submit feedback'}), 500


@feedback_bp.route('/history/<patient_id>', methods=['GET'])
@login_required
def get_feedback_history(patient_id):
    """
    Get feedback history for a patient
    
    Query parameters:
        limit: Maximum number of records to return (optional)
    """
    try:
        limit = request.args.get('limit', type=int)
        
        result = feedback_service.get_feedback_history(patient_id, limit=limit)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    
    except Exception as e:
        logger.error(f"Error retrieving feedback history: {e}")
        return jsonify({'error': 'Failed to retrieve feedback history'}), 500


@feedback_bp.route('/summary/<patient_id>', methods=['GET'])
@login_required
def get_feedback_summary(patient_id):
    """Get feedback summary and statistics for a patient"""
    try:
        result = feedback_service.get_feedback_summary(patient_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    
    except Exception as e:
        logger.error(f"Error retrieving feedback summary: {e}")
        return jsonify({'error': 'Failed to retrieve feedback summary'}), 500


@feedback_bp.route('/preferences/<patient_id>', methods=['GET'])
@login_required
def get_preferences(patient_id):
    """Get learned interaction preferences for a patient"""
    try:
        result = feedback_service.get_interaction_preferences(patient_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    
    except Exception as e:
        logger.error(f"Error retrieving preferences: {e}")
        return jsonify({'error': 'Failed to retrieve preferences'}), 500


@feedback_bp.route('/memory/<patient_id>', methods=['GET'])
@login_required
def get_memory_insights(patient_id):
    """Get agent memory insights for a patient"""
    try:
        result = feedback_service.get_memory_insights(patient_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    
    except Exception as e:
        logger.error(f"Error retrieving memory insights: {e}")
        return jsonify({'error': 'Failed to retrieve memory insights'}), 500


# Memory-based decision making endpoints
@feedback_bp.route('/decision', methods=['POST'])
@login_required
def get_adaptive_decision():
    """
    Get adaptive decision based on patient feedback history
    
    Request JSON:
    {
        "patient_id": "P001",
        "interaction_type": "music_suggestion",
        "available_actions": ["disney_classics", "nature_sounds", "classical"],
        "context": {
            "sleep_stage": "light_sleep",
            "time_of_day": "evening",
            "pain_level": 0.2
        }
    }
    """
    try:
        data = request.get_json()
        
        required_fields = ['patient_id', 'interaction_type', 'available_actions']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        patient_id = data['patient_id']
        interaction_type = data['interaction_type']
        available_actions = data['available_actions']
        context = data.get('context', {})
        
        # Get adaptive decision from memory service
        result = agent_memory_service.generate_adaptive_decision(
            patient_id=patient_id,
            interaction_type=interaction_type,
            available_actions=available_actions,
            current_context=context
        )
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error getting adaptive decision: {e}", exc_info=True)
        return jsonify({'error': 'Failed to generate adaptive decision'}), 500


@feedback_bp.route('/pattern-analysis/<patient_id>', methods=['GET'])
@login_required
def analyze_patterns(patient_id):
    """
    Use AI to analyze patient feedback patterns and identify adaptation opportunities
    """
    try:
        result = agent_memory_service.analyze_feedback_patterns(patient_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logger.error(f"Error analyzing patterns: {e}")
        return jsonify({'error': 'Failed to analyze patterns'}), 500


@feedback_bp.route('/predict/<patient_id>', methods=['POST'])
@login_required
def predict_optimal_action(patient_id):
    """
    Predict optimal action for a given situation
    
    Request JSON:
    {
        "interaction_type": "music_suggestion",
        "situation": "Patient is in light sleep during evening"
    }
    """
    try:
        data = request.get_json()
        
        interaction_type = data.get('interaction_type', 'general')
        situation = data.get('situation', '')
        
        result = agent_memory_service.predict_optimal_action(
            patient_id=patient_id,
            interaction_type=interaction_type,
            situation=situation
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logger.error(f"Error predicting action: {e}")
        return jsonify({'error': 'Failed to predict action'}), 500


@feedback_bp.route('/adaptation-report/<patient_id>', methods=['GET'])
@login_required
def get_adaptation_report(patient_id):
    """
    Get comprehensive report of agent adaptations for this patient
    Includes patterns, improvements, and recommendations
    """
    try:
        result = agent_memory_service.generate_adaptation_report(patient_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logger.error(f"Error generating adaptation report: {e}")
        return jsonify({'error': 'Failed to generate adaptation report'}), 500


@feedback_bp.route('/action-check/<patient_id>', methods=['POST'])
@login_required
def check_action_viability(patient_id):
    """
    Check if an action should be avoided or recommended based on feedback
    
    Request JSON:
    {
        "interaction_type": "music",
        "action": "heavy_metal_music"
    }
    """
    try:
        data = request.get_json()
        
        interaction_type = data.get('interaction_type', '')
        action = data.get('action', '')
        
        should_avoid, avoid_reason = feedback_service.should_avoid_action(
            patient_id, interaction_type, action
        )
        
        should_recommend, rec_reason = feedback_service.should_recommend_action(
            patient_id, interaction_type, action
        )
        
        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'action': action,
            'should_avoid': should_avoid,
            'avoid_reason': avoid_reason,
            'should_recommend': should_recommend,
            'recommend_reason': rec_reason
        }), 200
    
    except Exception as e:
        logger.error(f"Error checking action viability: {e}")
        return jsonify({'error': 'Failed to check action viability'}), 500


@feedback_bp.route('/clear/<patient_id>', methods=['DELETE'])
@login_required
def clear_feedback(patient_id):
    """
    Clear all feedback for a patient (admin function)
    """
    try:
        # Check if user is admin (would need proper role check in production)
        result = feedback_service.clear_patient_feedback(patient_id)
        
        if result['success']:
            logger.warning(f"Cleared all feedback for patient {patient_id}")
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logger.error(f"Error clearing feedback: {e}")
        return jsonify({'error': 'Failed to clear feedback'}), 500


@feedback_bp.route('/status', methods=['GET'])
@login_required
def feedback_system_status():
    """Get feedback system status and capabilities"""
    return jsonify({
        'success': True,
        'feedback_system_active': True,
        'memory_service_available': agent_memory_service.is_available(),
        'ai_provider': 'google-generative-ai' if agent_memory_service.is_available() else 'fallback',
        'features': [
            'feedback_collection',
            'pattern_analysis',
            'adaptive_decisions',
            'preference_learning',
            'memory_based_recommendations'
        ]
    }), 200

