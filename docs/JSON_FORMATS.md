# 📋 JSON Formats Guide - Beat Suite AI

**Complete reference for all JSON formats used in Beat Suite AI healthcare system**

Version 2.1 | November 2025

---

## 📋 Table of Contents

1. [AI Environment Control](#ai-environment-control)
2. [Patient Vitals Analysis](#patient-vitals-analysis)
3. [Health Predictions](#health-predictions)
4. [Smart Lighting Rules](#smart-lighting-rules)
5. [Comprehensive Reports](#comprehensive-reports)
6. [Google Home Integration](#google-home-integration)
7. [Gemini Live Configuration](#gemini-live-configuration)
8. [Room Management](#room-management)
9. [Notification System](#notification-system)
10. [Testing & Synthetic Data](#testing--synthetic-data)

---

## 🤖 AI Environment Control

### Standard Environment Optimization Format

```json
{
  "light_brightness": 50,
  "light_color": "warm",
  "light_hex_color": "#FFE4B5",
  "color_temp": 3000,
  "music_volume": 25,
  "music_type": "relaxing",
  "music_playlist_id": "calm_piano",
  "reasoning": "Patient is in light sleep, adjusting for comfort"
}
```

### Field Definitions

| Field | Type | Range/Options | Description |
|-------|------|---------------|-------------|
| `light_brightness` | integer | 0-100 | Brightness percentage |
| `light_color` | string | "warm", "cool", "neutral", "red" | Color temperature type |
| `light_hex_color` | string | hex color code | Exact color value |
| `color_temp` | integer | 1800-6500 | Kelvin temperature |
| `music_volume` | integer | 0-100 | Volume percentage |
| `music_type` | string | "relaxing", "nature", "silence", "healing" | Audio category |
| `music_playlist_id` | string | playlist name | Specific audio selection |
| `reasoning` | string | text | AI explanation for changes |

### Scenario Examples

#### Deep Sleep (2 AM)
```json
{
  "light_brightness": 5,
  "light_color": "warm",
  "light_hex_color": "#FFB347",
  "color_temp": 2000,
  "music_volume": 15,
  "music_type": "nature",
  "music_playlist_id": "rain_sounds",
  "reasoning": "Minimal amber light for deep sleep support"
}
```

#### Pain Detection
```json
{
  "light_brightness": 20,
  "light_color": "red",
  "light_hex_color": "#FF6B35",
  "color_temp": 1800,
  "music_volume": 30,
  "music_type": "healing",
  "music_playlist_id": "432hz_healing",
  "reasoning": "Red light therapy for pain relief with healing frequencies"
}
```

#### Morning Wake-Up (7 AM)
```json
{
  "light_brightness": 70,
  "light_color": "cool",
  "light_hex_color": "#CCE6FF",
  "color_temp": 6500,
  "music_volume": 40,
  "music_type": "energizing",
  "music_playlist_id": "morning_classical",
  "reasoning": "Blue-enriched light to support morning alertness"
}
```

---

## 📊 Patient Vitals Analysis

### AI Analysis Response Format

```json
{
  "status": "Patient is stable and resting comfortably",
  "concerns": ["slightly elevated heart rate", "minor movement detected"],
  "recommendations": ["monitor for next hour", "maintain current environment"],
  "risk_level": "Low",
  "confidence": "92%"
}
```

### Field Definitions

| Field | Type | Options | Description |
|-------|------|---------|-------------|
| `status` | string | text | Overall health summary |
| `concerns` | array | strings | List of detected issues |
| `recommendations` | array | strings | Suggested actions |
| `risk_level` | string | "Low", "Medium", "High", "Critical" | Risk assessment |
| `confidence` | string | percentage | AI confidence level |

### Risk Level Examples

#### Low Risk
```json
{
  "status": "All vitals within normal range, patient sleeping peacefully",
  "concerns": [],
  "recommendations": ["continue current monitoring", "maintain sleep environment"],
  "risk_level": "Low",
  "confidence": "95%"
}
```

#### Medium Risk
```json
{
  "status": "Slightly elevated heart rate, patient appears restless",
  "concerns": ["heart rate 85 BPM (elevated for sleep)", "increased movement"],
  "recommendations": ["check patient comfort", "consider pain assessment", "monitor closely"],
  "risk_level": "Medium",
  "confidence": "87%"
}
```

#### High Risk
```json
{
  "status": "Significant vital sign abnormalities detected",
  "concerns": ["heart rate >100 BPM", "oxygen saturation <95%", "signs of distress"],
  "recommendations": ["immediate nurse assessment", "consider medical intervention", "alert medical staff"],
  "risk_level": "High",
  "confidence": "92%"
}
```

---

## 🔮 Health Predictions

### Trend Analysis Format

```json
{
  "trends": ["heart rate stabilizing", "entering deeper sleep phase"],
  "predictions": ["expect continued rest for 2-3 hours", "vitals should normalize"],
  "preventive_actions": ["maintain dim lighting", "continue soft background audio"],
  "urgency": "Low"
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `trends` | array | Current patterns in patient data |
| `predictions` | array | Expected changes in next few hours |
| `preventive_actions` | array | Actions to prevent complications |
| `urgency` | string | "Low", "Medium", "High" - Action priority |

---

## 💡 Smart Lighting Rules

### Dynamic Lighting Scenarios

#### Circadian Rhythm Support
```json
{
  "morning": {
    "color_hex": "#E6F3FF",
    "brightness": 80,
    "color_temp": 6000,
    "reason": "Blue-white light to promote alertness"
  },
  "afternoon": {
    "color_hex": "#FFFFFF",
    "brightness": 100,
    "color_temp": 5500,
    "reason": "Natural daylight simulation"
  },
  "evening": {
    "color_hex": "#FFCC99",
    "brightness": 60,
    "color_temp": 3000,
    "reason": "Warm light to prepare for sleep"
  },
  "night": {
    "color_hex": "#FF9966",
    "brightness": 10,
    "color_temp": 2000,
    "reason": "Minimal warm light for navigation"
  }
}
```

#### Therapeutic Lighting
```json
{
  "pain_relief": {
    "color_hex": "#FF4500",
    "brightness": 25,
    "color_temp": 1800,
    "duration_minutes": 20,
    "reason": "Red light therapy for pain management"
  },
  "mood_enhancement": {
    "color_hex": "#87CEEB",
    "brightness": 50,
    "color_temp": 4000,
    "duration_minutes": 30,
    "reason": "Blue light therapy for mood support"
  },
  "sleep_induction": {
    "color_hex": "#FFB347",
    "brightness": 5,
    "color_temp": 2000,
    "reason": "Amber light to support melatonin production"
  }
}
```

---

## 📋 Comprehensive Reports

### Complete Health Report Format

```json
{
  "executive_summary": "Patient shows stable vitals with improving sleep patterns over 24-hour period",
  "vital_signs_analysis": "Heart rate averages 68 BPM with good variability. Oxygen saturation excellent at 98%. Temperature stable.",
  "health_trends": "Significant improvement in sleep quality. Heart rate variability increasing. Recovery indicators positive.",
  "detected_concerns": ["minor temperature fluctuation in evening", "brief elevated heart rate during 3 AM period"],
  "positive_indicators": ["stable overnight vitals", "good oxygen saturation", "consistent sleep patterns", "positive response to AI environment"],
  "sleep_recovery": "Patient achieving 6.5 hours quality sleep with 45% deep sleep phases. REM cycles normal. Recovery metrics excellent.",
  "clinical_recommendations": [
    "Continue current treatment protocol",
    "Monitor evening temperature trends",
    "Consider sleep study if patterns change",
    "Maintain AI environmental optimization"
  ],
  "risk_assessment": {
    "level": "Low",
    "factors": ["age-related considerations", "post-surgical monitoring"],
    "mitigation": ["24/7 AI monitoring", "environment optimization", "regular vitals checks"]
  },
  "prognosis": "Excellent trajectory for full recovery. Patient responding well to treatment with strong vital signs and improving sleep quality.",
  "ai_effectiveness": "AI environmental controls providing optimal support. Light therapy improving sleep by 23%. Music therapy reducing stress indicators by 18%.",
  "confidence_score": 89
}
```

---

## 🏠 Google Home Integration

### Voice Command Processing

#### Room Status Query
```json
{
  "queryResult": {
    "intent": {
      "displayName": "GetPatientVitals"
    },
    "parameters": {
      "room_number": "101"
    }
  }
}
```

#### Light Control
```json
{
  "queryResult": {
    "intent": {
      "displayName": "ControlLight"
    },
    "parameters": {
      "room_number": "102",
      "action": "on",
      "color": "blue",
      "brightness": "70"
    }
  }
}
```

#### Music Control
```json
{
  "queryResult": {
    "intent": {
      "displayName": "ControlMusic"
    },
    "parameters": {
      "room_number": "103",
      "action": "play",
      "music_type": "relaxing",
      "volume": "25"
    }
  }
}
```

#### AI Control
```json
{
  "queryResult": {
    "intent": {
      "displayName": "EnableAI"
    },
    "parameters": {
      "room_number": "104",
      "action": "enable"
    }
  }
}
```

---

## 🎙️ Gemini Live Configuration

### WebSocket Configuration
```json
{
  "model": "models/gemini-2.0-flash-exp",
  "generationConfig": {
    "responseModalities": "audio",
    "speechConfig": {
      "voiceConfig": {
        "prebuiltVoiceConfig": {
          "voiceName": "Aoede"
        }
      }
    }
  },
  "systemInstruction": {
    "parts": [{
      "text": "You are Dr. AI, a caring medical AI assistant..."
    }]
  }
}
```

### Healthcare System Instructions
```json
{
  "parts": [{
    "text": "You are Dr. AI, a caring medical AI assistant at Beat Suite AI healthcare system. You're helping with Sarah's care in Room 101.\n\nCurrent Patient Status:\n- Heart Rate: 72 BPM\n- Temperature: 98.1°F\n- SpO2: 98%\n- Sleep Stage: Light Sleep\n- Pain Detected: False\n- AI Environmental Control: Active\n\nYour Communication Style:\n• Sound human and warm - like a caring nurse colleague\n• Use natural, conversational language with contractions\n• Be reassuring when vitals are good, concerned when needed\n• Keep responses concise but informative (1-3 sentences)\n• Use medical terminology appropriately but explain when needed"
  }]
}
```

---

## 🏥 Room Management

### Room Data Structure
```json
{
  "id": "room_101",
  "room_number": "101",
  "patient": {
    "name": "Sarah Johnson",
    "age": 45,
    "condition": "Post-surgical recovery",
    "admission_date": "2025-11-20"
  },
  "vitals": {
    "heart_rate": 72,
    "spo2": 98,
    "temperature": 98.1,
    "movement": 0.2,
    "sleep_stage": "Light Sleep",
    "last_updated": "2025-11-21T14:30:00Z"
  },
  "environment": {
    "ai_control_active": true,
    "current_ai_settings": {
      "light_brightness": 20,
      "light_hex_color": "#FFE4B5",
      "music_volume": 15,
      "music_playlist_id": "nature_sounds",
      "ai_reasoning": "Optimizing for light sleep phase"
    }
  },
  "status": "occupied"
}
```

---

## 🔔 Notification System

### Critical Alert Format
```json
{
  "id": "notif_20251121143000",
  "type": "critical_vitals",
  "severity": "high",
  "room_id": "101",
  "patient_name": "Sarah Johnson",
  "message": "Critical: Heart rate >120 BPM for 5+ minutes",
  "vitals": {
    "heart_rate": 125,
    "spo2": 94,
    "timestamp": "2025-11-21T14:30:00Z"
  },
  "recommended_actions": [
    "Immediate nurse assessment",
    "Check patient comfort",
    "Consider medical intervention"
  ],
  "target_roles": ["admin", "nurse"],
  "created_at": "2025-11-21T14:30:15Z",
  "read": false
}
```

### Standard Notification
```json
{
  "id": "notif_20251121140000",
  "type": "ai_optimization",
  "severity": "info",
  "room_id": "102",
  "patient_name": "John Smith",
  "message": "AI adjusted environment for deep sleep phase",
  "changes": {
    "light_brightness": "reduced to 5%",
    "music_volume": "lowered to 10%",
    "reason": "Patient entered deep sleep"
  },
  "target_roles": ["nurse"],
  "created_at": "2025-11-21T14:00:00Z",
  "read": false
}
```

---

## 🧪 Testing & Synthetic Data

### Test Scenario Format
```json
{
  "scenario": "pain",
  "patient_state": "distressed - possible pain",
  "vitals": {
    "heart_rate": 95,
    "spo2": 95,
    "movement": 0.8,
    "temperature": 99.2,
    "respiratory_rate": 22,
    "blood_pressure_systolic": 140,
    "blood_pressure_diastolic": 90
  },
  "ai_recommendations": {
    "light": "red therapy at 20%",
    "music": "healing frequencies at 30%",
    "reasoning": "Pain detected - activating therapeutic environment"
  },
  "timestamp": "2025-11-21T14:30:00Z"
}
```

### Batch Testing
```json
{
  "scenarios": ["normal", "evening_rest", "sleeping", "pain", "morning_wake"],
  "interval_seconds": 5,
  "iterations": 3,
  "expected_outcomes": {
    "normal": "moderate brightness and volume",
    "sleeping": "minimal brightness, soft sounds",
    "pain": "red light therapy activated",
    "morning_wake": "bright cool light"
  }
}
```

---

## 📋 Validation Rules

### Required Fields by Context

#### Environment Control (Required)
- `light_brightness` (0-100)
- `light_color` (enum)
- `music_volume` (0-100)
- `reasoning` (string)

#### Vitals Analysis (Required)
- `status` (string)
- `risk_level` (enum)
- `confidence` (percentage)

#### Health Reports (Required)
- `executive_summary` (string)
- `risk_assessment` (object)
- `confidence_score` (0-100)

### Data Types & Constraints

```json
{
  "constraints": {
    "brightness": {"min": 0, "max": 100, "type": "integer"},
    "volume": {"min": 0, "max": 100, "type": "integer"},
    "color_temp": {"min": 1800, "max": 6500, "type": "integer"},
    "confidence": {"min": 0, "max": 100, "type": "integer"},
    "risk_level": ["Low", "Medium", "High", "Critical"],
    "urgency": ["Low", "Medium", "High"]
  }
}
```

---

## 🔗 Related Documentation

- [Complete Guide](COMPLETE_GUIDE.md) - Full system documentation
- [AI Environment Control](AI_ENVIRONMENT_CONTROL.md) - Detailed AI system guide
- [Deployment Guide](DEPLOYMENT.md) - Production setup instructions

---

*Last Updated: November 21, 2025 | Version 2.1*