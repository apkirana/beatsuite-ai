# 🎮 IoT Device Simulation Tools & Apps

Complete guide to simulate smartwatches, smart lights, and audio devices for testing Beat Suite AI.

---

## 📱 Smartwatch Simulators

### 1. **Apple Watch Simulator** (macOS only) ⭐ BEST for iOS
```bash
# Comes with Xcode - FREE
# Install Xcode from App Store

# Run Watch Simulator
open -a Simulator

# In Xcode:
1. Open Xcode → Window → Devices and Simulators
2. Click "+" to add Apple Watch
3. Pair with iPhone simulator
4. Use Health app to generate data
```

**Features:**
- ✅ Real HealthKit data
- ✅ Heart rate, steps, sleep data
- ✅ Can send data to your Flask backend via API
- ✅ FREE

**Integration with Beat Suite:**
```python
# backend/core/smartwatch.py - Add Apple Watch integration
from healthkit import HealthKitConnector

def connect_apple_watch_simulator():
    # Connect to simulator's HealthKit
    # Read heart rate, temperature, etc.
    pass
```

---

### 2. **Fitbit Studio** (Web-based) ⭐ BEST for Fitbit
- **URL**: https://studio.fitbit.com/
- **Features**: 
  - Online Fitbit device simulator
  - Test apps in browser
  - Generate mock health data
  - FREE

---

### 3. **Android Wear Emulator** (Cross-platform)
```bash
# Via Android Studio - FREE
# Download: https://developer.android.com/studio

# Create Wear OS Virtual Device:
1. Android Studio → Tools → AVD Manager
2. Create Virtual Device → Wear OS
3. Choose Wear OS device (e.g., Round Chin)
4. Download system image
5. Launch emulator
```

**Features:**
- ✅ Google Fit integration
- ✅ Heart rate sensor simulation
- ✅ Step counter
- ✅ FREE

---

### 4. **Postman / HTTP Client** ⭐ EASIEST
Simulate smartwatch data by sending HTTP requests to your backend:

```bash
# Install Postman or use curl
curl -X POST http://localhost:5001/api/test/synthetic-data/P001 \
  -H "Content-Type: application/json"

# Returns realistic vitals:
{
  "heart_rate": 72,
  "temperature": 36.8,
  "spo2": 98,
  "respiratory_rate": 16
}
```

**Your Backend Already Has This!** ✅
```python
# Use existing test endpoints:
GET  /api/test/synthetic-data/<patient_id>  # Generate fake vitals
POST /api/test/simulate-ai-adjustment/<patient_id>  # Test AI
```

---

## 💡 Smart Light Simulators

### 1. **Philips Hue Emulator** ⭐ BEST for Hue
```bash
# diyHue - FREE Open Source Hue Bridge Emulator
# GitHub: https://github.com/diyhue/diyHue

# Install with Docker:
docker run -d --name diyhue \
  -p 80:80 -p 443:443 \
  -v /path/to/config:/opt/hue-emulator/config \
  diyhue/core:latest

# Or install directly:
git clone https://github.com/diyhue/diyHue.git
cd diyHue
./install.sh
```

**Features:**
- ✅ Full Philips Hue API compatibility
- ✅ Virtual light bulbs
- ✅ Web interface to see lights change
- ✅ Works with your backend's Philips Hue integration
- ✅ FREE

**Connect to Beat Suite:**
```python
# backend/core/iot_controller.py
light_controller = SmartLightController('philips_hue')

# Config:
HUE_BRIDGE_IP = 'localhost'  # diyHue running locally
HUE_API_KEY = 'your_api_key'
```

---

### 2. **LIFX HTTP API Simulator** 
```python
# Create mock LIFX server - Python Flask
# lifx_simulator.py

from flask import Flask, request, jsonify

app = Flask(__name__)
lights = {}

@app.route('/v1/lights/<selector>/state', methods=['PUT'])
def set_light_state(selector):
    data = request.json
    lights[selector] = data
    print(f"💡 Light {selector}: {data}")
    return jsonify({"results": [{"status": "ok"}]})

@app.route('/v1/lights/<selector>', methods=['GET'])
def get_light_state(selector):
    return jsonify({"color": "blue", "brightness": 0.7})

app.run(port=8089)
```

---

### 3. **Virtual Smart Home (Browser-based)** ⭐ EASIEST
**Your IoT Simulator is Already Built!** ✅

Access at: **http://localhost:5001/iot-simulator**

**Features:**
- ✅ Visual lamp with real-time color changes
- ✅ Music player with volume control
- ✅ Shows AI decisions
- ✅ No installation needed!
- ✅ Already integrated with your backend

**How to Use:**
1. Open: http://localhost:5001/iot-simulator
2. Login with admin credentials
3. See rooms with virtual devices
4. AI automatically controls them based on patient data

---

## 🔊 Audio/Music Simulators

### 1. **Sonos API Simulator**
```bash
# node-sonos-http-api - FREE
# GitHub: https://github.com/jishi/node-sonos-http-api

npm install -g sonos-http-api
sonos-http-api

# Runs on: http://localhost:5005
```

**Endpoints:**
```bash
# Play music
http://localhost:5005/bedroom/play

# Set volume
http://localhost:5005/bedroom/volume/30
```

---

### 2. **Spotify Web API (Real but Testable)** ⭐ BEST for Real Music
```bash
# FREE with Spotify account
# https://developer.spotify.com/

# 1. Create app at: https://developer.spotify.com/dashboard
# 2. Get credentials (Client ID, Secret)
# 3. Use Web Playback SDK for browser-based player
```

**Integration:**
```python
# backend/core/iot_controller.py
audio_controller = SmartAudioController('spotify')

# Play on Spotify device
SPOTIFY_CLIENT_ID = 'your_client_id'
SPOTIFY_CLIENT_SECRET = 'your_secret'
```

---

### 3. **Howler.js (Browser Audio)** ⭐ ALREADY IMPLEMENTED
**Your IoT Simulator Already Uses This!** ✅

```javascript
// frontend/static/js/iot_simulator.js
// Plays real audio in browser
const sound = new Howl({
    src: ['/static/audio/calm-ambient.mp3'],
    volume: 0.3
});
sound.play();
```

---

## 🏠 Complete Smart Home Simulators

### 1. **Home Assistant** ⭐ BEST All-in-One Solution
```bash
# FREE Open Source Smart Home Platform
# Install with Docker:

docker run -d \
  --name homeassistant \
  --privileged \
  -p 8123:8123 \
  -v /path/to/config:/config \
  homeassistant/home-assistant:latest

# Access: http://localhost:8123
```

**Features:**
- ✅ Virtual lights, switches, sensors
- ✅ Automation builder
- ✅ REST API to control devices
- ✅ Dashboard to visualize devices
- ✅ Can integrate with Beat Suite via webhooks
- ✅ FREE

**Integration:**
```python
# Call Home Assistant API from Beat Suite
import requests

def control_home_assistant_light(room_id, color, brightness):
    requests.post(
        'http://localhost:8123/api/services/light/turn_on',
        headers={'Authorization': 'Bearer YOUR_TOKEN'},
        json={
            'entity_id': f'light.room_{room_id}',
            'rgb_color': [255, 100, 50],
            'brightness': int(brightness * 255)
        }
    )
```

---

### 2. **OpenHAB** (Alternative to Home Assistant)
- Similar features
- Java-based
- https://www.openhab.org/

---

## 🎯 Recommended Setup for Beat Suite AI

### **Option A: Easiest (No Installation)** ⭐
Use what you already have:

1. **Smartwatch Data**: 
   ```bash
   # Use built-in synthetic data generator
   curl http://localhost:5001/api/test/synthetic-data/P001
   ```

2. **Smart Lights/Audio**: 
   ```
   # Use built-in IoT Simulator
   http://localhost:5001/iot-simulator
   ```

3. **Test Everything**:
   ```bash
   ./test_google_home.sh
   ```

**Pros**: ✅ Zero setup, works immediately

---

### **Option B: Most Realistic** ⭐⭐
Combine real simulators:

1. **Smartwatch**: Apple Watch Simulator (if on Mac) or Postman
2. **Lights**: diyHue Emulator
3. **Audio**: Howler.js (already built-in)
4. **Integration**: Home Assistant for visualization

**Pros**: ✅ Looks and feels like real devices

---

### **Option C: Production-Ready** ⭐⭐⭐
Connect real devices:

1. **Smartwatch**: Real Apple Watch / Fitbit via APIs
2. **Lights**: Real Philips Hue bulbs
3. **Audio**: Real Sonos speakers / Spotify Connect
4. **Hub**: Home Assistant to coordinate

**Pros**: ✅ Actually controls physical devices

---

## 🚀 Quick Start: Home Assistant Setup

```bash
# 1. Install Home Assistant
docker run -d --name homeassistant \
  -p 8123:8123 \
  homeassistant/home-assistant:latest

# 2. Open browser: http://localhost:8123
# 3. Create account
# 4. Add virtual devices:
#    Configuration → Integrations → Demo

# 5. Create automation:
#    Listen for webhook from Beat Suite
#    Control virtual lights based on patient data
```

**Connect Beat Suite to Home Assistant:**
```python
# Add to backend/core/iot_controller.py

import requests

class HomeAssistantController:
    def __init__(self):
        self.base_url = 'http://localhost:8123/api'
        self.token = 'YOUR_LONG_LIVED_TOKEN'
    
    def set_light(self, room_id, color, brightness):
        requests.post(
            f'{self.base_url}/services/light/turn_on',
            headers={'Authorization': f'Bearer {self.token}'},
            json={
                'entity_id': f'light.room_{room_id}',
                'rgb_color': hex_to_rgb(color),
                'brightness': int(brightness * 255)
            }
        )
```

---

## 📊 Comparison Table

| Tool | Type | Cost | Ease of Use | Realism | Setup Time |
|------|------|------|-------------|---------|------------|
| **Built-in IoT Simulator** | Web | FREE | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 0 min |
| **Postman / curl** | HTTP | FREE | ⭐⭐⭐⭐⭐ | ⭐⭐ | 0 min |
| **Apple Watch Simulator** | Watch | FREE | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 30 min |
| **diyHue Emulator** | Lights | FREE | ⭐⭐⭐ | ⭐⭐⭐⭐ | 15 min |
| **Home Assistant** | All-in-One | FREE | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 20 min |
| **Real Devices** | Physical | $$$ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Hours |

---

## 🎓 Tutorial: Add Home Assistant Integration

Want me to create a full integration with Home Assistant? I can add:

1. **Home Assistant API connector** to your backend
2. **Automatic device discovery**
3. **Real-time device control** with visual feedback
4. **Dashboard in Home Assistant** showing patient rooms

Let me know if you want this! 🚀

---

**Which option interests you most?**
- A) Stick with built-in simulator (easiest)
- B) Add Home Assistant (most impressive)
- C) Add Apple Watch Simulator (most realistic health data)
- D) Add diyHue for realistic lights
