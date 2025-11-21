"""
Test Fixtures and Sample Data for Feedback System
Provides realistic test data for comprehensive evaluation
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random


class FeedbackTestFixtures:
    """Pre-built test scenarios and data fixtures"""
    
    @staticmethod
    def get_sample_feedback_entries() -> List[Dict[str, Any]]:
        """Get realistic sample feedback entries"""
        return [
            {
                "feedback_id": "FB001",
                "patient_id": "P001",
                "interaction_type": "music_suggestion",
                "action": "Classical: Beethoven Symphony No. 5",
                "situation": "Evening pain management",
                "feedback_type": "thumbs_up",
                "rating": 5,
                "comment": "Helped calm my anxiety and reduced pain perception",
                "timestamp": (datetime.now() - timedelta(days=3)).isoformat()
            },
            {
                "feedback_id": "FB002",
                "patient_id": "P001",
                "interaction_type": "music_suggestion",
                "action": "Jazz: Miles Davis Kind of Blue",
                "situation": "Afternoon relaxation",
                "feedback_type": "thumbs_up",
                "rating": 4,
                "comment": "Nice background music, helped focus",
                "timestamp": (datetime.now() - timedelta(days=2)).isoformat()
            },
            {
                "feedback_id": "FB003",
                "patient_id": "P001",
                "interaction_type": "music_suggestion",
                "action": "Pop: Upbeat modern hits",
                "situation": "Morning wake-up",
                "feedback_type": "thumbs_down",
                "rating": 2,
                "comment": "Too stimulating for my condition",
                "timestamp": (datetime.now() - timedelta(days=1)).isoformat()
            },
            {
                "feedback_id": "FB004",
                "patient_id": "P001",
                "interaction_type": "lighting_control",
                "action": "Warm lights at 30% brightness",
                "situation": "Evening preparation for sleep",
                "feedback_type": "thumbs_up",
                "rating": 5,
                "comment": "Perfect for winding down",
                "timestamp": (datetime.now() - timedelta(hours=12)).isoformat()
            },
            {
                "feedback_id": "FB005",
                "patient_id": "P001",
                "interaction_type": "temperature_control",
                "action": "Set to 20°C with 45% humidity",
                "situation": "Night sleep optimization",
                "feedback_type": "thumbs_up",
                "rating": 4,
                "comment": "Slept better than usual",
                "timestamp": (datetime.now() - timedelta(hours=6)).isoformat()
            }
        ]
    
    @staticmethod
    def get_music_preference_data() -> List[Dict[str, Any]]:
        """Get music therapy feedback data"""
        genres = [
            ("Classical", ["Beethoven", "Mozart", "Chopin"], 5, "Calming and therapeutic"),
            ("Jazz", ["Miles Davis", "John Coltrane", "Bill Evans"], 4, "Relaxing background"),
            ("Ambient", ["Brian Eno", "Satie", "Nils Frahm"], 5, "Very peaceful"),
            ("Pop", ["Modern hits", "Upbeat tracks"], 1, "Too stimulating"),
            ("Electronic", ["Techno", "House"], 2, "Not suitable for relaxation"),
        ]
        
        data = []
        idx = 1
        for genre, artists, rating, comment in genres:
            for artist in artists:
                data.append({
                    "feedback_id": f"MUSIC{idx:03d}",
                    "interaction_type": "music_suggestion",
                    "action": f"{genre}: {artist}",
                    "feedback_type": "thumbs_up" if rating >= 4 else "thumbs_down",
                    "rating": rating,
                    "comment": comment,
                    "timestamp": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
                })
                idx += 1
        
        return data
    
    @staticmethod
    def get_environmental_control_data() -> List[Dict[str, Any]]:
        """Get environmental control feedback data"""
        controls = [
            ("lighting_control", "Bright white lights 100%", 1, "Harsh on eyes"),
            ("lighting_control", "Warm lights at 30%", 5, "Perfect for evening"),
            ("lighting_control", "Complete darkness", 4, "Great for sleep"),
            ("temperature_control", "22°C, high humidity", 2, "Too warm"),
            ("temperature_control", "20°C, 45% humidity", 5, "Optimal comfort"),
            ("temperature_control", "18°C", 3, "A bit cold"),
            ("air_quality", "Fresh air mode", 4, "Good circulation"),
            ("air_quality", "Recirculate mode", 2, "Feels stuffy"),
        ]
        
        data = []
        idx = 1
        for itype, action, rating, comment in controls:
            data.append({
                "feedback_id": f"ENV{idx:03d}",
                "interaction_type": itype,
                "action": action,
                "feedback_type": "thumbs_up" if rating >= 4 else "thumbs_down",
                "rating": rating,
                "comment": comment,
                "timestamp": (datetime.now() - timedelta(days=random.randint(1, 20))).isoformat()
            })
            idx += 1
        
        return data
    
    @staticmethod
    def get_temporal_pattern_data() -> List[Dict[str, Any]]:
        """Get time-based feedback data showing temporal patterns"""
        time_patterns = [
            # Morning (6-9)
            ("music_suggestion", "Morning: Uplifting Music", "Morning (7:00 AM)", 5, "Perfect wake-up"),
            ("music_suggestion", "Morning: Classical Wake-up", "Morning (8:00 AM)", 4, "Energizing"),
            ("music_suggestion", "Morning: Ambient Calm", "Morning (6:30 AM)", 1, "Too slow for morning"),
            
            # Afternoon (12-17)
            ("activity_suggestion", "Afternoon: Light Exercise", "Afternoon (2:00 PM)", 4, "Productive"),
            ("music_suggestion", "Afternoon: Energetic Beats", "Afternoon (3:00 PM)", 4, "Good for activity"),
            ("activity_suggestion", "Afternoon: Rest", "Afternoon (2:30 PM)", 2, "Need activity"),
            
            # Evening (17-21)
            ("music_suggestion", "Evening: Jazz", "Evening (6:00 PM)", 5, "Very relaxing"),
            ("music_suggestion", "Evening: Upbeat Pop", "Evening (7:00 PM)", 1, "Too stimulating"),
            ("activity_suggestion", "Evening: Meditation", "Evening (8:00 PM)", 5, "Perfect wind-down"),
            
            # Night (21-6)
            ("activity_suggestion", "Night: Sleep Meditation", "Night (10:00 PM)", 5, "Helps me sleep"),
            ("activity_suggestion", "Night: Light Exercise", "Night (9:30 PM)", 1, "Keeps me awake"),
            ("music_suggestion", "Night: Ambient Sleep", "Night (10:30 PM)", 4, "Conducive to sleep"),
        ]
        
        data = []
        for idx, (itype, action, situation, rating, comment) in enumerate(time_patterns, 1):
            data.append({
                "feedback_id": f"TIME{idx:03d}",
                "interaction_type": itype,
                "action": action,
                "situation": situation,
                "feedback_type": "thumbs_up" if rating >= 4 else "thumbs_down",
                "rating": rating,
                "comment": comment,
                "timestamp": (datetime.now() - timedelta(days=random.randint(5, 30))).isoformat()
            })
        
        return data
    
    @staticmethod
    def get_multi_patient_data() -> Dict[str, List[Dict[str, Any]]]:
        """Get data for multiple patients with different preferences"""
        
        patient_data = {
            "PATIENT_A": [
                # Patient A loves classical, dislikes pop
                ("music_suggestion", "Classical Music", 5, "Love it", "thumbs_up"),
                ("music_suggestion", "Classical Pieces", 5, "Excellent", "thumbs_up"),
                ("music_suggestion", "Classical Symphony", 4, "Very good", "thumbs_up"),
                ("music_suggestion", "Pop Music", 1, "Hate it", "thumbs_down"),
                ("music_suggestion", "Pop Hits", 1, "Not for me", "thumbs_down"),
            ],
            "PATIENT_B": [
                # Patient B loves pop, dislikes classical
                ("music_suggestion", "Pop Music", 5, "Love it", "thumbs_up"),
                ("music_suggestion", "Pop Hits", 5, "Excellent", "thumbs_up"),
                ("music_suggestion", "Upbeat Pop", 4, "Very good", "thumbs_up"),
                ("music_suggestion", "Classical Music", 1, "Hate it", "thumbs_down"),
                ("music_suggestion", "Classical Symphony", 1, "Not for me", "thumbs_down"),
            ],
            "PATIENT_C": [
                # Patient C likes ambient/jazz
                ("music_suggestion", "Ambient", 5, "Perfect", "thumbs_up"),
                ("music_suggestion", "Jazz", 4, "Good", "thumbs_up"),
                ("music_suggestion", "Jazz Fusion", 4, "Nice", "thumbs_up"),
                ("music_suggestion", "Rock Music", 1, "Too loud", "thumbs_down"),
            ],
        }
        
        result = {}
        for patient_id, feedback_list in patient_data.items():
            patient_feedback = []
            for idx, (itype, action, rating, comment, ftype) in enumerate(feedback_list, 1):
                patient_feedback.append({
                    "feedback_id": f"{patient_id}_FB{idx:03d}",
                    "patient_id": patient_id,
                    "interaction_type": itype,
                    "action": action,
                    "situation": "Music therapy session",
                    "feedback_type": ftype,
                    "rating": rating,
                    "comment": comment,
                    "timestamp": (datetime.now() - timedelta(days=30-idx)).isoformat()
                })
            result[patient_id] = patient_feedback
        
        return result
    
    @staticmethod
    def get_confidence_building_data() -> List[Dict[str, Any]]:
        """Get data showing confidence building over multiple feedbacks"""
        # Consistent positive feedback for single action
        base_action = "Classical: Debussy Clair de lune"
        
        data = []
        for idx in range(10):
            data.append({
                "feedback_id": f"CONF{idx:03d}",
                "interaction_type": "music_suggestion",
                "action": base_action,
                "situation": f"Session {idx+1}",
                "feedback_type": "thumbs_up",
                "rating": 5 if idx % 3 != 2 else 4,  # Mostly 5s, some 4s
                "comment": "Excellent as always" if idx < 5 else "Consistent favorite",
                "timestamp": (datetime.now() - timedelta(days=10-idx)).isoformat()
            })
        
        return data
    
    @staticmethod
    def get_edge_case_data() -> List[Dict[str, Any]]:
        """Get edge case data for robustness testing"""
        return [
            {
                "feedback_id": "EDGE001",
                "interaction_type": "music_suggestion",
                "action": "",  # Empty action
                "situation": "Test",
                "feedback_type": "thumbs_up",
                "rating": 5,
                "comment": ""
            },
            {
                "feedback_id": "EDGE002",
                "interaction_type": "music_suggestion",
                "action": "A" * 500,  # Very long action
                "situation": "Test",
                "feedback_type": "thumbs_up",
                "rating": 5,
                "comment": "B" * 1000  # Very long comment
            },
            {
                "feedback_id": "EDGE003",
                "interaction_type": "music_suggestion",
                "action": "Special chars: @#$%^&*()",
                "situation": "Test",
                "feedback_type": "thumbs_up",
                "rating": 5,
                "comment": "Unicode: 你好 🎵 ñ"
            },
            {
                "feedback_id": "EDGE004",
                "interaction_type": "music_suggestion",
                "action": "Test",
                "situation": None,  # Null situation
                "feedback_type": "thumbs_neutral",
                "rating": 3,
                "comment": None
            },
        ]
    
    @staticmethod
    def generate_json_test_file(data: List[Dict[str, Any]], file_path: str) -> None:
        """Generate a JSON test file with sample data"""
        organized_data = {}
        for entry in data:
            patient_id = entry.get("patient_id", "P001")
            if patient_id not in organized_data:
                organized_data[patient_id] = {
                    "feedback_history": [],
                    "interaction_preferences": {},
                    "adaptation_settings": {
                        "auto_adapt": True,
                        "learning_enabled": True
                    }
                }
            
            # Add to history
            feedback_entry = {k: v for k, v in entry.items() if k != "patient_id"}
            organized_data[patient_id]["feedback_history"].append(feedback_entry)
        
        # Create directory if needed
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(organized_data, f, indent=2)
    
    @staticmethod
    def get_performance_test_data(count: int = 1000) -> List[Dict[str, Any]]:
        """Generate large dataset for performance testing"""
        actions = [
            "Classical: Beethoven",
            "Jazz: Miles Davis",
            "Ambient: Brian Eno",
            "Pop: Modern Hits",
            "Electronic: Techno",
        ]
        
        situations = [
            "Morning",
            "Afternoon",
            "Evening",
            "Night"
        ]
        
        data = []
        for i in range(count):
            data.append({
                "feedback_id": f"PERF{i:06d}",
                "interaction_type": "music_suggestion",
                "action": random.choice(actions),
                "situation": random.choice(situations),
                "feedback_type": random.choice(["thumbs_up", "thumbs_down"]),
                "rating": random.randint(1, 5),
                "comment": f"Feedback entry {i}",
                "timestamp": (datetime.now() - timedelta(seconds=i)).isoformat()
            })
        
        return data


class FeedbackScenarioGenerator:
    """Generate realistic test scenarios"""
    
    @staticmethod
    def scenario_pain_management() -> Dict[str, Any]:
        """Scenario: Patient with chronic pain seeking management"""
        return {
            "scenario_name": "Chronic Pain Management",
            "patient_id": "SCENARIO_PAIN",
            "description": "Patient experiences moderate to severe pain",
            "feedback_data": [
                ("music_suggestion", "Classical Calm", 5, "Reduced pain perception"),
                ("music_suggestion", "Jazz Background", 4, "Helpful"),
                ("music_suggestion", "Pop Energetic", 1, "Increased anxiety"),
                ("lighting_control", "Dim warm", 5, "Very comfortable"),
                ("lighting_control", "Bright white", 1, "Painful for eyes"),
                ("temperature_control", "20C optimal", 5, "Perfect"),
            ]
        }
    
    @staticmethod
    def scenario_sleep_optimization() -> Dict[str, Any]:
        """Scenario: Patient seeking better sleep quality"""
        return {
            "scenario_name": "Sleep Quality Improvement",
            "patient_id": "SCENARIO_SLEEP",
            "description": "Patient wants to improve sleep quality",
            "feedback_data": [
                ("lighting_control", "Complete darkness", 5, "Sleep onset faster"),
                ("lighting_control", "Dim lights", 4, "Acceptable"),
                ("temperature_control", "20C cool", 5, "Ideal for sleep"),
                ("music_suggestion", "Sleep meditation", 5, "Very helpful"),
                ("activity_suggestion", "Evening yoga", 4, "Relaxing"),
                ("activity_suggestion", "High activity", 1, "Too stimulating"),
            ]
        }
    
    @staticmethod
    def scenario_anxiety_reduction() -> Dict[str, Any]:
        """Scenario: Patient with anxiety seeking relief"""
        return {
            "scenario_name": "Anxiety Management",
            "patient_id": "SCENARIO_ANXIETY",
            "description": "Patient experiences anxiety episodes",
            "feedback_data": [
                ("music_suggestion", "Ambient calm", 5, "Highly calming"),
                ("music_suggestion", "Nature sounds", 5, "Very soothing"),
                ("breathing_exercise", "4-7-8 technique", 5, "Effective"),
                ("activity_suggestion", "Guided meditation", 4, "Helpful"),
                ("music_suggestion", "Upbeat pop", 1, "Increases anxiety"),
                ("activity_suggestion", "High intensity", 1, "Worsens anxiety"),
            ]
        }
    
    @staticmethod
    def scenario_recovery_motivation() -> Dict[str, Any]:
        """Scenario: Patient in recovery needing motivation"""
        return {
            "scenario_name": "Recovery Motivation",
            "patient_id": "SCENARIO_RECOVERY",
            "description": "Patient in post-surgery recovery",
            "feedback_data": [
                ("activity_suggestion", "Light stretching", 5, "Aids recovery"),
                ("activity_suggestion", "Gentle walk", 4, "Good progress"),
                ("music_suggestion", "Inspirational", 5, "Motivating"),
                ("music_suggestion", "Upbeat pop", 5, "Energizing"),
                ("activity_suggestion", "Heavy exercise", 1, "Too strenuous"),
                ("rest_suggestion", "Adequate breaks", 5, "Important"),
            ]
        }


if __name__ == "__main__":
    # Generate test files
    print("Generating test fixtures...")
    
    fixtures = FeedbackTestFixtures()
    
    # Generate sample feedback file
    sample_data = fixtures.get_sample_feedback_entries()
    fixtures.generate_json_test_file(
        sample_data,
        "/workspaces/beatsuite-ai/tests/fixtures/sample_feedback.json"
    )
    print("✓ Generated sample_feedback.json")
    
    # Generate music preference data
    music_data = fixtures.get_music_preference_data()
    fixtures.generate_json_test_file(
        music_data,
        "/workspaces/beatsuite-ai/tests/fixtures/music_preferences.json"
    )
    print("✓ Generated music_preferences.json")
    
    # Generate environmental data
    env_data = fixtures.get_environmental_control_data()
    fixtures.generate_json_test_file(
        env_data,
        "/workspaces/beatsuite-ai/tests/fixtures/environmental_data.json"
    )
    print("✓ Generated environmental_data.json")
    
    # Generate temporal pattern data
    temporal_data = fixtures.get_temporal_pattern_data()
    fixtures.generate_json_test_file(
        temporal_data,
        "/workspaces/beatsuite-ai/tests/fixtures/temporal_patterns.json"
    )
    print("✓ Generated temporal_patterns.json")
    
    # Generate multi-patient data
    multi_patient = fixtures.get_multi_patient_data()
    for patient_id, feedback_list in multi_patient.items():
        fixtures.generate_json_test_file(
            feedback_list,
            f"/workspaces/beatsuite-ai/tests/fixtures/patient_{patient_id}.json"
        )
    print(f"✓ Generated {len(multi_patient)} multi-patient files")
    
    # Generate confidence building data
    confidence_data = fixtures.get_confidence_building_data()
    fixtures.generate_json_test_file(
        confidence_data,
        "/workspaces/beatsuite-ai/tests/fixtures/confidence_building.json"
    )
    print("✓ Generated confidence_building.json")
    
    print("\n✓ All test fixtures generated successfully!")
    print("Location: /workspaces/beatsuite-ai/tests/fixtures/")
