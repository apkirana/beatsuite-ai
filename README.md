# 🏥 Beat Suite AI - Healthcare Monitoring System

**AI-Powered Healthcare Monitoring with Real-time Voice Conversation & Smart Environment Control**

[![Deploy Status](https://img.shields.io/badge/Deploy-GCP%20Cloud%20Run-blue)](https://beatsuite-675304702130.us-central1.run.app)
[![AI Status](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-green)](https://ai.google.dev)
[![Voice Chat](https://img.shields.io/badge/Voice-Gemini%20Live-purple)](https://ai.google.dev/gemini-api/docs/live)

> **🎙️ NEW: Gemini Live Integration** - Real-time bidirectional voice conversations with AI using Google's Gemini Live API

---

## 🚀 Live Demo

**Production URL**: https://beatsuite-675304702130.us-central1.run.app

**Demo Credentials:**
- **Admin**: `admin` / `admin123` 
- **Nurse**: `nurse1` / `nurse123`
- **Family**: `family1` / `family123`

---

## ✨ Key Features

### 🎙️ **Gemini Live Voice Chat** *(NEW)*
- **Real-time voice conversation** with Gemini 2.0 Flash
- **Natural speech interface** - just speak naturally about patient care
- **WebSocket audio streaming** with 16kHz PCM encoding
- **Aoede voice** - empathetic healthcare-optimized AI voice
- **Live transcription** of conversations
- **Healthcare context** - AI understands patient vitals and room status

### 🤖 **AI Environment Control**
- **Automatic lighting adjustment** based on sleep stages and pain detection
- **Therapeutic music selection** with binaural beats and healing frequencies
- **Circadian rhythm support** with color temperature optimization
- **Pain management** through red light therapy and 432Hz healing sounds

### 📊 **Real-time Monitoring** 
- **Smartwatch integration** (heart rate, SpO2, movement, temperature)
- **Sleep stage detection** (deep sleep, REM, light sleep, awake)
- **Pain indicator analysis** through physiological markers
- **Live vital signs dashboard** with trend analysis

### 🎛️ **Smart Device Control**
- **IoT simulator** for lights and audio (ready for Philips Hue, Sonos)
- **Google Home integration** with voice commands
- **Manual override system** for healthcare staff
- **Room environment optimization**

---

## 📖 Documentation

### 📚 **Complete Guide**
👉 **[READ THE COMPLETE GUIDE](docs/COMPLETE_GUIDE.md)** 👈

All comprehensive documentation in one place:
- [Quick Start (5 min setup)](docs/COMPLETE_GUIDE.md#quick-start-guide)
- [Gemini Live Voice Chat Setup](docs/COMPLETE_GUIDE.md#gemini-live-voice-chat)
- [AI Auto-Control System](docs/COMPLETE_GUIDE.md#ai-auto-control-system)
- [API Reference](docs/COMPLETE_GUIDE.md#api-reference)

### 🔧 **Technical Docs**
- **[AI Environment Control](AI_ENVIRONMENT_CONTROL.md)** - Deep dive into how AI controls lights & music
- **[Deployment Guide](DEPLOYMENT.md)** - Git workflow and GCP deployment instructions

---

## 🏃‍♂️ Quick Start

### Prerequisites
```bash
# Required
python3 --version  # 3.8+
git --version

# Get Google API Key
# Visit: https://ai.google.dev/gemini-api/docs/api-key
```

### Installation (5 minutes)
```bash
# 1. Clone repository
git clone https://github.com/apkirana/beatsuite-ai.git
cd beatsuite-ai

# 2. Setup environment
echo "GOOGLE_API_KEY=your_actual_api_key_here" > .env

# 3. Start server (auto-creates venv, installs deps)
./app start

# 4. Open browser
open http://localhost:5001
```

### First Steps
1. **Login**: Use `admin` / `admin123`
2. **View Dashboard**: See patient rooms with real-time vitals
3. **Try AI Assistant**: Click any room → AI Assistant button
4. **Test Gemini Live**: Click "Start Voice Chat" → Grant mic permission → Speak naturally!
5. **Example Questions**: 
   - *"How is the patient doing?"*
   - *"What's their heart rate?"*
   - *"Should I adjust the room lighting?"*

---

## 🛠️ Tech Stack

### Core Technologies
- **Backend**: Python Flask + Google Gemini 2.5 Flash
- **Frontend**: Vanilla JavaScript + CSS3 Glassmorphism
- **AI**: Gemini API for analysis + Gemini Live for voice
- **Storage**: JSON files (easily migrated to PostgreSQL)
- **Voice**: WebSocket + Web Audio API
- **Deployment**: Docker + Google Cloud Run

### AI Capabilities
- **Gemini 2.0 Flash Experimental** for real-time voice
- **Advanced prompt engineering** for medical context
- **Real-time audio processing** at 16kHz sample rate  
- **Healthcare-optimized system instructions**
- **Pain detection algorithms** via physiological analysis
- **Circadian rhythm synchronization**

---

## 🌟 Latest Updates (November 2025)

### 🎙️ Gemini Live Integration
- **Real-time voice chat** with patients and healthcare staff
- **WebSocket streaming** for low-latency conversation
- **Medical context awareness** - AI knows patient status
- **Natural conversation flow** with interruption handling
- **Healthcare-optimized prompts** for empathetic responses

### 🎨 UI/UX Improvements  
- **Modern glassmorphism design** with 2025 healthcare aesthetics
- **Responsive mobile interface** for tablets and phones
- **Smooth animations** and micro-interactions
- **Accessibility features** for healthcare professionals
- **Dark mode support** for night shifts

### 🔧 Technical Enhancements
- **Environment variable auto-loading** in startup script
- **Improved error handling** with detailed logging
- **Performance optimizations** for real-time features  
- **Security hardening** for production deployment
- **Docker containerization** with multi-stage builds

---

## 🎯 Use Cases

### For Nurses
- **Quick patient status checks** via voice: *"How is room 101?"*
- **Environment adjustments**: *"Dim the lights in room 102"*
- **Pain monitoring**: Get alerts when AI detects discomfort
- **Handoff reports**: AI generates comprehensive summaries

### For Doctors  
- **Rapid assessments** during rounds with voice queries
- **Trend analysis** of patient vitals over time
- **Treatment recommendations** based on AI analysis
- **Documentation assistance** with AI-generated notes

### For Family Members
- **Comfort status updates**: *"Is mom sleeping well?"*
- **Simple explanations** of medical readings
- **Visiting recommendations**: Best times based on sleep patterns
- **Peace of mind** through 24/7 AI monitoring

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  🏥 Beat Suite AI System Architecture (2025)           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ⌚ Smartwatch  →  🤖 AI Engine  →  💡🎵 Environment    │
│     (Vitals)       (Analysis)        (Control)         │
│                                                         │
│  📱 Voice Chat  →  🎙️ Gemini Live  →  🔊 Response      │
│     (Speech)       (Real-time)        (Audio)          │ 
│                                                         │
│  🏥 Dashboard   →  📊 Analytics   →  👩‍⚕️ Alerts        │
│     (Interface)    (Trends)          (Staff)           │
└─────────────────────────────────────────────────────────┘

Components:
├─ Frontend: Vanilla JS + CSS3 + WebSocket
├─ Backend: Flask + Gemini AI + IoT Control  
├─ Voice: Gemini Live API + Web Audio
├─ Storage: JSON → PostgreSQL ready
└─ Deploy: Docker + GCP Cloud Run
```

---

## 📊 System Capabilities

### AI Analysis
- **Sleep Stage Detection**: Deep, REM, Light Sleep, Awake
- **Pain Indicators**: Heart rate spikes, movement patterns  
- **Circadian Alignment**: Morning blue light, evening amber
- **Environmental Optimization**: Auto-adjust for healing

### Voice Intelligence  
- **Natural Conversation**: Speak as you would to a colleague
- **Medical Context**: AI knows patient history and current state
- **Real-time Processing**: Sub-second response times
- **Healthcare Terminology**: Understands medical language

### Smart Environment
- **Therapeutic Lighting**: Color therapy, circadian support
- **Healing Audio**: Binaural beats, nature sounds, 432Hz frequencies  
- **Automated Control**: Based on sleep stages and pain detection
- **Manual Override**: Staff can take control when needed

---

## 🔗 Resources

### Development
- **Repository**: https://github.com/apkirana/beatsuite-ai
- **Issues**: https://github.com/apkirana/beatsuite-ai/issues  
- **Contributions**: See [CONTRIBUTING.md](docs/CONTRIBUTING.md)

### Documentation
- **Complete Guide**: [docs/COMPLETE_GUIDE.md](docs/COMPLETE_GUIDE.md)
- **API Reference**: [docs/API.md](docs/API.md) 
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)

### External APIs
- **Gemini AI**: https://ai.google.dev/gemini-api
- **Gemini Live**: https://ai.google.dev/gemini-api/docs/live
- **Google Cloud**: https://cloud.google.com/run

---

## 📈 Roadmap 

### Phase 1 ✅ (Completed)
- [x] Core patient monitoring system
- [x] AI environment control  
- [x] Google Home integration
- [x] IoT device simulation
- [x] Gemini Live voice chat

### Phase 2 🚧 (In Progress) 
- [ ] Advanced analytics dashboard
- [ ] Mobile app (iOS/Android)
- [ ] Multi-hospital deployment
- [ ] Electronic Health Record (EHR) integration

### Phase 3 🔮 (Planned)
- [ ] Predictive health analytics
- [ ] VR/AR therapy environments  
- [ ] Wearable device integration (Apple Watch, Oura)
- [ ] Regulatory compliance (HIPAA, FDA)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🤝 Support

**Need Help?**
- 📧 Email: support@beatsuite.ai
- 💬 Discord: [Beat Suite Community](https://discord.gg/beatsuite)
- 📖 Docs: [Complete Guide](docs/COMPLETE_GUIDE.md)

**Found a Bug?**
- 🐛 Report: [GitHub Issues](https://github.com/apkirana/beatsuite-ai/issues)
- 🔧 Fix: Submit a Pull Request

---

**Built with ❤️ for Healthcare Professionals**

*Beat Suite AI - Revolutionizing Patient Care Through Intelligent Monitoring*

---

## 🚀 What Can You Do?

### 1. Monitor Patients (Dashboard)
```
http://localhost:5001/dashboard
```

### 2. Simulate IoT Devices (Web Interface)
```
http://localhost:5001/iot-simulator
```

### 3. Control with Voice (Google Home)
```
"Hey Google, check room 101"
```

### 4. Test APIs (Programmatic)
```bash
python3 demo_iot_simulation.py
```

---

## 💡 Need Help?

1. **Read**: [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) - Answers 99% of questions
2. **Run**: `python3 demo_iot_simulation.py` - See it in action
3. **Test**: `./test_google_home.sh` - Verify everything works
4. **Ask**: Create GitHub issue if stuck

---

## 📊 Quick Status Check

```bash
# Is everything working?
curl http://localhost:5001/api/health

# Generate demo data
python3 demo_iot_simulation.py

# Test Google Home
./test_google_home.sh
```

---

**🎉 Start reading: [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)**
