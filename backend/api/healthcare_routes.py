"""
Healthcare API Routes
Consolidated endpoints for patient management, health history, and reports
"""
from flask import Blueprint, request, jsonify, session
from backend.auth.decorators import login_required, role_required
from backend.services import patient_service, health_history_service
from backend.database.db import ReportDatabase, NotificationDatabase
from backend.ai.gemini_service import gemini_service
from backend.api.monitoring_routes import load_room_data
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ============== PATIENTS BLUEPRINT ==============
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
        if not query:
            return jsonify({'success': True, 'patients': []}), 200
        
        patients = patient_service.search_patients(query)
        return jsonify({'success': True, 'patients': patients}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@patients_bp.route('', methods=['POST'])
@login_required
@role_required(['admin', 'doctor'])
def create_patient():
    """Create new patient"""
    try:
        data = request.json
        patient = patient_service.create_patient(data)
        return jsonify({'success': True, 'patient': patient}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@patients_bp.route('/<patient_id>', methods=['PUT'])
@login_required
@role_required(['admin', 'doctor'])
def update_patient(patient_id):
    """Update patient information"""
    try:
        data = request.json
        patient = patient_service.update_patient(patient_id, data)
        if patient:
            return jsonify({'success': True, 'patient': patient}), 200
        return jsonify({'success': False, 'error': 'Patient not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@patients_bp.route('/<patient_id>', methods=['DELETE'])
@login_required
@role_required(['admin'])
def delete_patient(patient_id):
    """Delete patient"""
    try:
        success = patient_service.delete_patient(patient_id)
        if success:
            return jsonify({'success': True, 'message': 'Patient deleted'}), 200
        return jsonify({'success': False, 'error': 'Patient not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============== HEALTH HISTORY BLUEPRINT ==============
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


# ============== REPORTS BLUEPRINT ==============
reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@reports_bp.route('/generate/<room_id>', methods=['POST'])
@login_required
def generate_daily_report(room_id):
    """
    Generate AI-powered daily report for a patient
    Automatically saves to database
    """
    try:
        rooms = load_room_data()
        
        if room_id not in rooms:
            return jsonify({'error': 'Room not found'}), 404
        
        room_data = rooms[room_id]
        patient_name = room_data.get('patient_name', 'Patient')
        
        # Get AI analysis
        analysis = gemini_service.analyze_patient_vitals(room_data)
        summary = gemini_service.generate_health_summary(patient_name, room_data)
        
        # Create comprehensive report
        report = {
            'report_id': f"RPT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'report_time': datetime.now().strftime('%H:%M:%S'),
            'room_id': room_id,
            'room_number': room_id.replace('_', ' ').title(),
            'patient_name': patient_name,
            'patient_id': room_data.get('patient_id'),
            
            # Current vitals
            'heart_rate': room_data.get('heart_rate'),
            'blood_pressure': room_data.get('blood_pressure'),
            'oxygen_saturation': room_data.get('oxygen_saturation'),
            'temperature': room_data.get('temperature'),
            'respiratory_rate': room_data.get('respiratory_rate'),
            
            # AI Analysis
            'ai_analysis': analysis,
            'health_summary': summary,
            'status': room_data.get('status'),
            
            # Metadata
            'generated_at': datetime.now().isoformat(),
            'generated_by': 'AI System'
        }
        
        # Save to database
        db = ReportDatabase()
        db.save_report(report)
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/daily/<room_id>', methods=['GET'])
@login_required
def get_daily_reports(room_id):
    """Get all daily reports for a room"""
    try:
        db = ReportDatabase()
        reports = db.get_reports_by_room(room_id)
        
        return jsonify({
            'success': True,
            'room_id': room_id,
            'reports': reports,
            'count': len(reports)
        })
        
    except Exception as e:
        logger.error(f"Error fetching reports: {e}")
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/<report_id>', methods=['GET'])
@login_required
def get_report(report_id):
    """Get specific report by ID"""
    try:
        db = ReportDatabase()
        report = db.get_report_by_id(report_id)
        
        if report:
            return jsonify({
                'success': True,
                'report': report
            })
        else:
            return jsonify({'error': 'Report not found'}), 404
            
    except Exception as e:
        logger.error(f"Error fetching report: {e}")
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/all', methods=['GET'])
@login_required
@role_required(['admin', 'doctor'])
def get_all_reports():
    """Get all reports (admin/doctor only)"""
    try:
        db = ReportDatabase()
        reports = db.get_all_reports()
        
        return jsonify({
            'success': True,
            'reports': reports,
            'count': len(reports)
        })
        
    except Exception as e:
        logger.error(f"Error fetching all reports: {e}")
        return jsonify({'error': str(e)}), 500


# ============== NOTIFICATIONS BLUEPRINT ==============
notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@notifications_bp.route('', methods=['GET'])
@login_required
def get_notifications():
    """Get all notifications"""
    try:
        db = NotificationDatabase()
        notifications = db.get_all_notifications()
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'count': len(notifications)
        })
        
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/<room_id>', methods=['GET'])
@login_required
def get_room_notifications(room_id):
    """Get notifications for specific room"""
    try:
        db = NotificationDatabase()
        notifications = db.get_notifications_by_room(room_id)
        
        return jsonify({
            'success': True,
            'room_id': room_id,
            'notifications': notifications,
            'count': len(notifications)
        })
        
    except Exception as e:
        logger.error(f"Error fetching room notifications: {e}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/unread', methods=['GET'])
@login_required
def get_unread_notifications():
    """Get unread notifications"""
    try:
        db = NotificationDatabase()
        notifications = db.get_unread_notifications()
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'count': len(notifications)
        })
        
    except Exception as e:
        logger.error(f"Error fetching unread notifications: {e}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/<notification_id>/read', methods=['PUT'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        db = NotificationDatabase()
        success = db.mark_as_read(notification_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Notification marked as read'
            })
        else:
            return jsonify({'error': 'Notification not found'}), 404
            
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        return jsonify({'error': str(e)}), 500
