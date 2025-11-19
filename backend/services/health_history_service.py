"""
Health History Service
Tracks and stores patient vital signs history for graphing
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

HISTORY_FILE = os.path.join(os.path.dirname(__file__), '../data/health_history.json')

def load_health_history() -> Dict:
    """Load health history from JSON file"""
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_health_history(history: Dict) -> None:
    """Save health history to JSON file"""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def add_health_record(patient_id: str, vitals: Dict) -> None:
    """
    Add a health record for a patient
    Only saves if last record is > 1 minute old
    """
    history = load_health_history()
    
    if patient_id not in history:
        history[patient_id] = []
    
    now = datetime.now()
    current_time = now.isoformat()
    
    # Check if we should add a new record (every minute)
    patient_records = history[patient_id]
    should_add = True
    
    if patient_records:
        last_record = patient_records[-1]
        last_time = datetime.fromisoformat(last_record['timestamp'])
        time_diff = (now - last_time).total_seconds()  # seconds
        
        # Only add if last record was more than 1 minute ago (60 seconds)
        if time_diff < 60:
            should_add = False
    
    if should_add:
        record = {
            'timestamp': current_time,
            'temperature': vitals.get('temperature'),
            'heart_rate': vitals.get('heart_rate'),
            'spo2': vitals.get('spo2'),
            'respiratory_rate': vitals.get('respiratory_rate')
        }
        
        history[patient_id].append(record)
        
        # Keep only last 7 days (7 days * 24 hours * 60 minutes = 10,080 records max)
        max_records = 10080  # 7 days of minute-by-minute data
        if len(history[patient_id]) > max_records:
            history[patient_id] = history[patient_id][-max_records:]
        
        save_health_history(history)

def get_patient_history(patient_id: str, hours: int = 24) -> List[Dict]:
    """
    Get health history for a patient
    
    Args:
        patient_id: Patient identifier
        hours: Number of hours to retrieve (default 24)
    
    Returns:
        List of health records
    """
    history = load_health_history()
    
    if patient_id not in history:
        return []
    
    records = history[patient_id]
    
    if not records:
        return []
    
    # Filter by time range
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    filtered_records = [
        record for record in records
        if datetime.fromisoformat(record['timestamp']) >= cutoff_time
    ]
    
    return filtered_records

def initialize_sample_data():
    """Initialize sample health history data for testing (minute-by-minute for last 2 hours)"""
    from random import uniform, randint
    
    history = load_health_history()
    
    patients = ['P001', 'P002', 'P003', 'P004']
    
    for patient_id in patients:
        if patient_id not in history or len(history[patient_id]) < 10:
            history[patient_id] = []
            
            # Generate last 2 hours of data (every minute = 120 records)
            now = datetime.now()
            for i in range(120, 0, -1):
                timestamp = (now - timedelta(minutes=i)).isoformat()
                
                # Generate realistic vital signs with slight variations
                base_temp = 98.0 + uniform(-0.5, 0.5)
                base_hr = 75 + randint(-10, 10)
                base_spo2 = 97 + randint(0, 2)
                
                record = {
                    'timestamp': timestamp,
                    'temperature': round(base_temp, 1),
                    'heart_rate': base_hr,
                    'spo2': base_spo2,
                    'respiratory_rate': 16 + randint(-2, 2)
                }
                
                history[patient_id].append(record)
    
    save_health_history(history)
