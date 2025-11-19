# 🏥 Beat Suite AI Dashboard

A production-ready web-based dashboard for nurses and parents to monitor AI-controlled room environments and manually override settings in real-time.

## 🎯 Features

### Core AI System
- **Smartwatch Integration**: Real-time physiological data (HR, movement, SpO2)
- **AI Feedback Loop**: Continuous analysis and environment adjustment
- **Sleep Stage Detection**: Deep sleep, light sleep, REM, awake states
- **Pain Detection**: Identifies discomfort from HR spikes and movement
- **Circadian Alignment**: Adjusts lighting based on time of day
- **Adaptive Lighting**: Color temperature 1800K-6500K for different states
- **Therapeutic Music**: Binaural beats, healing frequencies, ambient playlists

### Dashboard & Control
- **Real-time Monitoring**: Live AI decision tracking
- **Manual Override**: Nurses can pause AI and adjust settings
- **Patient Vitals**: Heart rate, oxygen, sleep stage display
- **AI Reasoning**: Explains every environmental decision
- **Nurse Assistant Chat**: Quick answers about patient state
- **Responsive Design**: Works on desktop, tablet, mobile

## 🛠️ Technology Stack

- **Backend**: Python 3.x with Flask
- **AI Engine**: NumPy-based physiological analysis
- **Smartwatch Integration**: Simulated (ready for HealthKit, Google Fit, Fitbit)
- **IoT Control**: Ready for Philips Hue, LIFX, Sonos integration
- **Frontend**: Vanilla JavaScript with real-time updates
- **API**: RESTful JSON endpoints with WebSocket-ready architecture
- **Styling**: Custom CSS with gradient themes

## 📁 Project Structure

```
hqgoogle/
├── app.py                        # Main Flask application with AI integration
├── config.py                    # Environment configuration
├── ai_engine.py                 # Core AI decision-making engine
├── smartwatch_integration.py    # Wearable device data collection
├── iot_controller.py            # Smart light/audio control
├── requirements.txt             # Python dependencies
├── start.sh                     # Quick startup script
├── README.md                    # This file
├── .venv/                       # Virtual environment (not in git)
├── templates/
│   └── index.html              # Dashboard UI with live updates
└── static/
    └── styles.css              # Additional styling
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create and activate virtual environment (if not already done)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Run the Application

```bash
# Development mode (with auto-reload)
python app.py

# Or with Flask CLI
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

### 3. Access the Dashboard

Open your browser and navigate to:
```
http://localhost:5000
```

## 🔧 Configuration

The application uses `config.py` for environment-specific settings:

- **Development**: Auto-reload, debug mode, verbose logging
- **Production**: Optimized for deployment, requires environment variables
- **Testing**: Test-specific configurations

### Environment Variables

Create a `.env` file (not tracked in git) for sensitive configuration:

```bash
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
PORT=5000

# For production with Firestore
FIRESTORE_PROJECT_ID=your-project-id
FIRESTORE_CREDENTIALS=path/to/credentials.json
```

## 📡 API Endpoints

### Health Check
```
GET /api/health
```

### Get Room Data
```
GET /api/get_room_data/<room_id>
```

### Get All Rooms
```
GET /api/rooms
```

### Set Manual Override
```
POST /api/set_override/<room_id>
Body: {"brightness": 0.5, "volume": 0.3}
```

### Resume AI Control
```
POST /api/resume_ai/<room_id>
```

### Chat with Assistant
```
POST /api/chat
Body: {"message": "What is the patient's heart rate?"}
```

### Debug Room Data
```
GET /api/debug/rooms
```

## 🧪 Testing

Test API endpoints using curl or Postman:

```bash
# Health check
curl http://localhost:5000/api/health

# Get room data
curl http://localhost:5000/api/get_room_data/room_101

# Send chat message
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the current temperature?"}'
```

## 🔐 Security Features

- CORS protection with configurable origins
- Input validation on all API endpoints
- Secure session cookies (production)
- Error handling with proper HTTP status codes
- Logging for audit trails

## 📝 Development Notes

### Mock Data

The current implementation uses in-memory mock data (`mock_room_data` in `app.py`). In production, this should be replaced with:
- **Firestore**: For persistent patient and room data
- **Google Agent SDK**: For real AI assistant responses
- **IoT Integration**: For actual device control

### Future Enhancements

- [ ] Firestore database integration
- [ ] User authentication and authorization
- [ ] Multi-room management interface
- [ ] Historical data visualization
- [ ] Alert and notification system
- [ ] Mobile app version
- [ ] Real-time WebSocket updates

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find and kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

### Template Not Found

Ensure `templates/index.html` exists in the correct location relative to `app.py`.

### Import Errors

Reinstall dependencies:
```bash
pip install --upgrade -r requirements.txt
```

## 📄 License

This is a demonstration project for the Beat Suite AI healthcare system.

## 👥 Contributors

- **Developer**: Full-stack implementation
- **Project**: Beat Suite AI - NICU Environmental Control System

## 📞 Support

For issues or questions, please check the logs in the terminal where the Flask app is running.

---

**Note**: This is a demonstration application. Do not use in production healthcare environments without proper certification, security audits, and compliance verification.
