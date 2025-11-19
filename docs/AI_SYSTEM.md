# 🤖 AI Auto Remote Control - Complete System

## ✅ Your System Already Has Auto Remote Control!

The AI automatically adjusts lights and music based on patient conditions in real-time.

## 📋 What's Already Built

### 1. Smart Environment Control
- **Smart Lights**: Color, brightness, color temperature
- **Audio System**: Playlist selection, volume control
- **Circadian Alignment**: Time-of-day awareness
- **Pain Detection**: Automatic red light + healing music

### 2. AI Decision Engine
- **Sleep Stage Detection**: Awake, light sleep, deep sleep, REM
- **Pain Indicators**: Heart rate spikes + movement patterns
- **Circadian Phase**: Morning, afternoon, evening, night
- **Real-time Adaptation**: Continuous monitoring and adjustment

### 3. Patient Monitoring
- **Smartwatch Integration**: Heart rate, movement, SpO2
- **Synthetic Data Generator**: For testing without real sensors
- **Historical Tracking**: Maintains patient vital history
- **Anomaly Detection**: Flags unusual patterns

## 🎮 How to Use It

### Option 1: Use the Dashboard (Visual)
1. Go to http://localhost:5001/dashboard
2. Login as admin (admin/admin123)
3. See AI status on room cards: ✅ AI Active
4. Click room to see live adjustments
5. AI updates every 5 seconds automatically

### Option 2: Use Testing API (Programmatic)
```bash
# Test different patient scenarios
curl -X POST http://localhost:5001/api/test/simulate-ai-adjustment/P001 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"scenario": "pain"}'
```

See **QUICK_TEST.md** for all commands.

## 🔄 How Auto-Adjustment Works

```
┌─────────────┐     ┌──────────┐     ┌────────────┐     ┌──────────┐
│ Smartwatch  │────▶│ AI Engine│────▶│ Decision   │────▶│ IoT      │
│ (Patient)   │     │ Analysis │     │ Logic      │     │ Control  │
└─────────────┘     └──────────┘     └────────────┘     └──────────┘
   Heart Rate         Sleep Stage      Light Settings     Lights On
   Movement          Pain Detection    Music Selection    Music Play
   SpO2              Circadian Phase   Volume/Brightness  Auto-Adjust
```

### Example Scenarios:

**Scenario 1: Patient Falls Asleep (10 PM)**
- **Detected**: HR drops to 55, movement < 0.1
- **AI Decision**: Deep sleep detected
- **Action**: 
  - Lights → Amber, 5% brightness
  - Music → Binaural sleep beats, 15% volume

**Scenario 2: Patient in Pain (2 AM)**
- **Detected**: HR spikes to 115, movement 0.85
- **AI Decision**: Pain/distress indicators
- **Action**:
  - Lights → Red therapy, 20% brightness
  - Music → 432Hz healing frequencies, 25% volume

**Scenario 3: Morning Wake-Up (7 AM)**
- **Detected**: HR 75, movement increasing
- **AI Decision**: Circadian morning phase
- **Action**:
  - Lights → Blue-enriched, 70% brightness
  - Music → Energizing playlist, 30% volume

## 🧪 Testing Without Real Hardware

All IoT control is currently **simulated** for safe testing:

```python
# In backend/core/iot_controller.py
light_controller = SmartLightController('simulated')  # Safe mode
audio_controller = SmartAudioController('simulated')  # Safe mode
```

**What "simulated" means:**
- ✅ AI makes real decisions
- ✅ Logs all commands
- ✅ Tracks state changes
- ❌ Doesn't control real lights/speakers
- ✅ Perfect for testing and demos

## 🔌 Connect Real Hardware (When Ready)

### Philips Hue Lights
```python
# Change in backend/core/iot_controller.py
light_controller = SmartLightController('philips_hue')

# Add config
HUE_BRIDGE_IP = '192.168.1.100'
HUE_API_KEY = 'your_api_key_here'
```

### Sonos Audio
```python
audio_controller = SmartAudioController('sonos')

# Add config
SONOS_IP = '192.168.1.101'
```

### Apple Watch / Real Smartwatch
```python
# Change in backend/core/smartwatch.py
smartwatch_manager.register_device("P001", "apple_watch")

# Add HealthKit integration
from backend.core.healthkit import HealthKitConnector
```

## 📊 API Endpoints for Testing

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/test/scenarios` | GET | List all test scenarios |
| `/api/test/synthetic-data/<id>` | GET | Generate patient vitals |
| `/api/test/simulate-ai-adjustment/<id>` | POST | Test AI decision |
| `/api/test/environment-status/<id>` | GET | Check current settings |
| `/api/test/batch-simulation/<id>` | POST | Run multiple scenarios |

## 🎯 Test Right Now

1. **Open Terminal:**
   ```bash
   cd /Users/puspa.kirana/Documents/GitHub/hqgoogle
   ```

2. **Login:**
   ```bash
   curl -X POST http://localhost:5001/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}' \
     -c cookies.txt
   ```

3. **Test Pain Scenario:**
   ```bash
   curl -X POST http://localhost:5001/api/test/simulate-ai-adjustment/P001 \
     -H "Content-Type: application/json" -b cookies.txt \
     -d '{"scenario": "pain"}' | python3 -m json.tool
   ```

4. **Watch the Logs:**
   ```bash
   tail -f server.log | grep -E "LIGHTS|AUDIO"
   ```

You'll see output like:
```
[LIGHTS] Room P001: Color=#FF6B4A, Brightness=20%
[AUDIO] Room P001: Playing 'healing_frequencies' at 25% volume
```

## 📚 Documentation Files

- **TESTING_GUIDE.md** - Complete testing documentation
- **QUICK_TEST.md** - Quick reference commands
- **AI_SYSTEM.md** - This file
- **PROJECT_STRUCTURE.md** - Overall architecture

## 🎨 AI Light Settings Reference

| State | Color | Brightness | Reasoning |
|-------|-------|------------|-----------|
| Deep Sleep | Amber (#FFAA77) | 5% | Melatonin production |
| Light Sleep | Warm (#FFD699) | 15% | Sleep maintenance |
| Pain/Distress | Red (#FF6B4A) | 20% | Red light therapy |
| Morning | Blue-enriched (#E0F4FF) | 70% | Circadian alertness |
| Evening | Warm (#FFD699) | 40% | Relaxation |
| Awake/Normal | Neutral (#F5F5DC) | 60% | Daytime activity |

## 🎵 AI Music Settings Reference

| State | Playlist | Volume | Purpose |
|-------|----------|--------|---------|
| Deep Sleep | binaural_sleep | 15% | Delta waves |
| Pain | healing_frequencies | 25% | 432Hz therapy |
| Morning | upbeat_morning | 30% | Energy boost |
| Relaxing | calm_ambient | 20% | Stress reduction |
| Night | binaural_sleep | 10% | Quiet ambience |

## ⚙️ Configuration Files

- **backend/core/ai_engine.py** - AI decision logic
- **backend/core/iot_controller.py** - Device control
- **backend/core/smartwatch.py** - Data collection
- **backend/api/test_routes.py** - Testing endpoints
- **backend/data/room_monitoring.json** - Live room data

## 🚀 What's Next?

1. ✅ **System is ready** - AI auto-control is working
2. ✅ **Test with synthetic data** - Use testing API
3. ✅ **View on dashboard** - See live updates
4. ⏳ **Connect real sensors** - When hardware available
5. ⏳ **Train ML models** - Enhance AI predictions
6. ⏳ **Add more devices** - Expand to temperature, humidity, etc.

## 💡 Key Takeaways

1. **AI is already running** - No setup needed
2. **Fully testable** - Without real hardware
3. **Production-ready architecture** - Easy to connect real devices
4. **Comprehensive logging** - See every decision
5. **Manual override available** - Staff can pause AI anytime

## 🆘 Need Help?

- Check server logs: `tail -f server.log`
- Test scenarios: See QUICK_TEST.md
- API reference: See TESTING_GUIDE.md
- System architecture: See PROJECT_STRUCTURE.md

---

**Your AI auto remote control system is live and ready to test!** 🎉
