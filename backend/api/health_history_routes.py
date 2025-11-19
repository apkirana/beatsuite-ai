"""
Health History API Routes
Provides endpoints for retrieving patient health history
"""
from flask import Blueprint, jsonify, request
from backend.auth.decorators import login_required
from backend.services import health_history_service

health_history_bp = Blueprint('health_history', __name__, url_prefix='/api/health-history')

@health_history_bp.route('/<patient_id>', methods=['GET'])
@login_required
def get_patient_history(patient_id):
    """Get health history for a patient"""
    try:
        # Get hours parameter (default 24)
        hours = request.args.get('hours', 24, type=int)
        
        # Maximum 168 hours (7 days)
        if hours > 168:
            hours = 168
        
        records = health_history_service.get_patient_history(patient_id, hours)
        
        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'hours': hours,
            'records': records,
            'count': len(records)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@health_history_bp.route('/initialize', methods=['POST'])
@login_required
def initialize_sample_data():
    """Initialize sample health history data (for testing)"""
    try:
        health_history_service.initialize_sample_data()
        return jsonify({
            'success': True,
            'message': 'Sample health history data initialized'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
