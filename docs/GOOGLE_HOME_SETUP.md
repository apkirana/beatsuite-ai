# 🏠 Google Home / Google Assistant Integration Guide

Complete guide to integrate Beat Suite AI with Google Home using Actions Console Playground.

---

## 📋 Table of Contents
1. [Setup Overview](#setup-overview)
2. [Prerequisites](#prerequisites)
3. [Backend Setup](#backend-setup)
4. [Google Actions Console Setup](#google-actions-console-setup)
5. [Testing in Playground](#testing-in-playground)
6. [Voice Commands](#voice-commands)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Setup Overview

Your Beat Suite AI system now has a **Google Home fulfillment webhook** that allows you to control:
- 💡 Room lighting (color, brightness)
- 🎵 Room music (volume, play/stop)
- 👤 Patient vitals checking
- 🤖 AI control (enable/disable)
- 🏥 Room status monitoring

---

## ✅ Prerequisites

1. **Ngrok or Public URL** (for local development)
   ```bash
   brew install ngrok  # macOS
   # or download from https://ngrok.com
   ```

2. **Google Account** with access to:
   - [Google Actions Console](https://console.actions.google.com)

3. **Running Beat Suite AI Backend**
   ```bash
   cd /Users/puspa.kirana/Documents/GitHub/hqgoogle
   python run.py
   ```

---

## 🔧 Backend Setup

### Step 1: Start Your Backend Server

```bash
cd /Users/puspa.kirana/Documents/GitHub/hqgoogle
python run.py
```

Your server should be running on `http://localhost:5001`

### Step 2: Create Public URL with Ngrok

In a new terminal:

```bash
ngrok http 5001
```

You'll see output like:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:5001
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`) - you'll need this for Google Actions Console.

### Step 3: Test the Webhook Endpoint

```bash
# Test health check
curl https://YOUR-NGROK-URL.ngrok.io/api/google-home/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "Google Home Integration",
  "version": "1.0"
}
```

---

## 🎮 Google Actions Console Setup

### Step 1: Create New Action

1. Go to [Google Actions Console](https://console.actions.google.com)
2. Click **"New project"**
3. Name: **"Beat Suite AI"**
4. Click **Create project**

### Step 2: Choose Action Type

1. Select **"Custom"** (for custom conversational actions)
2. Click **"Next"**

### Step 3: Set Up Invocation

1. In the left sidebar, click **"Invocation"**
2. **Display Name**: `Beat Suite AI`
3. **Voice**: Choose your preferred voice
4. Click **"Save"**

### Step 4: Create Intents

#### Intent 1: Get Room Status

1. In left sidebar, click **"Actions"** → **"Add Action"**
2. Click **"Get Started"** on Custom Intent
3. Click **"Add Intent"**

**Intent Name**: `GetRoomStatus`

**Training Phrases** (add these):
```
Check room 101
What's the status of room 201
Tell me about room 303
How is the patient in room 102
Room 105 status
```

**Parameters**:
- Name: `room_number`
- Entity Type: `@sys.number`

#### Intent 2: Control Light

**Intent Name**: `ControlLight`

**Training Phrases**:
```
Turn on the lights in room 101
Turn off lights in room 202
Dim the lights in room 303
Brighten room 104
Set room 105 lights to 50%
Make room 106 lights blue
Set room 107 to warm white
```

**Parameters**:
- Name: `room_number`, Entity: `@sys.number`
- Name: `action`, Entity: `@sys.any` (on, off, dim, brighten)
- Name: `brightness`, Entity: `@sys.number`
- Name: `color`, Entity: `@sys.color`

#### Intent 3: Control Music

**Intent Name**: `ControlMusic`

**Training Phrases**:
```
Play music in room 101
Stop music in room 202
Turn up the volume in room 303
Lower the music in room 104
Set room 105 music to 30%
Play calming music in room 106
```

**Parameters**:
- Name: `room_number`, Entity: `@sys.number`
- Name: `action`, Entity: `@sys.any` (play, stop, louder, softer)
- Name: `volume`, Entity: `@sys.number`

#### Intent 4: Get Patient Vitals

**Intent Name**: `GetPatientVitals`

**Training Phrases**:
```
What are the vitals for room 101
Check patient vitals in room 202
Tell me the heart rate for room 303
How is the patient in room 104 doing
Give me vital signs for room 105
```

**Parameters**:
- Name: `room_number`, Entity: `@sys.number`

#### Intent 5: Enable AI

**Intent Name**: `EnableAI`

**Training Phrases**:
```
Enable AI for room 101
Turn on automatic control in room 202
Activate AI in room 303
Start AI monitoring for room 104
```

**Parameters**:
- Name: `room_number`, Entity: `@sys.number`

#### Intent 6: Disable AI

**Intent Name**: `DisableAI`

**Training Phrases**:
```
Disable AI for room 101
Turn off automatic control in room 202
Deactivate AI in room 303
Stop AI monitoring for room 104
Manual mode for room 105
```

**Parameters**:
- Name: `room_number`, Entity: `@sys.number`

### Step 5: Configure Webhook Fulfillment

1. In left sidebar, click **"Webhook"**
2. Enter your **Ngrok HTTPS URL**:
   ```
   https://YOUR-NGROK-URL.ngrok.io/api/google-home/fulfillment
   ```
3. Click **"Save"**

### Step 6: Enable Fulfillment for All Intents

For **each intent** you created:
1. Open the intent
2. Scroll down to **"Fulfillment"**
3. Toggle **"Enable webhook call for this intent"**
4. Click **"Save"**

---

## 🧪 Testing in Playground

### Step 1: Open Test Console

1. In Google Actions Console, click **"Test"** in top-right corner
2. Or click **"Simulator"** in left sidebar

### Step 2: Test Commands

Type or say these commands:

#### Test Room Status
```
Talk to Beat Suite AI
→ "Check room 101"

Expected Response:
"Room 101, patient Emma Johnson. Heart rate: 72 BPM, Temperature: 36.8 degrees, Oxygen: 98%, Sleep stage: Light sleep. AI control is active."
```

#### Test Light Control
```
Talk to Beat Suite AI
→ "Turn on lights in room 101"

Expected Response:
"Room 101 lights on."
```

```
→ "Set room 101 lights to blue at 70%"

Expected Response:
"Room 101 lights. Brightness set to 70%. Color set to blue."
```

#### Test Music Control
```
Talk to Beat Suite AI
→ "Play music in room 201"

Expected Response:
"Room 201 music play."
```

```
→ "Set room 201 volume to 40%"

Expected Response:
"Room 201 music. Volume set to 40%."
```

#### Test Patient Vitals
```
Talk to Beat Suite AI
→ "What are the vitals for room 303"

Expected Response:
"Michael Davis in room 303: Heart rate 65 BPM, Temperature 36.5 degrees Celsius, Respiratory rate 14 breaths per minute, Oxygen saturation 99%, Blood pressure 118/76."
```

#### Test AI Control
```
Talk to Beat Suite AI
→ "Enable AI for room 101"

Expected Response:
"AI control enabled for room 101. The system will now automatically adjust lighting and music based on patient needs."
```

```
→ "Disable AI for room 101"

Expected Response:
"AI control disabled for room 101. You can now manually control the environment."
```

---

## 🎤 Voice Commands Cheat Sheet

### Room Status & Vitals
- `"Check room [number]"`
- `"What's the status of room [number]"`
- `"Tell me the vitals for room [number]"`
- `"How is the patient in room [number]"`

### Light Control
- `"Turn on/off lights in room [number]"`
- `"Dim/brighten room [number]"`
- `"Set room [number] to [color]"`
- `"Make room [number] lights [blue/warm/cool/white]"`
- `"Set room [number] brightness to [0-100]%"`

### Music Control
- `"Play/stop music in room [number]"`
- `"Turn up/down volume in room [number]"`
- `"Set room [number] music to [0-100]%"`
- `"Louder/softer in room [number]"`

### AI Management
- `"Enable AI for room [number]"`
- `"Disable AI for room [number]"`
- `"Turn on/off automatic control in room [number]"`

---

## 🐛 Troubleshooting

### Issue: "Webhook error"

**Solution**:
1. Check ngrok is running: `ngrok http 5001`
2. Verify backend is running: `python run.py`
3. Test webhook directly:
   ```bash
   curl -X POST https://YOUR-NGROK-URL.ngrok.io/api/google-home/fulfillment \
     -H "Content-Type: application/json" \
     -d '{"queryResult":{"intent":{"displayName":"GetRoomStatus"},"parameters":{"room_number":101}}}'
   ```

### Issue: "Room not found"

**Solution**:
- Your system uses room IDs like `room-101`, `room-201`, etc.
- Check existing rooms:
  ```bash
  curl http://localhost:5001/api/rooms
  ```

### Issue: "Ngrok URL keeps changing"

**Solution**:
- Free ngrok URLs change on restart
- Either:
  - Pay for ngrok Pro (permanent URLs)
  - Or update webhook URL in Google Actions Console each time

### Issue: "Intent not recognized"

**Solution**:
1. Add more training phrases in Google Actions Console
2. Use exact room numbers that exist in your system
3. Check intent fulfillment is enabled

### Issue: "No response from Assistant"

**Solution**:
1. Check backend logs: Look for errors in terminal running `python run.py`
2. Check ngrok logs: Look at ngrok web interface `http://localhost:4040`
3. Verify JSON format in webhook response

---

## 📊 API Endpoint Reference

### Fulfillment Webhook
```
POST /api/google-home/fulfillment
Content-Type: application/json

{
  "queryResult": {
    "intent": {
      "displayName": "IntentName"
    },
    "parameters": {
      "room_number": 101,
      "action": "on",
      "brightness": 70,
      "color": "blue"
    }
  }
}
```

### Health Check
```
GET /api/google-home/health

Response:
{
  "status": "healthy",
  "service": "Google Home Integration",
  "version": "1.0"
}
```

---

## 🚀 Production Deployment

### For Production Use:

1. **Deploy backend to cloud** (not localhost):
   - Heroku: `heroku create beatsuite-ai`
   - Google Cloud Run
   - AWS Lambda
   - Or any hosting service

2. **Use production URL** instead of ngrok:
   ```
   https://beatsuite-ai.herokuapp.com/api/google-home/fulfillment
   ```

3. **Add authentication** (recommended):
   - API keys
   - OAuth tokens
   - IP whitelisting

4. **Enable HTTPS** (required by Google):
   - Use Let's Encrypt
   - Or cloud provider's SSL

---

## 📝 Example Conversation Flow

```
You: "Hey Google, talk to Beat Suite AI"
Google: "Sure, getting the test version of Beat Suite AI"

You: "Check room 101"
Assistant: "Room 101, patient Emma Johnson. Heart rate: 72 BPM, 
            Temperature: 36.8 degrees, Oxygen: 98%, Sleep stage: Light sleep. 
            AI control is active."

You: "Turn off the lights"
Assistant: "Which room would you like to control?"

You: "Room 101"
Assistant: "Room 101 lights off."

You: "Enable AI"
Assistant: "Which room should have AI control enabled?"

You: "Room 101"
Assistant: "AI control enabled for room 101. The system will now 
            automatically adjust lighting and music based on patient needs."

You: "Thank you"
Google: "You're welcome!"
```

---

## 🎯 Next Steps

1. **Test all intents** in Google Actions Playground
2. **Add more training phrases** for better recognition
3. **Customize responses** in `google_home_routes.py`
4. **Add authentication** for production
5. **Deploy to production** server
6. **Submit for review** (optional, if you want public access)

---

## 📚 Additional Resources

- [Google Actions Console](https://console.actions.google.com)
- [Actions SDK Documentation](https://developers.google.com/assistant/conversational)
- [Dialogflow Documentation](https://cloud.google.com/dialogflow/docs)
- [Ngrok Documentation](https://ngrok.com/docs)

---

**Happy testing! 🎉**

For questions or issues, check the backend logs or ngrok inspection interface at `http://localhost:4040`
