# Beat Suite AI - Testing Guide

## Auto Remote Control System Overview

Your app **already has AI auto-adjustment built in!** Here's how it works:

### 🎯 System Components

1. **Smartwatch Simulator** (`backend/core/smartwatch.py`)
   - Generates synthetic patient vitals (heart rate, movement, SpO2)
   - Simulates realistic circadian patterns
   - Automatically varies data based on time of day

2. **AI Engine** (`backend/core/ai_engine.py`)
   - Analyzes patient data in real-time
   - Detects sleep stages, pain indicators
   - Generates environment recommendations

3. **IoT Controller** (`backend/core/iot_controller.py`)
   - Controls smart lights (color, brightness)
   - Controls audio systems (playlists, volume)
   - Currently in **simulated mode** for testing

### 🤖 How AI Auto-Adjustment Works

```
Patient Vitals → AI Analysis → Environment Control
   (Smartwatch)    (AI Engine)    (IoT Devices)
```

**Example Flow:**
1. Patient enters **deep sleep** (low HR, minimal movement)
   - AI detects sleep stage
   - **Lights**: Dim amber (5% brightness)
   - **Music**: Binaural sleep frequencies (15% volume)

2. Patient shows **pain indicators** (high HR, restless)
   - AI detects distress
   - **Lights**: Red light therapy (20% brightness)
   - **Music**: 432Hz healing frequencies (25% volume)

3. **Morning wake-up** (increasing HR, movement)
   - AI detects circadian morning phase
   - **Lights**: Blue-enriched (70% brightness)
   - **Music**: Energizing upbeat playlist (30% volume)

---

## 🧪 Testing API Endpoints

### 1. List Available Test Scenarios

```bash
curl http://localhost:5001/api/test/scenarios
```

**Available Scenarios:**
- `normal` - Healthy awake state
- `sleeping` - Deep sleep
- `pain` - Distress/pain indicators
- `morning_wake` - Morning wake-up
- `evening_rest` - Evening wind-down

### 2. Generate Synthetic Patient Data

```bash
# Normal state
curl http://localhost:5001/api/test/synthetic-data/P001?scenario=normal \
  -H "Cookie: session_token=YOUR_TOKEN"

# Sleeping state
curl http://localhost:5001/api/test/synthetic-data/P001?scenario=sleeping \
  -H "Cookie: session_token=YOUR_TOKEN"

# Pain/distress state
curl http://localhost:5001/api/test/synthetic-data/P001?scenario=pain \
  -H "Cookie: session_token=YOUR_TOKEN"
```

**Response Example:**
```json
{
  "success": true,
  "scenario": "sleeping",
  "data": {
    "patient_id": "P001",
    "heart_rate": 58,
    "spo2": 97,
    "movement": 0.12,
    "temperature": 97.4,
    "respiratory_rate": 14,
    "blood_pressure_systolic": 108,
    "blood_pressure_diastolic": 68,
    "state": "deep sleep"
  }
}
```

### 3. Simulate AI Auto-Adjustment

```bash
# Using scenario
curl -X POST http://localhost:5001/api/test/simulate-ai-adjustment/P001 \
  -H "Content-Type: application/json" \
  -H "Cookie: session_token=YOUR_TOKEN" \
  -d '{"scenario": "pain"}'

# Using custom vitals
curl -X POST http://localhost:5001/api/test/simulate-ai-adjustment/P001 \
  -H "Content-Type: application/json" \
  -H "Cookie: session_token=YOUR_TOKEN" \
  -d '{
    "heart_rate": 110,
    "movement": 0.8,
    "spo2": 95
  }'
```

**Response Example:**
```json
{
  "success": true,
  "patient_id": "P001",
  "input_data": {
    "heart_rate": 110,
    "movement": 0.8,
    "spo2": 95
  },
  "ai_analysis": {
    "sleep_stage": "awake",
    "pain_detected": true,
    "pain_severity": 0.75,
    "circadian_phase": "afternoon"
  },
  "environment_adjustments": {
    "light": {
      "color_hex": "#FF6B4A",
      "brightness": 0.2,
      "color_temp": 1800,
      "reason": "Red light therapy for pain relief"
    },
    "music": {
      "playlist_id": "healing_frequencies",
      "volume": 0.25,
      "reason": "432Hz healing frequencies for pain management"
    }
  },
  "ai_reasoning": "Elevated heart rate and high movement detected. Patient may be experiencing discomfort. Applying red light therapy and healing frequencies."
}
```

### 4. Check Virtual Environment Status

```bash
curl http://localhost:5001/api/test/environment-status/P001 \
  -H "Cookie: session_token=YOUR_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "room_id": "P001",
  "light": {
    "color": "#FF6B4A",
    "brightness": 0.2,
    "updated": 1700412345.67
  },
  "audio": {
    "playlist": "healing_frequencies",
    "volume": 0.25,
    "playing": true,
    "updated": 1700412345.67
  }
}
```

### 5. Batch Simulation (Multiple Scenarios)

```bash
curl -X POST http://localhost:5001/api/test/batch-simulation/P001 \
  -H "Content-Type: application/json" \
  -H "Cookie: session_token=YOUR_TOKEN" \
  -d '{
    "scenarios": ["morning_wake", "normal", "evening_rest", "sleeping"],
    "interval_seconds": 2
  }'
```

---

## 🎮 Interactive Testing (Browser)

### Using the Dashboard

1. **Login** to http://localhost:5001/dashboard as admin
2. **View Room Cards** - See current AI status for each patient
3. **Click Room Card** - View detailed vitals and environment settings
4. **Override AI** - Manually control lights/music (AI pauses)
5. **Resume AI** - Let AI take control again

### AI Status Indicators

- ✅ **AI Active** - Green badge, auto-adjusting
- ⏸️ **Manual Override** - Orange badge, AI paused

---

## 🔌 Real Hardware Integration

### To Connect Real Devices:

1. **Smart Lights** (Philips Hue, LIFX, Nanoleaf)
   
   Update `backend/core/iot_controller.py`:
   ```python
   # Change from 'simulated' to your device type
   light_controller = SmartLightController('philips_hue')
   
   # Add API credentials
   HUE_BRIDGE_IP = 'YOUR_BRIDGE_IP'
   HUE_API_KEY = 'YOUR_API_KEY'
   ```

2. **Audio Systems** (Sonos, Spotify)
   
   Update `backend/core/iot_controller.py`:
   ```python
   audio_controller = SmartAudioController('sonos')
   
   # Add credentials
   SONOS_IP = 'YOUR_SONOS_IP'
   ```

3. **Smartwatches** (Apple Watch, Fitbit, Garmin)
   
   Update `backend/core/smartwatch.py`:
   ```python
   # Register real device instead of simulator
   smartwatch_manager.register_device("P001", "apple_watch")
   
   # Add HealthKit integration
   from backend.core.healthkit import HealthKitConnector
   ```

---

## 📊 Example Test Sequence

### Scenario: Testing Full 24-Hour Cycle

```bash
# 1. Morning (6 AM) - Wake up
curl -X POST http://localhost:5001/api/test/simulate-ai-adjustment/P001 \
  -d '{"scenario": "morning_wake"}' -H "Content-Type: application/json"

# Expected: Blue-enriched light (70%), energizing music

# 2. Afternoon (2 PM) - Normal activity
curl -X POST http://localhost:5001/api/test/simulate-ai-adjustment/P001 \
  -d '{"scenario": "normal"}' -H "Content-Type: application/json"

# Expected: Neutral light (60%), ambient music

# 3. Evening (8 PM) - Winding down
curl -X POST http://localhost:5001/api/test/simulate-ai-adjustment/P001 \
  -d '{"scenario": "evening_rest"}' -H "Content-Type: application/json"

# Expected: Warm light (40%), calming music

# 4. Night (11 PM) - Deep sleep
curl -X POST http://localhost:5001/api/test/simulate-ai-adjustment/P001 \
  -d '{"scenario": "sleeping"}' -H "Content-Type: application/json"

# Expected: Dim amber (5%), sleep binaural beats

# 5. Pain event (2 AM) - Distress detected
curl -X POST http://localhost:5001/api/test/simulate-ai-adjustment/P001 \
  -d '{"scenario": "pain"}' -H "Content-Type: application/json"

# Expected: Red light therapy (20%), healing frequencies
```

---

## 🔐 Authentication for API Testing

### Get Session Token

```bash
# Login
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  -c cookies.txt

# Use cookies in subsequent requests
curl http://localhost:5001/api/test/scenarios -b cookies.txt
```

---

## 📈 Monitoring AI Decisions

### Check Server Logs

```bash
tail -f /Users/puspa.kirana/Documents/GitHub/hqgoogle/server.log
```

**Look for:**
- `[LIGHTS] Room room_101: Color=#FFAA77, Brightness=40%`
- `[AUDIO] Room room_101: Playing 'calm_ambient' at 20% volume`
- `[AI] Patient P001: sleep_stage=light_sleep, pain=False`

---

## 🎯 Key Features Already Implemented

✅ **AI Sleep Stage Detection** - Deep sleep, light sleep, REM, awake
✅ **Pain Detection** - Elevated HR + movement patterns
✅ **Circadian Rhythm Alignment** - Time-of-day adjustments
✅ **Light Therapy** - Color temperature optimization
✅ **Music Therapy** - Playlist selection based on state
✅ **Manual Override** - Staff can pause AI and control manually
✅ **Real-time Updates** - Dashboard refreshes every 5 seconds
✅ **Synthetic Data Generation** - Full testing without real sensors

---

## 🚀 Next Steps

1. **Test the API endpoints** using the examples above
2. **View AI decisions** in real-time on the dashboard
3. **Experiment with scenarios** to see different AI responses
4. **Connect real hardware** when ready for production
5. **Customize AI logic** in `backend/core/ai_engine.py`

---

## 📝 Notes

- **Simulated Mode**: Safe for testing, no real devices needed
- **Production Mode**: Requires real smartwatch APIs and IoT devices
- **AI Learning**: Currently rule-based, can be enhanced with ML models
- **Data Privacy**: All patient data stays local in JSON files

---

## 🆘 Support

For real hardware integration help, check:
- Philips Hue API: https://developers.meethue.com/
- LIFX API: https://api.developer.lifx.com/
- Apple HealthKit: https://developer.apple.com/healthkit/
- Fitbit Web API: https://dev.fitbit.com/
