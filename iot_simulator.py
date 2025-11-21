#!/usr/bin/env python3
"""
IoT Device Simulator
Simulates and tests IoT device functionality for the Beat Suite AI system
Demonstrates light and audio control across multiple patient rooms
"""

import time
import random
import logging
from typing import Dict, List
from backend.core.iot_controller import get_iot_device_manager, IoTDeviceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IoTSimulator:
    """
    Comprehensive IoT Device Simulator
    Tests and demonstrates IoT functionality
    """
    
    def __init__(self):
        self.iot_manager: IoTDeviceManager = get_iot_device_manager()
        self.rooms = ['room_101', 'room_102', 'room_103', 'room_104', 'room_105']
        self.patient_scenarios = {
            'room_101': {'name': 'Alex Thompson', 'condition': 'post-surgery'},
            'room_102': {'name': 'Maria Garcia', 'condition': 'diabetes'},
            'room_103': {'name': 'Sophie van Berg', 'condition': 'asthma'},
            'room_104': {'name': 'Liam Chen', 'condition': 'cardiac'},
            'room_105': {'name': 'Emma Johnson', 'condition': 'appendectomy'}
        }
        
    def simulate_patient_scenarios(self):
        """Simulate different patient scenarios with appropriate IoT responses"""
        print("\n🏥 IoT Simulator - Patient Scenario Testing")
        print("=" * 60)
        
        scenarios = [
            {
                'name': 'Deep Sleep Recovery',
                'settings': {
                    'light': {'color_hex': '#1a1a2e', 'brightness': 0.1},
                    'music': {'playlist_id': 'sleep_therapy', 'volume': 0.05}
                },
                'rooms': ['room_101', 'room_104']
            },
            {
                'name': 'Morning Wake-up',
                'settings': {
                    'light': {'color_hex': '#FFE4B5', 'brightness': 0.7},
                    'music': {'playlist_id': 'upbeat_morning', 'volume': 0.3}
                },
                'rooms': ['room_102', 'room_105']
            },
            {
                'name': 'Pain Management',
                'settings': {
                    'light': {'color_hex': '#FF6B6B', 'brightness': 0.4},
                    'music': {'playlist_id': 'healing_frequencies', 'volume': 0.2}
                },
                'rooms': ['room_103']
            },
            {
                'name': 'Relaxation Mode',
                'settings': {
                    'light': {'color_hex': '#4A90E2', 'brightness': 0.5},
                    'music': {'playlist_id': 'calm_ambient', 'volume': 0.25}
                },
                'rooms': ['room_104', 'room_105']
            }
        ]
        
        for scenario in scenarios:
            print(f"\n🎬 Scenario: {scenario['name']}")
            print("-" * 40)
            
            for room_id in scenario['rooms']:
                patient = self.patient_scenarios.get(room_id, {'name': 'Unknown'})
                print(f"\n   🏠 {room_id} - {patient['name']} ({patient.get('condition', 'N/A')})")
                
                success = self.iot_manager.apply_environment_settings(room_id, scenario['settings'])
                
                if success:
                    print(f"   ✅ IoT settings applied successfully")
                    # Get current state
                    state = self.iot_manager.get_current_state(room_id)
                    self._display_device_state(state)
                else:
                    print(f"   ❌ Failed to apply IoT settings")
                
                time.sleep(3)  # Longer delay for lamp changes demonstration
    
    def test_individual_devices(self):
        """Test individual device controllers"""
        print("\n🔧 IoT Simulator - Individual Device Testing")
        print("=" * 60)
        
        # Test Light Controller
        print("\n💡 Testing Light Controller")
        print("-" * 30)
        
        light_tests = [
            {'room': 'room_101', 'color': '#FF0000', 'brightness': 1.0, 'name': 'Bright Red'},
            {'room': 'room_102', 'color': '#00FF00', 'brightness': 0.6, 'name': 'Medium Green'},
            {'room': 'room_103', 'color': '#0000FF', 'brightness': 0.3, 'name': 'Dim Blue'},
            {'room': 'room_104', 'color': '#FFFF00', 'brightness': 0.8, 'name': 'Bright Yellow'},
            {'room': 'room_105', 'color': '#FF00FF', 'brightness': 0.4, 'name': 'Medium Magenta'}
        ]
        
        for test in light_tests:
            print(f"  🔆 {test['room']}: {test['name']} ({test['color']}, {test['brightness']:.0%})")
            success = self.iot_manager.light_controller.set_color_and_brightness(
                test['room'], test['color'], test['brightness']
            )
            print(f"     {'✅ Success' if success else '❌ Failed'}")
        
        # Test Audio Controller
        print("\n🔊 Testing Audio Controller")
        print("-" * 30)
        
        audio_tests = [
            {'room': 'room_101', 'playlist': 'deep_sleep_binaural', 'volume': 0.1},
            {'room': 'room_102', 'playlist': 'spanish_guitar_relaxing', 'volume': 0.3},
            {'room': 'room_103', 'playlist': 'children_lullabies', 'volume': 0.2},
            {'room': 'room_104', 'playlist': 'nature_sounds_forest', 'volume': 0.25},
            {'room': 'room_105', 'playlist': 'disney_instrumental', 'volume': 0.15}
        ]
        
        for test in audio_tests:
            print(f"  🎵 {test['room']}: '{test['playlist']}' at {test['volume']:.0%}")
            success = self.iot_manager.audio_controller.play_playlist(
                test['room'], test['playlist'], test['volume']
            )
            print(f"     {'✅ Success' if success else '❌ Failed'}")
    
    def simulate_ai_responses(self):
        """Simulate AI engine responses with realistic IoT commands"""
        print("\n🤖 IoT Simulator - AI Response Simulation")
        print("=" * 60)
        
        ai_scenarios = [
            {
                'patient_state': 'Patient showing signs of restlessness, elevated heart rate',
                'ai_output': {
                    'light': {'color_hex': '#8A2BE2', 'brightness': 0.3},
                    'music': {'playlist_id': 'calm_meditation', 'volume': 0.2},
                    'ai_reasoning': 'Applying calming environment to reduce anxiety'
                }
            },
            {
                'patient_state': 'Patient entering deep sleep phase, stable vitals',
                'ai_output': {
                    'light': {'color_hex': '#000080', 'brightness': 0.05},
                    'music': {'playlist_id': 'deep_sleep_waves', 'volume': 0.1},
                    'ai_reasoning': 'Optimizing environment for deep sleep recovery'
                }
            },
            {
                'patient_state': 'Patient reporting pain level 7/10, discomfort detected',
                'ai_output': {
                    'light': {'color_hex': '#DC143C', 'brightness': 0.4},
                    'music': {'playlist_id': 'pain_relief_frequencies', 'volume': 0.25},
                    'ai_reasoning': 'Activating pain management environment protocols'
                }
            },
            {
                'patient_state': 'Morning wake-up time, circadian rhythm optimization',
                'ai_output': {
                    'light': {'color_hex': '#FFA500', 'brightness': 0.8},
                    'music': {'playlist_id': 'gentle_morning_classical', 'volume': 0.35},
                    'ai_reasoning': 'Supporting natural circadian rhythm for healthy wake cycle'
                }
            }
        ]
        
        for i, scenario in enumerate(ai_scenarios, 1):
            print(f"\n🎯 AI Scenario {i}")
            print("-" * 20)
            print(f"Patient State: {scenario['patient_state']}")
            print(f"AI Reasoning: {scenario['ai_output']['ai_reasoning']}")
            
            # Apply to a random room
            room_id = random.choice(self.rooms)
            patient = self.patient_scenarios[room_id]
            print(f"Target Room: {room_id} - {patient['name']}")
            
            success = self.iot_manager.apply_environment_settings(room_id, scenario['ai_output'])
            
            if success:
                print("✅ AI response applied successfully")
                state = self.iot_manager.get_current_state(room_id)
                self._display_device_state(state, detailed=True)
            else:
                print("❌ Failed to apply AI response")
            
            time.sleep(2)  # Pause between scenarios
    
    def monitor_all_rooms(self):
        """Monitor current state of all rooms"""
        print("\n📊 IoT Simulator - Room Status Monitor")
        print("=" * 60)
        
        for room_id in self.rooms:
            patient = self.patient_scenarios[room_id]
            print(f"\n🏠 {room_id} - {patient['name']} ({patient['condition']})")
            print("-" * 40)
            
            state = self.iot_manager.get_current_state(room_id)
            
            if not state['lights'] and not state['audio']:
                print("   🔘 No active devices")
            else:
                self._display_device_state(state, detailed=True)
    
    def stress_test(self, num_commands: int = 50):
        """Perform stress test with rapid IoT commands"""
        print(f"\n⚡ IoT Simulator - Stress Test ({num_commands} commands)")
        print("=" * 60)
        
        success_count = 0
        start_time = time.time()
        
        for i in range(num_commands):
            room_id = random.choice(self.rooms)
            
            # Random settings
            settings = {
                'light': {
                    'color_hex': f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}",
                    'brightness': random.uniform(0.1, 1.0)
                },
                'music': {
                    'playlist_id': random.choice(['ambient', 'classical', 'nature', 'therapy', 'sleep']),
                    'volume': random.uniform(0.1, 0.5)
                }
            }
            
            success = self.iot_manager.apply_environment_settings(room_id, settings)
            if success:
                success_count += 1
            
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{num_commands} commands completed")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📈 Stress Test Results:")
        print(f"   Commands: {num_commands}")
        print(f"   Successful: {success_count}")
        print(f"   Failed: {num_commands - success_count}")
        print(f"   Success Rate: {(success_count/num_commands)*100:.1f}%")
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Commands/second: {num_commands/duration:.1f}")
    
    def _display_device_state(self, state: Dict, detailed: bool = False):
        """Display device state information"""
        lights = state.get('lights', {})
        audio = state.get('audio', {})
        
        if lights:
            color = lights.get('color', 'Unknown')
            brightness = lights.get('brightness', 0)
            updated = lights.get('updated', 0)
            if detailed:
                print(f"   💡 Lights: {color} at {brightness:.0%} (updated: {time.ctime(updated) if updated else 'Never'})")
            else:
                print(f"   💡 {color} at {brightness:.0%}")
        
        if audio:
            playlist = audio.get('playlist', 'Unknown')
            volume = audio.get('volume', 0)
            playing = audio.get('playing', False)
            updated = audio.get('updated', 0)
            if detailed:
                print(f"   🔊 Audio: '{playlist}' at {volume:.0%} {'(Playing)' if playing else '(Stopped)'}")
                print(f"       Updated: {time.ctime(updated) if updated else 'Never'}")
            else:
                print(f"   🔊 '{playlist}' at {volume:.0%}")


def main():
    """Main IoT Simulator execution"""
    print("🚀 Beat Suite AI - IoT Device Simulator")
    print("=" * 70)
    
    # Initialize simulator
    simulator = IoTSimulator()
    
    # Menu system
    while True:
        print("\n📋 IoT Simulator Menu:")
        print("1. 🎬 Simulate Patient Scenarios")
        print("2. 🔧 Test Individual Devices") 
        print("3. 🤖 Simulate AI Responses")
        print("4. 📊 Monitor All Rooms")
        print("5. ⚡ Stress Test")
        print("6. 🚪 Exit")
        
        try:
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                simulator.simulate_patient_scenarios()
            elif choice == '2':
                simulator.test_individual_devices()
            elif choice == '3':
                simulator.simulate_ai_responses()
            elif choice == '4':
                simulator.monitor_all_rooms()
            elif choice == '5':
                try:
                    num_commands = int(input("Enter number of commands (default 50): ") or "50")
                    simulator.stress_test(num_commands)
                except ValueError:
                    print("Invalid number, using default (50)")
                    simulator.stress_test()
            elif choice == '6':
                print("\n👋 IoT Simulator shutting down...")
                break
            else:
                print("❌ Invalid choice. Please select 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 IoT Simulator interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Simulator error: {e}")


if __name__ == "__main__":
    main()