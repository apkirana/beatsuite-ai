#!/usr/bin/env python3
"""
Test External Audio API Integration
Demonstrates how to use different external audio APIs
"""

import os
from backend.core.iot_controller import IoTDeviceManager

def test_spotify_integration():
    """Test Spotify Web API integration"""
    print("🎵 Testing Spotify Integration")
    print("=" * 40)
    
    # Initialize with Spotify
    iot_manager = IoTDeviceManager(audio_type='spotify')
    
    # Test settings
    spotify_settings = {
        'music': {
            'playlist_id': '37i9dQZF1DWS6vxNPVqrmG',  # Example Spotify playlist ID
            'volume': 0.3
        }
    }
    
    result = iot_manager.apply_environment_settings('room_101', spotify_settings)
    print(f"Spotify test result: {'✅ Success' if result else '❌ Failed'}")
    
    state = iot_manager.get_current_state('room_101')
    if state['audio']:
        print(f"Current state: {state['audio']}")
    print()

def test_youtube_music_integration():
    """Test YouTube Music API integration"""
    print("🎬 Testing YouTube Music Integration")
    print("=" * 40)
    
    # Initialize with YouTube Music
    iot_manager = IoTDeviceManager(audio_type='youtube_music')
    
    # Test settings
    youtube_settings = {
        'music': {
            'playlist_id': 'PLrAD5BHsKGOhVH6I2XnN3Q',  # Example YouTube playlist ID
            'volume': 0.25
        }
    }
    
    result = iot_manager.apply_environment_settings('room_102', youtube_settings)
    print(f"YouTube Music test result: {'✅ Success' if result else '❌ Failed'}")
    
    state = iot_manager.get_current_state('room_102')
    if state['audio']:
        print(f"Current state: {state['audio']}")
    print()

def test_custom_api_integration():
    """Test Custom Audio API integration"""
    print("🔧 Testing Custom Audio API Integration")
    print("=" * 40)
    
    # Initialize with Custom API
    iot_manager = IoTDeviceManager(audio_type='custom_api')
    
    # Test settings
    custom_settings = {
        'music': {
            'playlist_id': 'healthcare_sleep_therapy_v2',
            'volume': 0.2
        }
    }
    
    result = iot_manager.apply_environment_settings('room_103', custom_settings)
    print(f"Custom API test result: {'✅ Success' if result else '❌ Failed'}")
    
    state = iot_manager.get_current_state('room_103')
    if state['audio']:
        print(f"Current state: {state['audio']}")
    print()

def show_configuration_guide():
    """Show configuration guide for external APIs"""
    print("📋 External Audio API Configuration Guide")
    print("=" * 50)
    print()
    
    print("🎵 SPOTIFY SETUP:")
    print("1. Go to https://developer.spotify.com/dashboard")
    print("2. Create an app and get your Client ID/Secret")
    print("3. Use OAuth 2.0 to get access token")
    print("4. Set environment variables:")
    print("   export SPOTIFY_ACCESS_TOKEN='your_token_here'")
    print("   export SPOTIFY_DEFAULT_DEVICE='device_id_here'")
    print()
    
    print("🎬 YOUTUBE MUSIC SETUP:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Enable YouTube Data API v3")
    print("3. Create API key")
    print("4. Set environment variable:")
    print("   export YOUTUBE_API_KEY='your_api_key_here'")
    print()
    
    print("🔧 CUSTOM API SETUP:")
    print("1. Set up your healthcare audio service")
    print("2. Get API token from your service provider")
    print("3. Set environment variables:")
    print("   export CUSTOM_AUDIO_API_URL='https://your-api.com/v1'")
    print("   export CUSTOM_AUDIO_API_TOKEN='your_token_here'")
    print()
    
    print("📁 Create .env file from .env.example for easier configuration")
    print()

def main():
    """Main test execution"""
    print("🚀 External Audio API Integration Test")
    print("=" * 50)
    print()
    
    show_configuration_guide()
    
    # Check if environment variables are set
    spotify_token = os.getenv('SPOTIFY_ACCESS_TOKEN')
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    custom_token = os.getenv('CUSTOM_AUDIO_API_TOKEN')
    
    print("🔍 Environment Check:")
    print(f"Spotify Token: {'✅ Set' if spotify_token else '❌ Not set'}")
    print(f"YouTube API Key: {'✅ Set' if youtube_key else '❌ Not set'}")
    print(f"Custom API Token: {'✅ Set' if custom_token else '❌ Not set'}")
    print()
    
    # Run tests (will work in simulation mode if credentials not set)
    if spotify_token:
        test_spotify_integration()
    else:
        print("⚠️ Skipping Spotify test - no access token configured")
        print()
    
    if youtube_key:
        test_youtube_music_integration()
    else:
        print("⚠️ Skipping YouTube Music test - no API key configured")
        print()
    
    if custom_token:
        test_custom_api_integration()
    else:
        print("⚠️ Skipping Custom API test - no token configured")
        print()
    
    print("💡 To test with real APIs, configure credentials in .env file")
    print("💡 See .env.example for required environment variables")

if __name__ == "__main__":
    main()