"""
Patient CRUD API Routes
Provides REST API endpoints for patient management
"""
from flask import Blueprint, request, jsonify, session
from backend.auth.decorators import login_required, role_required
from backend.services import patient_service

patients_bp = Blueprint('patients', __name__, url_prefix='/api/patients')

@patients_bp.route('', methods=['GET'])
@login_required
def get_patients():
    """Get all patients"""
    try:
        patients = patient_service.get_all_patients()
        return jsonify({'success': True, 'patients': patients}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@patients_bp.route('/<patient_id>', methods=['GET'])
@login_required
def get_patient(patient_id):
    """Get patient by ID"""
    try:
        patient = patient_service.get_patient_by_id(patient_id)
        if patient:
            return jsonify({'success': True, 'patient': patient}), 200
        return jsonify({'success': False, 'error': 'Patient not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@patients_bp.route('/room/<room_id>', methods=['GET'])
@login_required
def get_patient_by_room(room_id):
    """Get patient by room ID"""
    try:
        patient = patient_service.get_patients_by_room(room_id)
        if patient:
            return jsonify({'success': True, 'patient': patient}), 200
        return jsonify({'success': False, 'error': 'No patient in this room'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@patients_bp.route('/search', methods=['GET'])
@login_required
def search_patients():
    """Search patients by name or ID"""
    try:
        query = request.args.get('q', '')
        patients = patient_service.search_patients(query)
        return jsonify({'success': True, 'patients': patients}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@patients_bp.route('', methods=['POST'])
@role_required(['admin', 'nurse'])
def create_patient():
    """Create new patient"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['patient_name', 'age', 'gender', 'diagnosis']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        patient = patient_service.create_patient(data)
        return jsonify({'success': True, 'patient': patient, 'message': 'Patient created successfully'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@patients_bp.route('/<patient_id>', methods=['PUT'])
@role_required(['admin', 'nurse'])
def update_patient(patient_id):
    """Update existing patient"""
    try:
        data = request.get_json()
        patient = patient_service.update_patient(patient_id, data)
        
        if patient:
            return jsonify({'success': True, 'patient': patient, 'message': 'Patient updated successfully'}), 200
        return jsonify({'success': False, 'error': 'Patient not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@patients_bp.route('/<patient_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_patient(patient_id):
    """Delete patient (soft delete)"""
    try:
        success = patient_service.delete_patient(patient_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Patient deleted successfully'}), 200
        return jsonify({'success': False, 'error': 'Patient not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
