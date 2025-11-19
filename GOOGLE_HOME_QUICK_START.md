# 🎤 Google Home Quick Start Guide

## Quick Setup (5 minutes)

### 1. Start Backend + Ngrok

```bash
# Terminal 1: Start backend
cd /Users/puspa.kirana/Documents/GitHub/hqgoogle
python run.py

# Terminal 2: Expose with ngrok
ngrok http 5001
# Copy the https URL (e.g., https://abc123.ngrok.io)
```

### 2. Configure Google Actions Console

1. Go to: https://console.actions.google.com
2. Create project → Choose "Custom" → Name: "Beat Suite AI"
3. Click "Webhook" → Enter: `https://YOUR-NGROK-URL.ngrok.io/api/google-home/fulfillment`
4. Create these intents (copy from GOOGLE_HOME_SETUP.md)

### 3. Test in Playground

```
"Talk to Beat Suite AI"
"Check room 101"
"Turn on lights in room 102"
"Play music in room 201"
```

## Available Commands

### 📊 Room Status
- "Check room 101"
- "What's the status of room 102"
- "How is room 201"

### 💡 Lights
- "Turn on/off lights in room 101"
- "Set room 102 to blue"
- "Brighten room 103"
- "Set room 104 to 70%"

### 🎵 Music
- "Play music in room 201"
- "Stop music in room 202"
- "Set room 203 volume to 40%"
- "Louder in room 204"

### 👤 Patient Info
- "What are the vitals for room 101"
- "Check patient in room 102"

### 🤖 AI Control
- "Enable AI for room 101"
- "Disable AI for room 102"

## Test Webhook Locally

```bash
# Run test script
./test_google_home.sh

# Or manual test
curl http://localhost:5001/api/google-home/health
```

## Existing Rooms

- Room 101 (Alex Thompson - P001)
- Room 102 (Maria Garcia - P002)
- Room 103 (Michael Davis - P003)
- Room 201, 202, 203, 204, 205

## Full Documentation

See: `docs/GOOGLE_HOME_SETUP.md`
