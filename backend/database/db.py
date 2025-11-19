"""
Database for storing daily reports and notifications
Using JSON files for simplicity (can be migrated to SQLite/PostgreSQL later)
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
REPORTS_FILE = os.path.join(DATA_DIR, 'daily_reports.json')
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, 'notifications.json')


class ReportDatabase:
    """Manages daily patient reports"""
    
    @staticmethod
    def save_daily_report(report: Dict) -> bool:
        """Save a daily report"""
        try:
            # Load existing reports
            reports = ReportDatabase.load_all_reports()
            
            # Add new report with timestamp
            report['saved_at'] = datetime.now().isoformat()
            reports.append(report)
            
            # Save back
            with open(REPORTS_FILE, 'w') as f:
                json.dump(reports, f, indent=2)
            
            logger.info(f"Saved daily report for {report.get('patient_name')} - {report.get('room_id')}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            return False
    
    @staticmethod
    def load_all_reports() -> List[Dict]:
        """Load all reports"""
        try:
            if os.path.exists(REPORTS_FILE):
                with open(REPORTS_FILE, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading reports: {e}")
            return []
    
    @staticmethod
    def get_reports_by_room(room_id: str, limit: int = 10) -> List[Dict]:
        """Get recent reports for a specific room"""
        all_reports = ReportDatabase.load_all_reports()
        room_reports = [r for r in all_reports if r.get('room_id') == room_id]
        return sorted(room_reports, key=lambda x: x.get('saved_at', ''), reverse=True)[:limit]
    
    @staticmethod
    def get_reports_by_date(date: str) -> List[Dict]:
        """Get all reports for a specific date (YYYY-MM-DD)"""
        all_reports = ReportDatabase.load_all_reports()
        return [r for r in all_reports if r.get('report_date', '').startswith(date)]


class NotificationDatabase:
    """Manages critical patient notifications"""
    
    @staticmethod
    def create_notification(notification: Dict) -> bool:
        """Create a new notification"""
        try:
            notifications = NotificationDatabase.load_all_notifications()
            
            # Add metadata
            notification['id'] = f"notif_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            notification['created_at'] = datetime.now().isoformat()
            notification['read'] = False
            
            notifications.append(notification)
            
            # Save
            with open(NOTIFICATIONS_FILE, 'w') as f:
                json.dump(notifications, f, indent=2)
            
            logger.warning(f"CRITICAL NOTIFICATION: {notification.get('message')}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return False
    
    @staticmethod
    def load_all_notifications() -> List[Dict]:
        """Load all notifications"""
        try:
            if os.path.exists(NOTIFICATIONS_FILE):
                with open(NOTIFICATIONS_FILE, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading notifications: {e}")
            return []
    
    @staticmethod
    def get_unread_notifications(role: str = None) -> List[Dict]:
        """Get unread notifications, optionally filtered by role"""
        all_notifs = NotificationDatabase.load_all_notifications()
        unread = [n for n in all_notifs if not n.get('read', False)]
        
        if role:
            unread = [n for n in unread if role in n.get('target_roles', ['admin', 'nurse'])]
        
        return sorted(unread, key=lambda x: x.get('created_at', ''), reverse=True)
    
    @staticmethod
    def mark_as_read(notification_id: str) -> bool:
        """Mark a notification as read"""
        try:
            notifications = NotificationDatabase.load_all_notifications()
            
            for notif in notifications:
                if notif.get('id') == notification_id:
                    notif['read'] = True
                    notif['read_at'] = datetime.now().isoformat()
            
            with open(NOTIFICATIONS_FILE, 'w') as f:
                json.dump(notifications, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False
    
    @staticmethod
    def clear_old_notifications(days: int = 7) -> int:
        """Clear notifications older than specified days"""
        try:
            notifications = NotificationDatabase.load_all_notifications()
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            filtered = []
            removed = 0
            
            for notif in notifications:
                created = datetime.fromisoformat(notif.get('created_at', datetime.now().isoformat()))
                if created.timestamp() > cutoff_date:
                    filtered.append(notif)
                else:
                    removed += 1
            
            if removed > 0:
                with open(NOTIFICATIONS_FILE, 'w') as f:
                    json.dump(filtered, f, indent=2)
                logger.info(f"Cleared {removed} old notifications")
            
            return removed
        except Exception as e:
            logger.error(f"Error clearing old notifications: {e}")
            return 0


# Initialize database files if they don't exist
def initialize_database():
    """Create database files if they don't exist"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, 'w') as f:
            json.dump([], f)
        logger.info("Created daily_reports.json")
    
    if not os.path.exists(NOTIFICATIONS_FILE):
        with open(NOTIFICATIONS_FILE, 'w') as f:
            json.dump([], f)
        logger.info("Created notifications.json")


# Initialize on import
initialize_database()
