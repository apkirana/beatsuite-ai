#!/usr/bin/env python3
"""
Demo: Simulate IoT Devices Without External Apps
Shows how Beat Suite AI already has everything you need for testing!
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5001"

print("=" * 60)
print("🏥 Beat Suite AI - Built-in IoT Simulation Demo")
print("=" * 60)
print()

# Login first (required for API access)
print("🔐 Step 1: Login...")
session = requests.Session()
login_response = session.post(f"{BASE_URL}/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})

if login_response.status_code == 200:
    print("✅ Logged in successfully!")
else:
    print("❌ Login failed. Make sure server is running.")
    exit(1)

print()

# Get all rooms
print("📋 Step 2: Get all rooms...")
rooms_response = session.get(f"{BASE_URL}/api/rooms")
rooms_data = rooms_response.json()

if 'rooms' in rooms_data:
    print(f"✅ Found {len(rooms_data['rooms'])} rooms")
    for room in rooms_data['rooms'][:3]:
        print(f"   - {room['room_id']}: {room['patient_name']}")
else:
    print("❌ Could not fetch rooms")
    exit(1)

print()

# Generate synthetic smartwatch data
print("⌚ Step 3: Generate synthetic smartwatch data...")
patient_id = "P001"
synthetic_response = session.get(f"{BASE_URL}/api/test/synthetic-data/{patient_id}")
synthetic_data = synthetic_response.json()

if synthetic_response.status_code == 200:
    print("✅ Generated realistic patient vitals:")
    print(f"   💓 Heart Rate: {synthetic_data.get('heart_rate')} BPM")
    print(f"   🌡️  Temperature: {synthetic_data.get('temperature')}°C")
    print(f"   🫁 SpO2: {synthetic_data.get('spo2')}%")
    print(f"   😴 Sleep Stage: {synthetic_data.get('sleep_stage')}")
else:
    print("⚠️  Synthetic data endpoint may require authentication")

print()

# Simulate AI adjustment
print("🤖 Step 4: Run AI simulation...")
ai_sim_response = session.post(f"{BASE_URL}/api/test/simulate-ai-adjustment/{patient_id}")

if ai_sim_response.status_code == 200:
    ai_data = ai_sim_response.json()
    print("✅ AI processed patient data:")
    
    if 'environment_adjustments' in ai_data:
        light = ai_data['environment_adjustments'].get('light', {})
        music = ai_data['environment_adjustments'].get('music', {})
        
        print(f"   💡 Light Color: {light.get('color_hex')} at {int(light.get('brightness', 0)*100)}%")
        print(f"   🎵 Music Volume: {int(music.get('volume', 0)*100)}%")
        print(f"   📝 AI Reasoning: {ai_data.get('ai_reasoning', 'N/A')[:60]}...")
else:
    print("⚠️  AI simulation requires admin role")

print()

# Get room details with live data
print("📊 Step 5: Get room with live IoT status...")
room_id = "room_101"
room_response = session.get(f"{BASE_URL}/api/rooms/{room_id}")

if room_response.status_code == 200:
    room_data = room_response.json()
    print(f"✅ Room {room_id} status:")
    print(f"   👤 Patient: {room_data.get('patient_name')}")
    print(f"   💓 Heart Rate: {room_data.get('heart_rate')} BPM")
    print(f"   🤖 AI Active: {room_data.get('ai_is_active')}")
    
    if 'current_ai_settings' in room_data:
        settings = room_data['current_ai_settings']
        print(f"   💡 Current Light: {settings.get('light_hex_color')} @ {int(settings.get('light_brightness', 0)*100)}%")
        print(f"   🎵 Current Volume: {int(settings.get('music_volume', 0)*100)}%")
else:
    print(f"⚠️  Could not fetch room data")

print()

# Control light manually (simulate smart bulb)
print("💡 Step 6: Control smart light (simulated)...")
override_response = session.post(f"{BASE_URL}/api/rooms/{room_id}/override", json={
    "brightness": 80,
    "volume": 40,
    "hex_color": "#4A90E2"  # Blue
})

if override_response.status_code == 200:
    print("✅ Light changed to blue at 80%")
    print("   (Check http://localhost:5001/iot-simulator to see visual change)")
else:
    print("⚠️  Manual control requires admin/nurse role")

print()

# Resume AI control
print("🤖 Step 7: Resume AI automatic control...")
resume_response = session.post(f"{BASE_URL}/api/rooms/{room_id}/resume")

if resume_response.status_code == 200:
    print("✅ AI control resumed - system will auto-adjust based on patient needs")
else:
    print("⚠️  Resume requires admin/nurse role")

print()
print("=" * 60)
print("✨ Demo Complete!")
print("=" * 60)
print()
print("📱 What You Can Do Next:")
print("1. Open http://localhost:5001/iot-simulator in browser")
print("2. Watch lights and music change in real-time")
print("3. Use Google Home: 'Check room 101'")
print("4. Monitor AI decisions in the web interface")
print()
print("🎮 You don't need external apps - everything is built-in!")
print("=" * 60)
