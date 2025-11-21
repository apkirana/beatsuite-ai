# 🧪 Synthetic Data Rules - Beat Suite AI

**Complete guide to synthetic data generation and testing rules for healthcare scenarios**

Version 2.1 | November 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Patient Scenarios](#patient-scenarios)
3. [Vital Signs Rules](#vital-signs-rules)
4. [AI Response Rules](#ai-response-rules)
5. [Environment Control Logic](#environment-control-logic)
6. [Time-Based Rules](#time-based-rules)
7. [Testing Scenarios](#testing-scenarios)
8. [Batch Simulation](#batch-simulation)
9. [Edge Cases](#edge-cases)
10. [Validation Rules](#validation-rules)

---

## 🎯 Overview

The synthetic data system generates realistic patient scenarios for testing AI responses, environment control, and system behavior. All rules are based on medical guidelines and real-world healthcare patterns.

### Core Principles

1. **Medical Accuracy** - All synthetic data follows clinical guidelines
2. **Realistic Variability** - Natural fluctuations in vital signs
3. **Scenario Consistency** - Each scenario has logical vital sign patterns
4. **AI Training** - Data helps train and validate AI responses
5. **Edge Case Testing** - Includes rare but important medical situations

---

## 👤 Patient Scenarios

### 1. Normal/Healthy State

**Characteristics:**
- Stable vital signs within normal ranges
- Low movement indicating rest
- Good oxygen saturation
- Normal temperature

```json
{
  "scenario": "normal",
  "patient_state": "awake and comfortable",
  "vitals": {
    "heart_rate": "65-80 BPM",
    "spo2": "97-100%",
    "movement": "0.3-0.5",
    "temperature": "97.8-98.6°F",
    "respiratory_rate": "12-18 breaths/min",
    "blood_pressure": "110-130/70-85 mmHg"
  },
  "expected_ai_response": {
    "light_brightness": "40-60%",
    "music_volume": "20-40%",
    "reasoning": "Maintaining comfortable environment"
  }
}
```

**Generation Rules:**
```python
heart_rate = random.randint(65, 80)
spo2 = random.randint(97, 100)
movement = round(random.uniform(0.3, 0.5), 2)
temperature = round(random.uniform(97.8, 98.6), 1)
respiratory_rate = random.randint(12, 18)
blood_pressure_systolic = random.randint(110, 130)
blood_pressure_diastolic = random.randint(70, 85)
```

### 2. Sleeping State

**Characteristics:**
- Lower heart rate and respiratory rate
- Minimal movement
- Excellent oxygen saturation
- Slightly lower temperature

```json
{
  "scenario": "sleeping",
  "patient_state": "deep sleep",
  "vitals": {
    "heart_rate": "50-65 BPM",
    "spo2": "96-99%",
    "movement": "0.0-0.2",
    "temperature": "97.0-98.2°F",
    "respiratory_rate": "12-16 breaths/min",
    "blood_pressure": "100-120/60-75 mmHg"
  },
  "expected_ai_response": {
    "light_brightness": "0-10%",
    "music_volume": "10-20%",
    "music_type": "nature_sounds",
    "reasoning": "Supporting deep sleep phase"
  }
}
```

**Generation Rules:**
```python
heart_rate = random.randint(50, 65)
spo2 = random.randint(96, 99)
movement = round(random.uniform(0.0, 0.2), 2)
temperature = round(random.uniform(97.0, 98.2), 1)
respiratory_rate = random.randint(12, 16)
blood_pressure_systolic = random.randint(100, 120)
blood_pressure_diastolic = random.randint(60, 75)
```

### 3. Pain/Distress State

**Characteristics:**
- Elevated heart rate and blood pressure
- Increased movement and restlessness
- Higher temperature from stress response
- Faster respiratory rate

```json
{
  "scenario": "pain",
  "patient_state": "distressed - possible pain",
  "vitals": {
    "heart_rate": "95-120 BPM",
    "spo2": "94-97%",
    "movement": "0.6-0.9",
    "temperature": "98.5-99.8°F",
    "respiratory_rate": "18-24 breaths/min",
    "blood_pressure": "130-150/85-95 mmHg"
  },
  "expected_ai_response": {
    "light_brightness": "15-25%",
    "light_color": "red",
    "music_volume": "25-35%",
    "music_type": "healing_frequencies",
    "reasoning": "Pain detected - activating red light therapy"
  }
}
```

**Generation Rules:**
```python
heart_rate = random.randint(95, 120)
spo2 = random.randint(94, 97)
movement = round(random.uniform(0.6, 0.9), 2)
temperature = round(random.uniform(98.5, 99.8), 1)
respiratory_rate = random.randint(18, 24)
blood_pressure_systolic = random.randint(130, 150)
blood_pressure_diastolic = random.randint(85, 95)
```

### 4. Morning Wake-Up State

**Characteristics:**
- Gradually increasing heart rate
- Moderate movement as patient awakens
- Normal temperature and oxygen levels
- Natural circadian rhythm awakening

```json
{
  "scenario": "morning_wake",
  "patient_state": "waking up",
  "vitals": {
    "heart_rate": "70-85 BPM",
    "spo2": "97-100%",
    "movement": "0.4-0.7",
    "temperature": "97.8-98.6°F",
    "respiratory_rate": "15-19 breaths/min",
    "blood_pressure": "115-135/72-88 mmHg"
  },
  "expected_ai_response": {
    "light_brightness": "60-80%",
    "light_color": "cool",
    "music_volume": "30-50%",
    "music_type": "energizing",
    "reasoning": "Supporting natural morning awakening"
  }
}
```

### 5. Evening Rest State

**Characteristics:**
- Settling heart rate preparing for sleep
- Decreasing movement
- Stable vital signs
- Pre-sleep physiological changes

```json
{
  "scenario": "evening_rest",
  "patient_state": "relaxing for sleep",
  "vitals": {
    "heart_rate": "60-75 BPM",
    "spo2": "96-99%",
    "movement": "0.1-0.3",
    "temperature": "97.5-98.4°F",
    "respiratory_rate": "13-17 breaths/min",
    "blood_pressure": "105-125/65-80 mmHg"
  },
  "expected_ai_response": {
    "light_brightness": "20-40%",
    "light_color": "warm",
    "music_volume": "15-25%",
    "music_type": "relaxing",
    "reasoning": "Preparing environment for sleep"
  }
}
```

---

## 📊 Vital Signs Rules

### Heart Rate Classification

```json
{
  "heart_rate_zones": {
    "bradycardia": "<50 BPM",
    "resting_low": "50-60 BPM", 
    "normal_rest": "60-80 BPM",
    "elevated": "80-100 BPM",
    "tachycardia": ">100 BPM",
    "critical": ">120 BPM"
  },
  "context_modifiers": {
    "sleep": "-10 to -20 BPM",
    "pain": "+15 to +40 BPM",
    "fever": "+8 to +10 BPM per degree",
    "medication": "variable effect",
    "age_factor": "max_hr = 220 - age"
  }
}
```

### SpO2 (Oxygen Saturation) Rules

```json
{
  "spo2_levels": {
    "excellent": "98-100%",
    "good": "95-97%",
    "concerning": "90-94%",
    "critical": "<90%"
  },
  "scenario_modifiers": {
    "normal": "97-100%",
    "sleeping": "96-99%",
    "pain_stress": "94-97%",
    "respiratory_issue": "90-94%"
  }
}
```

### Temperature Rules

```json
{
  "temperature_ranges": {
    "hypothermic": "<95°F",
    "low_normal": "95-97°F",
    "normal": "97-99°F",
    "mild_fever": "99-101°F",
    "moderate_fever": "101-103°F",
    "high_fever": ">103°F"
  },
  "circadian_variation": {
    "morning_low": "97.0-97.8°F",
    "afternoon_peak": "98.6-99.2°F",
    "evening_decline": "97.8-98.4°F"
  }
}
```

### Movement Level Rules

```json
{
  "movement_scale": {
    "motionless": "0.0-0.1",
    "very_still": "0.1-0.2",
    "sleeping": "0.0-0.2",
    "resting": "0.2-0.4",
    "comfortable": "0.3-0.5",
    "restless": "0.5-0.7",
    "agitated": "0.7-0.9",
    "highly_active": "0.9-1.0"
  }
}
```

---

## 🤖 AI Response Rules

### Adaptive Rule Engine

The adaptive rule engine uses conditional logic to provide sophisticated, context-aware responses based on multiple patient parameters, time of day, and clinical evidence.

```json
{
  "adaptive_rules": [
    {
      "condition": "heart_rate > 100 AND movement > 0.6",
      "scenario": "possible_pain",
      "ai_response": {
        "light_brightness": "15-25%",
        "light_color": "red",
        "music_volume": "25-35%",
        "music_type": "healing_frequencies",
        "music_playlist": "432hz_healing",
        "reasoning": "Elevated HR and movement detected; activating pain-reducing stimuli per clinical trial evidence"
      }
    },
    {
      "condition": "heart_rate < 65 AND movement < 0.2 AND time BETWEEN 22:00 AND 06:00",
      "scenario": "deep_sleep",
      "ai_response": {
        "light_brightness": "0-10%",
        "light_color": "warm",
        "music_volume": "5-15%",
        "music_type": "nature_sounds",
        "music_playlist": "rain_sounds",
        "reasoning": "Detected deep sleep pattern; maintaining sleep-supportive lighting and minimal acoustic environment"
      }
    },
    {
      "condition": "time BETWEEN 06:00 AND 08:30 AND heart_rate BETWEEN 65 AND 85 AND movement > 0.4",
      "scenario": "circadian_morning_activation",
      "ai_response": {
        "light_brightness": "60-80%",
        "light_color": "cool",
        "music_volume": "30-50%",
        "music_type": "energizing",
        "music_playlist": "morning_classical",
        "reasoning": "Circadian phase cue; stimulating alertness per chronotherapy research"
      }
    },
    {
      "condition": "spo2 < 92",
      "scenario": "respiratory_distress",
      "ai_response": {
        "emergency_mode": true,
        "light_brightness": "100%",
        "light_color": "white",
        "music_volume": "0%",
        "notification": "critical_staff_alert",
        "reasoning": "Critical oxygen saturation; alerting staff and silencing environment"
      }
    },
    {
      "condition": "movement < 0.1 AND heart_rate BETWEEN 60 AND 75 AND time BETWEEN 20:00 AND 22:00",
      "scenario": "evening_settle",
      "ai_response": {
        "light_brightness": "20-40%",
        "light_color": "warm",
        "music_volume": "15-25%",
        "music_type": "relaxing",
        "music_playlist": "calm_piano",
        "reasoning": "Settling period detected; preparing environment for sleep onset"
      }
    },
    {
      "condition": "movement SPIKE DETECTED DURING sleep_phase",
      "scenario": "sleep_disturbance",
      "ai_response": {
        "light_brightness": "5-15%",
        "light_color": "warm",
        "music_volume": "15-20%",
        "music_type": "soothing",
        "music_playlist": "gentle_lullaby",
        "reasoning": "Disturbance detected during sleep; gentle modulation to resettle patient"
      }
    }
  ]
}
```

### Rule Processing Logic

```python
def evaluate_adaptive_rules(patient_data, current_time):
    """
    Evaluate adaptive rules and return appropriate AI response
    
    Args:
        patient_data (dict): Current patient vitals and status
        current_time (datetime): Current timestamp for time-based rules
    
    Returns:
        dict: AI response configuration or None if no rules match
    """
    
    rules = load_adaptive_rules()
    
    for rule in rules['adaptive_rules']:
        if evaluate_condition(rule['condition'], patient_data, current_time):
            return {
                'scenario': rule['scenario'],
                'response': rule['ai_response'],
                'rule_matched': rule['condition']
            }
    
    return None  # No rules matched, use default behavior

def evaluate_condition(condition_string, data, current_time):
    """
    Parse and evaluate rule conditions
    
    Supported operators:
    - Comparisons: >, <, >=, <=, ==, !=
    - Logic: AND, OR, NOT
    - Time: BETWEEN (for time ranges)
    - Patterns: SPIKE DETECTED, DURING
    """
    
    # Replace variables with actual values
    condition = condition_string
    condition = condition.replace('heart_rate', str(data.get('heart_rate', 0)))
    condition = condition.replace('movement', str(data.get('movement', 0)))
    condition = condition.replace('spo2', str(data.get('spo2', 100)))
    
    # Handle time-based conditions
    if 'time BETWEEN' in condition:
        return evaluate_time_condition(condition, current_time)
    
    # Handle pattern detection
    if 'SPIKE DETECTED' in condition:
        return detect_movement_spike(data)
    
    # Evaluate standard boolean expression
    return eval_safe_condition(condition)
```

### Priority System

Rules are evaluated in priority order to handle overlapping conditions:

```json
{
  "rule_priorities": {
    "emergency": {
      "priority": 1,
      "conditions": ["spo2 < 92", "heart_rate > 130", "temperature > 102"],
      "override_other_rules": true
    },
    "critical_care": {
      "priority": 2, 
      "conditions": ["possible_pain", "respiratory_distress"],
      "can_be_overridden": false
    },
    "sleep_optimization": {
      "priority": 3,
      "conditions": ["deep_sleep", "sleep_disturbance"],
      "can_be_overridden": true
    },
    "circadian_support": {
      "priority": 4,
      "conditions": ["morning_activation", "evening_settle"],
      "can_be_overridden": true
    },
    "comfort_optimization": {
      "priority": 5,
      "conditions": ["normal_awake", "general_comfort"],
      "can_be_overridden": true
    }
  }
}
```

### Lighting Response Logic

```json
{
  "lighting_rules": {
    "deep_sleep": {
      "brightness": "0-10%",
      "color": "warm",
      "hex": "#FF9966",
      "temp": "2000K"
    },
    "light_sleep": {
      "brightness": "10-20%",
      "color": "warm", 
      "hex": "#FFE4B5",
      "temp": "2500K"
    },
    "awake_comfortable": {
      "brightness": "40-60%",
      "color": "neutral",
      "hex": "#FFFFFF",
      "temp": "4000K"
    },
    "pain_detected": {
      "brightness": "15-25%",
      "color": "red",
      "hex": "#FF6B35",
      "temp": "1800K"
    },
    "morning_wake": {
      "brightness": "60-80%",
      "color": "cool",
      "hex": "#CCE6FF",
      "temp": "6000K"
    }
  }
}
```

### Music Response Logic

```json
{
  "music_rules": {
    "deep_sleep": {
      "volume": "5-15%",
      "type": "nature_sounds",
      "playlist": "rain_sounds"
    },
    "light_sleep": {
      "volume": "10-20%",
      "type": "ambient",
      "playlist": "calm_ambient"
    },
    "pain_relief": {
      "volume": "25-35%",
      "type": "healing_frequencies",
      "playlist": "432hz_healing"
    },
    "relaxation": {
      "volume": "20-30%",
      "type": "relaxing",
      "playlist": "calm_piano"
    },
    "energizing": {
      "volume": "30-50%",
      "type": "classical",
      "playlist": "morning_classical"
    }
  }
}
```

### Implementation Example

Here's how to integrate adaptive rules into your existing AI system:

#### 1. Create Adaptive Rules Configuration File

Create `/backend/config/adaptive_rules.json`:

```json
{
  "adaptive_rules": [
    {
      "id": "pain_detection",
      "condition": "heart_rate > 100 AND movement > 0.6",
      "scenario": "possible_pain",
      "priority": 2,
      "ai_response": {
        "light_brightness": "15-25%",
        "light_color": "red",
        "music_volume": "25-35%",
        "music_type": "healing_frequencies",
        "music_playlist": "432hz_healing",
        "reasoning": "Elevated HR and movement detected; activating pain-reducing stimuli per clinical trial evidence"
      }
    },
    {
      "id": "deep_sleep_optimization",
      "condition": "heart_rate < 65 AND movement < 0.2 AND time BETWEEN 22:00 AND 06:00",
      "scenario": "deep_sleep",
      "priority": 3,
      "ai_response": {
        "light_brightness": "0-10%",
        "light_color": "warm",
        "music_volume": "5-15%",
        "music_type": "nature_sounds",
        "music_playlist": "rain_sounds",
        "reasoning": "Detected deep sleep pattern; maintaining sleep-supportive lighting and minimal acoustic environment"
      }
    }
  ]
}
```

#### 2. Update Gemini Service with Adaptive Rules

Add to `/backend/ai/gemini_service.py`:

```python
import json
import os
from datetime import datetime, time

class GeminiService:
    def __init__(self):
        self.adaptive_rules = self.load_adaptive_rules()
    
    def load_adaptive_rules(self):
        """Load adaptive rules from configuration file"""
        rules_path = os.path.join(os.path.dirname(__file__), '../config/adaptive_rules.json')
        try:
            with open(rules_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Adaptive rules file not found, using fallback rules")
            return {"adaptive_rules": []}
    
    def optimize_environment_adaptive(self, patient_data: Dict, current_environment: Dict) -> Dict:
        """Enhanced environment optimization using adaptive rules"""
        try:
            current_time = datetime.now().time()
            
            # First, check adaptive rules
            matched_rule = self.evaluate_adaptive_rules(patient_data, current_time)
            
            if matched_rule:
                logger.info(f"Adaptive rule matched: {matched_rule['scenario']}")
                return {
                    'success': True,
                    'recommendations': matched_rule['response'],
                    'ai_provider': 'gemini-adaptive-rules',
                    'rule_matched': matched_rule['scenario'],
                    'reasoning': matched_rule['response'].get('reasoning', 'Adaptive rule applied')
                }
            
            # Fall back to Gemini AI if no rules match
            return self.optimize_environment(patient_data, current_environment)
            
        except Exception as e:
            logger.error(f"Error in adaptive optimization: {e}")
            return self.optimize_environment(patient_data, current_environment)
    
    def evaluate_adaptive_rules(self, patient_data: Dict, current_time: time) -> Dict:
        """Evaluate adaptive rules and return matching rule"""
        
        # Sort rules by priority (lower number = higher priority)
        sorted_rules = sorted(
            self.adaptive_rules['adaptive_rules'], 
            key=lambda x: x.get('priority', 5)
        )
        
        for rule in sorted_rules:
            if self.evaluate_condition(rule['condition'], patient_data, current_time):
                return {
                    'scenario': rule['scenario'],
                    'response': rule['ai_response'],
                    'rule_id': rule.get('id', 'unknown')
                }
        
        return None
    
    def evaluate_condition(self, condition_string: str, data: Dict, current_time: time) -> bool:
        """Safely evaluate rule conditions"""
        try:
            # Extract values
            heart_rate = data.get('heart_rate', 0)
            movement = data.get('movement', 0)
            spo2 = data.get('spo2', 100)
            temperature = data.get('temperature', 98.6)
            
            # Handle time-based conditions
            if 'time BETWEEN' in condition_string:
                return self.evaluate_time_condition(condition_string, current_time)
            
            # Handle pattern detection
            if 'SPIKE DETECTED' in condition_string:
                return self.detect_movement_spike(data)
            
            # Replace variables with values
            condition = condition_string
            condition = condition.replace('heart_rate', str(heart_rate))
            condition = condition.replace('movement', str(movement))
            condition = condition.replace('spo2', str(spo2))
            condition = condition.replace('temperature', str(temperature))
            condition = condition.replace('AND', ' and ')
            condition = condition.replace('OR', ' or ')
            
            # Safely evaluate the condition
            return eval(condition)
            
        except Exception as e:
            logger.warning(f"Error evaluating condition '{condition_string}': {e}")
            return False
```

#### 3. Update API Routes to Use Adaptive Rules

Modify `/backend/api/ai_routes.py`:

```python
@ai_bp.route('/optimize-adaptive/<room_id>', methods=['POST'])
@role_required(['admin', 'nurse'])
def optimize_environment_adaptive(room_id):
    """Get AI recommendations using adaptive rules"""
    try:
        rooms = load_room_data()
        
        if room_id not in rooms:
            return jsonify({'error': 'Room not found'}), 404
        
        room_data = rooms[room_id]
        current_env = room_data.get('current_ai_settings', {})
        
        # Use adaptive optimization
        optimization = gemini_service.optimize_environment_adaptive(room_data, current_env)
        
        return jsonify({
            'success': True,
            'room_id': room_id,
            'optimization': optimization,
            'adaptive_rules': True
        })
        
    except Exception as e:
        logger.error(f"Error in adaptive environment optimization: {e}")
        return jsonify({'error': 'Adaptive optimization failed'}), 500
```

---

## 🕒 Time-Based Rules

### Circadian Rhythm Adjustments

```json
{
  "time_based_modifiers": {
    "night_hours": {
      "time_range": "22:00-06:00",
      "light_max": "20%",
      "volume_max": "25%",
      "color_preference": "warm",
      "sleep_promotion": true
    },
    "morning_hours": {
      "time_range": "06:00-10:00", 
      "light_preference": "cool",
      "volume_range": "30-60%",
      "energy_support": true
    },
    "afternoon_hours": {
      "time_range": "10:00-18:00",
      "light_preference": "neutral",
      "volume_range": "40-70%",
      "activity_support": true
    },
    "evening_hours": {
      "time_range": "18:00-22:00",
      "light_preference": "warm",
      "volume_range": "25-50%",
      "relaxation_mode": true
    }
  }
}
```

---

## 🧪 Testing Scenarios

### Scenario Progression Testing

```json
{
  "test_sequence": {
    "name": "24_hour_simulation",
    "duration": "24_hours",
    "scenarios": [
      {
        "time": "22:00",
        "scenario": "evening_rest",
        "duration": "2_hours",
        "expected": "gradual environment dimming"
      },
      {
        "time": "00:00",
        "scenario": "sleeping",
        "duration": "6_hours", 
        "expected": "minimal lighting, soft sounds"
      },
      {
        "time": "03:00",
        "scenario": "pain",
        "duration": "30_minutes",
        "expected": "red light activation, healing audio"
      },
      {
        "time": "06:30",
        "scenario": "morning_wake",
        "duration": "1_hour",
        "expected": "gradual brightening, energizing sounds"
      },
      {
        "time": "08:00",
        "scenario": "normal",
        "duration": "14_hours",
        "expected": "standard daytime environment"
      }
    ]
  }
}
```

### Stress Testing Scenarios

```json
{
  "stress_tests": {
    "rapid_changes": {
      "description": "Quick scenario switches",
      "sequence": ["normal", "pain", "normal", "sleep", "normal"],
      "interval": "30_seconds",
      "expected": "AI adapts quickly without overcorrection"
    },
    "extreme_vitals": {
      "description": "Edge case vital signs",
      "scenarios": {
        "high_fever": {"temp": "102.5°F", "hr": "110"},
        "low_oxygen": {"spo2": "88%", "hr": "95"},
        "hypertension": {"bp": "160/95", "hr": "85"}
      },
      "expected": "Appropriate alerts and environment changes"
    },
    "equipment_failure": {
      "description": "Simulated sensor failures",
      "failures": ["heart_rate", "spo2", "temperature"],
      "expected": "Graceful degradation, use available data"
    }
  }
}
```

---

## 📋 Batch Simulation

### Multi-Patient Testing

```json
{
  "batch_configuration": {
    "patients": [
      {
        "id": "patient_001",
        "age": 45,
        "condition": "post_surgical",
        "scenarios": ["normal", "pain", "sleeping", "evening_rest"]
      },
      {
        "id": "patient_002", 
        "age": 72,
        "condition": "cardiac_monitoring",
        "scenarios": ["normal", "sleeping", "morning_wake"]
      },
      {
        "id": "patient_003",
        "age": 28,
        "condition": "recovery", 
        "scenarios": ["normal", "evening_rest", "sleeping", "morning_wake"]
      }
    ],
    "test_parameters": {
      "duration_per_scenario": "5_minutes",
      "interval_between_changes": "2_seconds",
      "data_collection": "continuous",
      "ai_response_tracking": true
    }
  }
}
```

### Performance Testing

```json
{
  "performance_tests": {
    "concurrent_rooms": {
      "room_count": 50,
      "scenario_randomization": true,
      "stress_duration": "24_hours",
      "metrics_tracked": [
        "ai_response_time",
        "environment_change_latency", 
        "system_resource_usage",
        "accuracy_of_recommendations"
      ]
    },
    "load_testing": {
      "simultaneous_changes": 10,
      "change_frequency": "every_30_seconds",
      "expected_response_time": "<2_seconds",
      "success_criteria": "99.9%_uptime"
    }
  }
}
```

---

## ⚠️ Edge Cases

### Rare Medical Scenarios

```json
{
  "edge_cases": {
    "cardiac_event": {
      "vitals": {
        "heart_rate": ">130",
        "blood_pressure": ">160/100",
        "spo2": "<92%"
      },
      "ai_response": "immediate_alert",
      "environment": "emergency_lighting",
      "notification": "critical_staff_alert"
    },
    "respiratory_distress": {
      "vitals": {
        "spo2": "<88%",
        "respiratory_rate": ">30",
        "movement": ">0.8"
      },
      "ai_response": "emergency_protocol",
      "environment": "maximum_alertness",
      "notification": "medical_team_alert"
    },
    "seizure_activity": {
      "vitals": {
        "movement": ">0.95",
        "heart_rate": ">120",
        "pattern": "rhythmic_spikes"
      },
      "ai_response": "seizure_protocol",
      "environment": "protective_mode",
      "notification": "immediate_medical_response"
    }
  }
}
```

### System Edge Cases

```json
{
  "system_edges": {
    "sensor_malfunction": {
      "missing_data": ["heart_rate"],
      "ai_behavior": "use_available_sensors",
      "confidence_reduction": "25%",
      "notification": "sensor_maintenance_needed"
    },
    "network_interruption": {
      "duration": "5_minutes",
      "ai_behavior": "local_fallback_rules",
      "data_buffering": true,
      "sync_on_reconnect": true
    },
    "power_fluctuation": {
      "affected_devices": ["lights", "audio"],
      "ai_behavior": "maintain_monitoring",
      "priority": "patient_safety_first"
    }
  }
}
```

---

## ✅ Validation Rules

### Data Integrity Checks

```python
def validate_synthetic_data(data):
    """Validate generated synthetic data"""
    rules = {
        'heart_rate': {'min': 30, 'max': 200, 'type': int},
        'spo2': {'min': 70, 'max': 100, 'type': int},
        'temperature': {'min': 95.0, 'max': 110.0, 'type': float},
        'movement': {'min': 0.0, 'max': 1.0, 'type': float},
        'respiratory_rate': {'min': 8, 'max': 40, 'type': int},
        'blood_pressure_systolic': {'min': 70, 'max': 200, 'type': int},
        'blood_pressure_diastolic': {'min': 40, 'max': 120, 'type': int}
    }
    
    for field, constraints in rules.items():
        value = data.get(field)
        if value is None:
            raise ValueError(f"Missing required field: {field}")
        if not isinstance(value, constraints['type']):
            raise TypeError(f"Invalid type for {field}")
        if value < constraints['min'] or value > constraints['max']:
            raise ValueError(f"{field} out of range: {value}")
    
    # Logical consistency checks
    if data['blood_pressure_diastolic'] >= data['blood_pressure_systolic']:
        raise ValueError("Diastolic pressure cannot be >= systolic")
    
    return True
```

### AI Response Validation

```python
def validate_ai_response(response, patient_state):
    """Validate AI response appropriateness"""
    
    # Pain scenario should trigger red light therapy
    if 'pain' in patient_state:
        if response.get('light_color') != 'red':
            return False, "Pain detected but red light therapy not activated"
    
    # Sleep scenarios should have low brightness
    if 'sleep' in patient_state:
        if response.get('light_brightness', 100) > 20:
            return False, "Sleep state but brightness too high"
    
    # Morning should have cool light
    if 'morning' in patient_state:
        if response.get('light_color') != 'cool':
            return False, "Morning wake but not using cool light"
    
    return True, "Response appropriate"
```

---

## 🔗 Integration Examples

### API Integration
```python
# Generate synthetic data for testing
response = requests.get('/api/test/synthetic-data/patient_001')
synthetic_data = response.json()

# Process through AI system
ai_response = requests.post('/api/ai/optimize/room_101', 
                           json=synthetic_data)

# Validate response
is_valid, message = validate_ai_response(
    ai_response.json(), 
    synthetic_data['patient_state']
)
```

### Continuous Testing
```python
# 24-hour simulation
scenarios = ['normal', 'evening_rest', 'sleeping', 'morning_wake']
for scenario in scenarios:
    data = generate_synthetic_data('patient_001', scenario)
    ai_response = process_with_ai(data)
    validate_and_log(ai_response, scenario)
    time.sleep(test_interval)
```

---

## 📋 Summary

The synthetic data rules provide:

1. **Realistic Patient Scenarios** - Medically accurate vital sign patterns
2. **AI Training Data** - Consistent scenarios for AI learning
3. **System Validation** - Test edge cases and normal operations
4. **Performance Testing** - Load testing with multiple patients
5. **Medical Accuracy** - All data follows clinical guidelines

Use these rules to ensure your Beat Suite AI system responds appropriately to all patient conditions and maintains high standards of healthcare monitoring.

---

## 🔗 Related Documentation

- [JSON Formats Guide](JSON_FORMATS.md) - Complete API format reference
- [Complete Guide](COMPLETE_GUIDE.md) - Full system documentation  
- [AI Environment Control](AI_ENVIRONMENT_CONTROL.md) - AI system details

---

*Last Updated: November 21, 2025 | Version 2.1*