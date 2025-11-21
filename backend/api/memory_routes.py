from flask import Blueprint, jsonify
from ..auth.decorators import role_required
from ..services.memory_service import memory_service
import logging

logger = logging.getLogger(__name__)

memory_bp = Blueprint('memory', __name__, url_prefix='/api/memory')

@memory_bp.route('/all', methods=['GET'])
@role_required(['admin'])
def get_all_memories():
    """
    Retrieves all memories for all users.
    """
    try:
        memories = memory_service.get_all_memories()
        return jsonify(memories), 200
    except Exception as e:
        logger.error(f"Error getting all memories: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve memories'}), 500

def register_routes(app):
    """Register memory blueprint"""
    app.register_blueprint(memory_bp)