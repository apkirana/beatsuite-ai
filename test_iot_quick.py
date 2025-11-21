#!/usr/bin/env python3
"""
Quick IoT Test Script
Simple demonstration of IoT device functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.iot_controller import get_iot_device_manager, apply_ai_settings_to_room, get_room_device_state


def quick_iot_test():
    """Quick test of IoT functionality"""
    print("🔧 Quick IoT Device Test")
    print("=" * 30)
    
    # Get the IoT manager
    iot_manager = get_iot_device_manager()
    print(f"✅ IoT Manager initialized: {type(iot_manager).__name__}")
    
    # Test room
    room_id = "room_101"
    print(f"\n🏠 Testing room: {room_id}")
    
    # Test 1: Direct device control
    print("\n1️⃣ Testing direct device control:")
    
    # Control lights directly
    success = iot_manager.light_controller.set_color_and_brightness(
        room_id, "#FF6B6B", 0.7
    )
    print(f"   💡 Light control: {'✅ Success' if success else '❌ Failed'}")
    
    # Control audio directly
    success = iot_manager.audio_controller.play_playlist(
        room_id, "relaxing_music", 0.3
    )
    print(f"   🔊 Audio control: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 2: AI settings application
    print("\n2️⃣ Testing AI settings application:")
    
    ai_output = {
        'light': {
            'color_hex': '#4A90E2',
            'brightness': 0.5
        },
        'music': {
            'playlist_id': 'calm_ambient',
            'volume': 0.2
        },
        'ai_reasoning': 'Patient in light sleep, applying calm environment'
    }
    
    success = apply_ai_settings_to_room(room_id, ai_output)
    print(f"   🤖 AI settings: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 3: Get current state
    print("\n3️⃣ Getting current device state:")
    
    state = get_room_device_state(room_id)
    print(f"   📊 Current state retrieved:")
    
    if state['lights']:
        lights = state['lights']
        print(f"      💡 Lights: {lights.get('color', 'N/A')} at {lights.get('brightness', 0):.0%}")
    else:
        print(f"      💡 No light data")
    
    if state['audio']:
        audio = state['audio']
        print(f"      🔊 Audio: '{audio.get('playlist', 'N/A')}' at {audio.get('volume', 0):.0%}")
    else:
        print(f"      🔊 No audio data")
    
    print("\n✅ Quick test completed!")


if __name__ == "__main__":
    try:
        quick_iot_test()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()