"""
CRUD Service for Patients
Handles all database operations for patient data
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/patients.json')

def load_patients() -> List[Dict]:
    """Load all patients from JSON file"""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_patients(patients: List[Dict]) -> None:
    """Save patients to JSON file"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(patients, f, indent=2)

def get_all_patients() -> List[Dict]:
    """Get all active patients"""
    patients = load_patients()
    return [p for p in patients if p.get('is_active', True)]

def get_patient_by_id(patient_id: str) -> Optional[Dict]:
    """Get patient by ID"""
    patients = load_patients()
    for patient in patients:
        if patient['patient_id'] == patient_id and patient.get('is_active', True):
            return patient
    return None

def get_patients_by_room(room_id: str) -> Optional[Dict]:
    """Get patient by room ID"""
    patients = load_patients()
    for patient in patients:
        if patient.get('room_id') == room_id and patient.get('is_active', True):
            return patient
    return None

def create_patient(patient_data: Dict) -> Dict:
    """Create a new patient"""
    patients = load_patients()
    
    # Generate patient ID
    patient_ids = [p['patient_id'] for p in patients]
    max_id = max([int(pid.replace('P', '')) for pid in patient_ids if pid.startswith('P')], default=0)
    patient_data['patient_id'] = f'P{str(max_id + 1).zfill(3)}'
    
    # Add timestamps
    now = datetime.now().isoformat()
    patient_data['created_at'] = now
    patient_data['updated_at'] = now
    patient_data['is_active'] = True
    
    patients.append(patient_data)
    save_patients(patients)
    
    return patient_data

def update_patient(patient_id: str, patient_data: Dict) -> Optional[Dict]:
    """Update existing patient"""
    patients = load_patients()
    
    for i, patient in enumerate(patients):
        if patient['patient_id'] == patient_id:
            patient_data['patient_id'] = patient_id
            patient_data['created_at'] = patient.get('created_at', datetime.now().isoformat())
            patient_data['updated_at'] = datetime.now().isoformat()
            patient_data['is_active'] = patient_data.get('is_active', True)
            
            patients[i] = patient_data
            save_patients(patients)
            return patient_data
    
    return None

def delete_patient(patient_id: str) -> bool:
    """Soft delete patient (set is_active to False)"""
    patients = load_patients()
    
    for patient in patients:
        if patient['patient_id'] == patient_id:
            patient['is_active'] = False
            patient['updated_at'] = datetime.now().isoformat()
            save_patients(patients)
            return True
    
    return False

def search_patients(query: str) -> List[Dict]:
    """Search patients by name or ID"""
    patients = get_all_patients()
    query = query.lower()
    
    return [p for p in patients if 
            query in p['patient_name'].lower() or 
            query in p['patient_id'].lower()]
