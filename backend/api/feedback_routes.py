from flask import Blueprint, request, jsonify
from ..auth.decorators import login_required
from ..services.memory_service import memory_service
import logging

logger = logging.getLogger(__name__)

feedback_bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')

@feedback_bp.route('/submit', methods=['POST'])
@login_required
def submit_feedback():
    """
    Receives user feedback for an AI interaction and stores it in memory.
    """
    try:
        data = request.json
        user_id = request.headers.get('X-User-ID', 'default_user')
        interaction_summary = data.get('interaction_summary')
        feedback = data.get('feedback') # e.g., 'positive', 'negative', or a comment

        if not interaction_summary or not feedback:
            return jsonify({'error': 'Missing required fields: interaction_summary or feedback'}), 400

        memory_service.add_memory(user_id, interaction_summary, feedback)

        logger.info(f"Feedback submitted for user {user_id}: {feedback} on '{interaction_summary}'")
        return jsonify({'message': 'Feedback submitted successfully'}), 200

    except Exception as e:
        logger.error(f"Error submitting feedback: {e}", exc_info=True)
        return jsonify({'error': 'Failed to submit feedback'}), 500

def register_routes(app):
    """Register feedback blueprint"""
    app.register_blueprint(feedback_bp)