"""
Reports and Notifications API routes
"""

from flask import Blueprint, request, jsonify
from backend.auth.decorators import login_required, role_required
from backend.database.db import ReportDatabase, NotificationDatabase
from backend.ai.gemini_service import gemini_service
from backend.api.room_routes import load_room_data
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')
notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')


# ============== REPORTS ENDPOINTS ==============

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
            
            # Vital Signs
            'vitals': {
                'heart_rate': room_data.get('heart_rate', 70),
                'temperature': room_data.get('temperature', 98.6),
                'respiratory_rate': room_data.get('respiratory_rate', 16),
                'spo2': room_data.get('oxygen_level', 98),
                'blood_pressure': room_data.get('blood_pressure', '120/80')
            },
            
            # Patient State
            'state': {
                'sleep_stage': room_data.get('sleep_stage', 'AWAKE'),
                'pain_detected': room_data.get('pain_detected', False),
                'movement_level': room_data.get('movement_level', 'low')
            },
            
            # Environment Settings
            'environment': room_data.get('current_ai_settings', {}),
            
            # AI Analysis
            'ai_analysis': analysis.get('analysis', {}),
            'ai_summary': summary,
            
            # Metadata
            'generated_by': request.current_user.get('username'),
            'ai_was_active': room_data.get('ai_is_active', False)
        }
        
        # Save to database
        success = ReportDatabase.save_daily_report(report)
        
        if success:
            # Check if patient is critical and create notification
            risk_level = analysis.get('analysis', {}).get('risk_level', 'Low')
            if risk_level in ['High', 'Critical']:
                NotificationDatabase.create_notification({
                    'type': 'critical_patient',
                    'severity': 'high',
                    'room_id': room_id,
                    'patient_name': patient_name,
                    'message': f"⚠️ CRITICAL: {patient_name} in {room_id.replace('_', ' ').title()} requires immediate attention!",
                    'risk_level': risk_level,
                    'target_roles': ['admin', 'nurse']
                })
            
            return jsonify({
                'success': True,
                'message': 'Daily report generated and saved',
                'report': report
            }), 200
        else:
            return jsonify({'error': 'Failed to save report'}), 500
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/room/<room_id>', methods=['GET'])
@login_required
def get_room_reports(room_id):
    """Get recent reports for a specific room"""
    try:
        limit = request.args.get('limit', 10, type=int)
        reports = ReportDatabase.get_reports_by_room(room_id, limit)
        
        return jsonify({
            'success': True,
            'room_id': room_id,
            'count': len(reports),
            'reports': reports
        })
    except Exception as e:
        logger.error(f"Error fetching reports: {e}")
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/date/<date>', methods=['GET'])
@login_required
def get_reports_by_date(date):
    """Get all reports for a specific date (YYYY-MM-DD)"""
    try:
        reports = ReportDatabase.get_reports_by_date(date)
        
        return jsonify({
            'success': True,
            'date': date,
            'count': len(reports),
            'reports': reports
        })
    except Exception as e:
        logger.error(f"Error fetching reports by date: {e}")
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/all', methods=['GET'])
@role_required(['admin', 'nurse'])
def get_all_reports():
    """Get all reports (admin/nurse only)"""
    try:
        limit = request.args.get('limit', 50, type=int)
        all_reports = ReportDatabase.load_all_reports()
        
        # Sort by date descending
        sorted_reports = sorted(all_reports, key=lambda x: x.get('saved_at', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'count': len(sorted_reports[:limit]),
            'reports': sorted_reports[:limit]
        })
    except Exception as e:
        logger.error(f"Error fetching all reports: {e}")
        return jsonify({'error': str(e)}), 500


# ============== NOTIFICATIONS ENDPOINTS ==============

@notifications_bp.route('/unread', methods=['GET'])
@login_required
def get_unread_notifications():
    """Get unread notifications for current user"""
    try:
        user_role = request.current_user.get('role')
        notifications = NotificationDatabase.get_unread_notifications(user_role)
        
        return jsonify({
            'success': True,
            'count': len(notifications),
            'notifications': notifications
        })
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/<notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        success = NotificationDatabase.mark_as_read(notification_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Notification marked as read'
            })
        else:
            return jsonify({'error': 'Failed to mark as read'}), 500
            
    except Exception as e:
        logger.error(f"Error marking notification: {e}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/check-critical', methods=['POST'])
@login_required
def check_critical_patients():
    """
    Check all patients and create notifications for critical ones
    Can be called periodically or manually
    """
    try:
        rooms = load_room_data()
        notifications_created = 0
        
        for room_id, room_data in rooms.items():
            # Analyze patient
            analysis = gemini_service.analyze_patient_vitals(room_data)
            risk_level = analysis.get('analysis', {}).get('risk_level', 'Low')
            
            if risk_level in ['High', 'Critical']:
                NotificationDatabase.create_notification({
                    'type': 'critical_patient',
                    'severity': 'high',
                    'room_id': room_id,
                    'patient_name': room_data.get('patient_name'),
                    'message': f"⚠️ CRITICAL: {room_data.get('patient_name')} in {room_id.replace('_', ' ').title()} - Risk Level: {risk_level}",
                    'risk_level': risk_level,
                    'concerns': analysis.get('analysis', {}).get('concerns', []),
                    'target_roles': ['admin', 'nurse']
                })
                notifications_created += 1
        
        return jsonify({
            'success': True,
            'notifications_created': notifications_created,
            'message': f'Created {notifications_created} critical notifications'
        })
        
    except Exception as e:
        logger.error(f"Error checking critical patients: {e}")
        return jsonify({'error': str(e)}), 500
