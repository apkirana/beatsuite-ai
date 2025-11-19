"""
Beat Suite AI - Core AI Engine
Processes physiological data from smartwatches and adjusts room environment
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class PatientDataProcessor:
    """Process and analyze patient physiological data"""
    
    def __init__(self):
        # Baseline ranges for healthy vitals
        self.baseline_hr_range = (60, 100)  # BPM
        self.baseline_spo2_range = (95, 100)  # Percentage
        self.movement_threshold = 0.3  # Normalized movement score
        
    def analyze_sleep_stage(self, heart_rate: int, movement: float, time_of_day: int) -> str:
        """
        Determine sleep stage based on vitals
        Returns: 'awake', 'light_sleep', 'deep_sleep', 'rem_sleep'
        """
        if movement > 0.5:
            return 'awake'
        
        # Lower HR + minimal movement = deeper sleep
        hr_ratio = heart_rate / self.baseline_hr_range[1]
        
        if hr_ratio < 0.7 and movement < 0.1:
            return 'deep_sleep'
        elif hr_ratio < 0.8 and movement < 0.2:
            return 'rem_sleep'
        elif movement < 0.3:
            return 'light_sleep'
        else:
            return 'awake'
    
    def detect_pain_indicators(self, heart_rate: int, movement: float, 
                               hr_history: List[int]) -> Tuple[bool, float]:
        """
        Detect potential pain/discomfort
        Returns: (is_pain_detected, severity_score)
        """
        # Sudden HR increase
        if len(hr_history) >= 5:
            avg_hr = np.mean(hr_history[-5:])
            if heart_rate > avg_hr + 15:
                severity = min((heart_rate - avg_hr) / 20.0, 1.0)
                return True, severity
        
        # High HR + increased movement
        if heart_rate > 90 and movement > 0.6:
            return True, 0.7
        
        return False, 0.0
    
    def assess_circadian_phase(self, time_of_day: int) -> str:
        """
        Determine circadian phase (0-23 hours)
        Returns: 'morning', 'afternoon', 'evening', 'night'
        """
        if 6 <= time_of_day < 12:
            return 'morning'
        elif 12 <= time_of_day < 17:
            return 'afternoon'
        elif 17 <= time_of_day < 22:
            return 'evening'
        else:
            return 'night'


class EnvironmentController:
    """Adaptive environmental control based on patient state"""
    
    def __init__(self):
        # Light color temperatures (Kelvin)
        self.color_temps = {
            'blue_enriched': 6500,   # Alerting, morning
            'neutral': 4000,          # Afternoon
            'warm': 3000,            # Evening relaxation
            'amber': 2000,           # Deep sleep, night
            'red': 1800              # Pain relief
        }
        
        # Music playlist mappings
        self.playlists = {
            'energizing': 'upbeat_morning',
            'focus': 'ambient_concentration',
            'relaxing': 'calm_ambient',
            'sleep': 'binaural_sleep',
            'pain_relief': 'healing_frequencies'
        }
    
    def kelvin_to_hex(self, kelvin: int) -> str:
        """Convert color temperature to hex color"""
        # Simplified conversion
        if kelvin >= 6000:
            return '#E0F4FF'  # Cool blue-white
        elif kelvin >= 4500:
            return '#F5F5DC'  # Neutral white
        elif kelvin >= 3000:
            return '#FFD699'  # Warm white
        elif kelvin >= 2000:
            return '#FFAA77'  # Amber
        else:
            return '#FF6B4A'  # Red-amber
    
    def calculate_light_settings(self, sleep_stage: str, circadian_phase: str,
                                  pain_detected: bool, pain_severity: float) -> Dict:
        """
        Determine optimal lighting based on patient state
        Returns: {color_hex, brightness, color_temp}
        """
        # Pain override
        if pain_detected and pain_severity > 0.5:
            return {
                'color_hex': self.kelvin_to_hex(self.color_temps['red']),
                'brightness': 0.2,
                'color_temp': self.color_temps['red'],
                'reason': 'Red light therapy for pain relief'
            }
        
        # Sleep-based adjustments
        if sleep_stage == 'deep_sleep':
            return {
                'color_hex': self.kelvin_to_hex(self.color_temps['amber']),
                'brightness': 0.05,
                'color_temp': self.color_temps['amber'],
                'reason': 'Minimal amber light for deep sleep'
            }
        elif sleep_stage == 'light_sleep' or sleep_stage == 'rem_sleep':
            return {
                'color_hex': self.kelvin_to_hex(self.color_temps['warm']),
                'brightness': 0.15,
                'color_temp': self.color_temps['warm'],
                'reason': 'Warm light supporting sleep maintenance'
            }
        
        # Circadian-aligned lighting for awake state
        if circadian_phase == 'morning':
            return {
                'color_hex': self.kelvin_to_hex(self.color_temps['blue_enriched']),
                'brightness': 0.7,
                'color_temp': self.color_temps['blue_enriched'],
                'reason': 'Blue-enriched light to support morning alertness'
            }
        elif circadian_phase == 'afternoon':
            return {
                'color_hex': self.kelvin_to_hex(self.color_temps['neutral']),
                'brightness': 0.6,
                'color_temp': self.color_temps['neutral'],
                'reason': 'Neutral daylight for afternoon activity'
            }
        elif circadian_phase == 'evening':
            return {
                'color_hex': self.kelvin_to_hex(self.color_temps['warm']),
                'brightness': 0.4,
                'color_temp': self.color_temps['warm'],
                'reason': 'Warm light to promote evening relaxation'
            }
        else:  # night
            return {
                'color_hex': self.kelvin_to_hex(self.color_temps['amber']),
                'brightness': 0.1,
                'color_temp': self.color_temps['amber'],
                'reason': 'Dim amber light for nighttime melatonin production'
            }
    
    def calculate_music_settings(self, sleep_stage: str, pain_detected: bool,
                                  pain_severity: float, circadian_phase: str) -> Dict:
        """
        Determine optimal music based on patient state
        Returns: {playlist_id, volume}
        """
        # Pain override
        if pain_detected and pain_severity > 0.6:
            return {
                'playlist_id': self.playlists['pain_relief'],
                'volume': 0.25,
                'reason': '432Hz healing frequencies for pain management'
            }
        
        # Sleep-based music
        if sleep_stage in ['deep_sleep', 'light_sleep', 'rem_sleep']:
            return {
                'playlist_id': self.playlists['sleep'],
                'volume': 0.15,
                'reason': 'Binaural beats and delta waves for sleep'
            }
        
        # Awake state music
        if circadian_phase == 'morning':
            return {
                'playlist_id': self.playlists['energizing'],
                'volume': 0.3,
                'reason': 'Uplifting music to support morning energy'
            }
        elif circadian_phase in ['afternoon', 'evening']:
            return {
                'playlist_id': self.playlists['relaxing'],
                'volume': 0.2,
                'reason': 'Calming ambient music for relaxation'
            }
        else:
            return {
                'playlist_id': self.playlists['sleep'],
                'volume': 0.1,
                'reason': 'Quiet ambient sounds for nighttime'
            }


class BeatSuiteAI:
    """Main AI engine coordinating patient monitoring and environment control"""
    
    def __init__(self):
        self.data_processor = PatientDataProcessor()
        self.env_controller = EnvironmentController()
        self.patient_histories = {}  # Store HR history per patient
        
        logger.info("Beat Suite AI Engine initialized")
    
    def process_smartwatch_data(self, patient_id: str, smartwatch_data: Dict) -> Dict:
        """
        Main processing loop: analyze patient data and generate environment settings
        
        Args:
            patient_id: Unique patient identifier
            smartwatch_data: {
                'heart_rate': int,
                'movement': float (0-1),
                'spo2': int,
                'timestamp': datetime
            }
        
        Returns:
            environment_settings: {
                'light': {...},
                'music': {...},
                'patient_state': {...},
                'ai_reasoning': str
            }
        """
        # Initialize patient history if needed
        if patient_id not in self.patient_histories:
            self.patient_histories[patient_id] = {
                'heart_rates': [],
                'last_update': None
            }
        
        # Extract data
        hr = smartwatch_data.get('heart_rate', 70)
        movement = smartwatch_data.get('movement', 0.0)
        spo2 = smartwatch_data.get('spo2', 98)
        timestamp = smartwatch_data.get('timestamp', datetime.now())
        
        # Update history
        history = self.patient_histories[patient_id]
        history['heart_rates'].append(hr)
        if len(history['heart_rates']) > 20:  # Keep last 20 readings
            history['heart_rates'] = history['heart_rates'][-20:]
        history['last_update'] = timestamp
        
        # Analyze patient state
        hour = timestamp.hour
        sleep_stage = self.data_processor.analyze_sleep_stage(hr, movement, hour)
        pain_detected, pain_severity = self.data_processor.detect_pain_indicators(
            hr, movement, history['heart_rates']
        )
        circadian_phase = self.data_processor.assess_circadian_phase(hour)
        
        # Calculate optimal environment
        light_settings = self.env_controller.calculate_light_settings(
            sleep_stage, circadian_phase, pain_detected, pain_severity
        )
        music_settings = self.env_controller.calculate_music_settings(
            sleep_stage, pain_detected, pain_severity, circadian_phase
        )
        
        # Generate AI reasoning
        reasoning = self._generate_reasoning(
            sleep_stage, circadian_phase, pain_detected, 
            pain_severity, hr, movement, spo2
        )
        
        return {
            'light': light_settings,
            'music': music_settings,
            'patient_state': {
                'sleep_stage': sleep_stage,
                'circadian_phase': circadian_phase,
                'pain_detected': pain_detected,
                'pain_severity': pain_severity,
                'heart_rate': hr,
                'movement': movement,
                'oxygen_level': spo2
            },
            'ai_reasoning': reasoning,
            'timestamp': timestamp.isoformat()
        }
    
    def _generate_reasoning(self, sleep_stage: str, circadian_phase: str,
                           pain_detected: bool, pain_severity: float,
                           hr: int, movement: float, spo2: int) -> str:
        """Generate human-readable explanation of AI decisions"""
        
        parts = []
        
        # Sleep state
        if sleep_stage == 'deep_sleep':
            parts.append(f"Patient in deep sleep (HR: {hr}, minimal movement)")
        elif sleep_stage in ['light_sleep', 'rem_sleep']:
            parts.append(f"Patient in {sleep_stage.replace('_', ' ')} (HR: {hr})")
        else:
            parts.append(f"Patient awake (HR: {hr}, movement detected)")
        
        # Pain detection
        if pain_detected:
            parts.append(f"Pain/discomfort detected (severity: {pain_severity:.1%})")
            parts.append("Applying red light therapy and healing frequencies")
        
        # Circadian alignment
        parts.append(f"Circadian phase: {circadian_phase}")
        
        if circadian_phase == 'morning':
            parts.append("Blue-enriched light supporting cortisol awakening response")
        elif circadian_phase == 'night':
            parts.append("Amber light promoting melatonin production")
        
        # Vitals status
        if spo2 < 95:
            parts.append(f"Monitoring O2 levels: {spo2}%")
        
        return ". ".join(parts) + "."


# Singleton instance
ai_engine = BeatSuiteAI()


def process_patient_update(patient_id: str, smartwatch_data: Dict) -> Dict:
    """
    Public API for processing patient data updates
    """
    return ai_engine.process_smartwatch_data(patient_id, smartwatch_data)
