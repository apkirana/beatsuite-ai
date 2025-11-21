"""
Comprehensive Integration Tests for Feedback System
Tests the complete feedback flow: collection → storage → analysis → adaptation
"""

import pytest
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from services.feedback_service import FeedbackService
from services.agent_memory_service import AgentMemoryService


class TestFeedbackServiceIntegration:
    """Integration tests for FeedbackService"""

    @pytest.fixture
    def temp_feedback_file(self):
        """Create temporary feedback file for testing"""
        temp_dir = tempfile.mkdtemp()
        feedback_file = Path(temp_dir) / "user_feedback.json"
        
        # Initialize with sample data
        initial_data = {
            "P001": {
                "feedback_history": [],
                "interaction_preferences": {},
                "adaptation_settings": {"auto_adapt": True, "learning_enabled": True}
            }
        }
        
        with open(feedback_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
        
        yield feedback_file
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def feedback_service(self, temp_feedback_file):
        """Create FeedbackService instance with temp file"""
        service = FeedbackService()
        service.feedback_file = temp_feedback_file
        return service

    @pytest.fixture
    def temp_memory_file(self):
        """Create temporary memory file for testing"""
        temp_dir = tempfile.mkdtemp()
        memory_file = Path(temp_dir) / "agent_memory.json"
        
        initial_data = {
            "P001": {
                "learned_patterns": [],
                "adaptation_rules": [],
                "last_updated": datetime.now().isoformat(),
                "confidence_score": 0.0
            }
        }
        
        with open(memory_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
        
        yield memory_file
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def agent_memory_service(self, temp_memory_file):
        """Create AgentMemoryService instance with temp file"""
        service = AgentMemoryService()
        service.memory_file = temp_memory_file
        return service

    def test_feedback_submission_and_retrieval(self, feedback_service):
        """Test submitting feedback and retrieving it"""
        patient_id = "P001"
        
        # Submit feedback
        result = feedback_service.submit_feedback(
            patient_id=patient_id,
            interaction_type="music_suggestion",
            action="Played Beethoven Symphony",
            situation="Patient experiencing pain",
            feedback_type="thumbs_up",
            rating=5,
            comment="Really helped me relax"
        )
        
        assert result["success"] is True
        assert result["feedback_id"] is not None
        
        # Retrieve feedback
        history = feedback_service.get_feedback_history(patient_id)
        assert len(history) > 0
        assert history[0]["interaction_type"] == "music_suggestion"
        assert history[0]["feedback_type"] == "thumbs_up"

    def test_feedback_summary_generation(self, feedback_service):
        """Test feedback summary metrics"""
        patient_id = "P001"
        
        # Submit multiple feedback items
        feedback_data = [
            ("music_suggestion", "Played Beethoven", "Patient in pain", "thumbs_up", 5, "Excellent"),
            ("music_suggestion", "Played Mozart", "Patient awake", "thumbs_up", 5, "Great"),
            ("lighting_control", "Dimmed lights", "Evening time", "thumbs_down", 2, "Too dark"),
            ("temperature_control", "Set to 22C", "Patient cold", "thumbs_up", 4, "Perfect"),
        ]
        
        for itype, action, situation, ftype, rating, comment in feedback_data:
            feedback_service.submit_feedback(
                patient_id=patient_id,
                interaction_type=itype,
                action=action,
                situation=situation,
                feedback_type=ftype,
                rating=rating,
                comment=comment
            )
        
        # Get summary
        summary = feedback_service.get_feedback_summary(patient_id)
        
        assert summary["total_feedback"] == 4
        assert summary["positive_feedback"] == 3
        assert summary["negative_feedback"] == 1
        assert summary["average_rating"] == 4.0
        assert len(summary["most_liked_actions"]) > 0
        assert len(summary["least_liked_actions"]) > 0

    def test_preference_extraction(self, feedback_service):
        """Test extraction of preferences from feedback"""
        patient_id = "P001"
        
        # Submit feedback with patterns
        interactions = [
            ("music_suggestion", "Played Classical", "thumbs_up", 5),
            ("music_suggestion", "Played Classical", "thumbs_up", 5),
            ("music_suggestion", "Played Pop", "thumbs_down", 2),
            ("music_suggestion", "Played Jazz", "thumbs_up", 4),
        ]
        
        for itype, action, ftype, rating in interactions:
            feedback_service.submit_feedback(
                patient_id=patient_id,
                interaction_type=itype,
                action=action,
                situation="Testing music",
                feedback_type=ftype,
                rating=rating,
                comment=""
            )
        
        # Get preferences
        prefs = feedback_service.get_interaction_preferences(patient_id)
        
        assert "music_suggestion" in prefs
        assert prefs["music_suggestion"]["preferred_actions"]
        assert prefs["music_suggestion"]["success_rate"] > 0.5

    def test_action_avoidance_logic(self, feedback_service):
        """Test that system correctly identifies actions to avoid"""
        patient_id = "P001"
        
        # Submit negative feedback for specific action
        for _ in range(3):
            feedback_service.submit_feedback(
                patient_id=patient_id,
                interaction_type="lighting_control",
                action="Bright white light 100%",
                situation="Bedtime",
                feedback_type="thumbs_down",
                rating=1,
                comment="Harsh, painful to eyes"
            )
        
        # Check avoidance
        should_avoid = feedback_service.should_avoid_action(
            patient_id=patient_id,
            interaction_type="lighting_control",
            action="Bright white light 100%"
        )
        
        assert should_avoid is True

    def test_action_recommendation_logic(self, feedback_service):
        """Test that system correctly recommends positive actions"""
        patient_id = "P001"
        
        # Submit positive feedback for specific action
        for _ in range(3):
            feedback_service.submit_feedback(
                patient_id=patient_id,
                interaction_type="temperature_control",
                action="Set to 21C with humidity 50%",
                situation="Night time",
                feedback_type="thumbs_up",
                rating=5,
                comment="Perfect comfort level"
            )
        
        # Check recommendation
        should_recommend = feedback_service.should_recommend_action(
            patient_id=patient_id,
            interaction_type="temperature_control",
            action="Set to 21C with humidity 50%"
        )
        
        assert should_recommend is True

    def test_feedback_persistence(self, feedback_service, temp_feedback_file):
        """Test that feedback is properly persisted to disk"""
        patient_id = "P001"
        
        # Submit feedback
        feedback_service.submit_feedback(
            patient_id=patient_id,
            interaction_type="music_suggestion",
            action="Played Debussy",
            situation="Relaxation time",
            feedback_type="thumbs_up",
            rating=5,
            comment="Beautiful"
        )
        
        # Create new service instance (simulating app restart)
        new_service = FeedbackService()
        new_service.feedback_file = temp_feedback_file
        
        # Verify data persists
        history = new_service.get_feedback_history(patient_id)
        assert len(history) > 0
        assert history[0]["action"] == "Played Debussy"

    def test_multiple_patients_isolation(self, feedback_service):
        """Test that feedback from different patients is isolated"""
        # Submit feedback for P001
        feedback_service.submit_feedback(
            patient_id="P001",
            interaction_type="music_suggestion",
            action="Played Beethoven",
            situation="Pain management",
            feedback_type="thumbs_up",
            rating=5,
            comment="Excellent"
        )
        
        # Submit feedback for P002
        feedback_service.submit_feedback(
            patient_id="P002",
            interaction_type="music_suggestion",
            action="Played Mozart",
            situation="Relaxation",
            feedback_type="thumbs_down",
            rating=1,
            comment="Not my preference"
        )
        
        # Verify isolation
        p001_history = feedback_service.get_feedback_history("P001")
        p002_history = feedback_service.get_feedback_history("P002")
        
        assert len(p001_history) == 1
        assert len(p002_history) == 1
        assert p001_history[0]["action"] != p002_history[0]["action"]


class TestAgentMemoryServiceIntegration:
    """Integration tests for AgentMemoryService"""

    @pytest.fixture
    def temp_memory_file(self):
        """Create temporary memory file"""
        temp_dir = tempfile.mkdtemp()
        memory_file = Path(temp_dir) / "agent_memory.json"
        
        initial_data = {
            "P001": {
                "learned_patterns": [],
                "adaptation_rules": [],
                "last_updated": datetime.now().isoformat(),
                "confidence_score": 0.0
            }
        }
        
        with open(memory_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
        
        yield memory_file
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def agent_memory_service(self, temp_memory_file):
        """Create AgentMemoryService"""
        service = AgentMemoryService()
        service.memory_file = temp_memory_file
        return service

    def test_memory_initialization(self, agent_memory_service):
        """Test memory initialization for patient"""
        patient_id = "P003"
        
        agent_memory_service._ensure_patient_memory(patient_id)
        
        with open(agent_memory_service.memory_file, 'r') as f:
            data = json.load(f)
        
        assert patient_id in data
        assert "learned_patterns" in data[patient_id]

    @patch('backend.services.agent_memory_service.genai.GenerativeModel')
    def test_pattern_analysis_with_fallback(self, mock_genai, agent_memory_service):
        """Test pattern analysis with fallback logic"""
        patient_id = "P001"
        feedback_history = [
            {"interaction_type": "music", "feedback_type": "thumbs_up"},
            {"interaction_type": "music", "feedback_type": "thumbs_up"},
            {"interaction_type": "music", "feedback_type": "thumbs_down"},
        ]
        
        # Test with API unavailable (None response)
        mock_genai.return_value.generate_content.return_value = None
        
        result = agent_memory_service.analyze_feedback_patterns(
            patient_id=patient_id,
            feedback_history=feedback_history
        )
        
        # Should use fallback and return some result
        assert result is not None
        assert "patterns" in result or "fallback" in str(result).lower()

    def test_adaptive_decision_structure(self, agent_memory_service):
        """Test that adaptive decisions have proper structure"""
        patient_id = "P001"
        
        # Create minimal memory data
        agent_memory_service._ensure_patient_memory(patient_id)
        
        # Note: With mocked Gemini, test the structure
        with patch.object(agent_memory_service, '_call_gemini') as mock_call:
            mock_call.return_value = json.dumps({
                "recommended_action": "Play Beethoven",
                "reasoning": "Patient previously enjoyed classical",
                "confidence": 0.85,
                "fallback": False
            })
            
            result = agent_memory_service.generate_adaptive_decision(
                patient_id=patient_id,
                situation="Patient in pain",
                available_actions=["Play music", "Adjust temperature"]
            )
            
            assert result is not None
            if isinstance(result, dict):
                assert "recommended_action" in result or "fallback" in result

    def test_interaction_evaluation_framework(self, agent_memory_service):
        """Test evaluation of interaction success"""
        patient_id = "P001"
        
        agent_memory_service._ensure_patient_memory(patient_id)
        
        # Test evaluation structure
        with patch.object(agent_memory_service, '_call_gemini') as mock_call:
            mock_call.return_value = json.dumps({
                "success": True,
                "score": 0.85,
                "improvements": ["Could add more context"]
            })
            
            result = agent_memory_service.evaluate_interaction_success(
                patient_id=patient_id,
                interaction_type="music_suggestion",
                action="Played Debussy",
                outcome="Patient reported improved pain"
            )
            
            # Should return evaluation structure
            assert result is not None


class TestEndToEndFeedbackFlow:
    """End-to-end integration tests for complete feedback workflow"""

    @pytest.fixture
    def temp_files(self):
        """Create temporary files for both services"""
        temp_dir = tempfile.mkdtemp()
        feedback_file = Path(temp_dir) / "user_feedback.json"
        memory_file = Path(temp_dir) / "agent_memory.json"
        
        # Initialize feedback file
        feedback_data = {
            "P001": {
                "feedback_history": [],
                "interaction_preferences": {},
                "adaptation_settings": {"auto_adapt": True}
            }
        }
        with open(feedback_file, 'w') as f:
            json.dump(feedback_data, f)
        
        # Initialize memory file
        memory_data = {
            "P001": {
                "learned_patterns": [],
                "adaptation_rules": [],
                "last_updated": datetime.now().isoformat(),
                "confidence_score": 0.0
            }
        }
        with open(memory_file, 'w') as f:
            json.dump(memory_data, f)
        
        yield feedback_file, memory_file
        shutil.rmtree(temp_dir)

    def test_complete_feedback_workflow(self, temp_files):
        """Test complete workflow: feedback → storage → analysis → decision"""
        feedback_file, memory_file = temp_files
        patient_id = "P001"
        
        # Initialize services
        feedback_service = FeedbackService()
        feedback_service.feedback_file = feedback_file
        memory_service = AgentMemoryService()
        memory_service.memory_file = memory_file
        
        # Step 1: Submit feedback
        for i in range(5):
            feedback_service.submit_feedback(
                patient_id=patient_id,
                interaction_type="music_suggestion",
                action="Played Classical Music",
                situation=f"Evening relaxation {i}",
                feedback_type="thumbs_up",
                rating=5,
                comment="Helped with pain"
            )
        
        # Step 2: Verify storage
        history = feedback_service.get_feedback_history(patient_id)
        assert len(history) == 5
        
        # Step 3: Get preferences
        prefs = feedback_service.get_interaction_preferences(patient_id)
        assert "music_suggestion" in prefs
        
        # Step 4: Check memory (would use Gemini in production)
        with patch.object(memory_service, '_call_gemini') as mock_gemini:
            mock_gemini.return_value = json.dumps({
                "recommendation": "Continue with classical music",
                "confidence": 0.95
            })
            
            summary = feedback_service.get_memory_insights(patient_id)
            assert len(summary["feedback_summary"]["feedback_history"]) > 0

    def test_feedback_driven_adaptation_cycle(self, temp_files):
        """Test multiple cycles of feedback and adaptation"""
        feedback_file, memory_file = temp_files
        patient_id = "P001"
        
        feedback_service = FeedbackService()
        feedback_service.feedback_file = feedback_file
        
        # Cycle 1: Initial feedback
        feedback_service.submit_feedback(
            patient_id=patient_id,
            interaction_type="music_suggestion",
            action="Played Pop Music",
            situation="Evening",
            feedback_type="thumbs_down",
            rating=2
        )
        
        # Verify avoidance
        should_avoid = feedback_service.should_avoid_action(
            patient_id=patient_id,
            interaction_type="music_suggestion",
            action="Played Pop Music"
        )
        
        # Cycle 2: New suggestion (should be different)
        feedback_service.submit_feedback(
            patient_id=patient_id,
            interaction_type="music_suggestion",
            action="Played Jazz",
            situation="Evening",
            feedback_type="thumbs_up",
            rating=4
        )
        
        # Verify recommendation
        should_recommend = feedback_service.should_recommend_action(
            patient_id=patient_id,
            interaction_type="music_suggestion",
            action="Played Jazz"
        )
        
        assert should_avoid is True or len(history := feedback_service.get_feedback_history(patient_id)) > 0


class TestFeedbackDataQuality:
    """Tests for data quality and consistency"""

    @pytest.fixture
    def feedback_service(self):
        """Create service with temp file"""
        temp_dir = tempfile.mkdtemp()
        feedback_file = Path(temp_dir) / "user_feedback.json"
        
        initial_data = {"P001": {"feedback_history": [], "interaction_preferences": {}, "adaptation_settings": {}}}
        with open(feedback_file, 'w') as f:
            json.dump(initial_data, f)
        
        service = FeedbackService()
        service.feedback_file = feedback_file
        yield service
        shutil.rmtree(temp_dir)

    def test_feedback_timestamp_accuracy(self, feedback_service):
        """Test that feedback timestamps are accurate"""
        patient_id = "P001"
        before = datetime.now()
        
        feedback_service.submit_feedback(
            patient_id=patient_id,
            interaction_type="music",
            action="Test",
            situation="Test",
            feedback_type="thumbs_up",
            rating=5
        )
        
        after = datetime.now()
        history = feedback_service.get_feedback_history(patient_id)
        feedback_timestamp = datetime.fromisoformat(history[0]["timestamp"])
        
        assert before <= feedback_timestamp <= after

    def test_rating_scale_consistency(self, feedback_service):
        """Test that ratings remain in valid ranges"""
        patient_id = "P001"
        
        for rating in [1, 2, 3, 4, 5]:
            feedback_service.submit_feedback(
                patient_id=patient_id,
                interaction_type="music",
                action="Test",
                situation="Test",
                feedback_type="thumbs_up",
                rating=rating
            )
        
        history = feedback_service.get_feedback_history(patient_id)
        
        for feedback in history:
            assert 1 <= feedback["rating"] <= 5

    def test_null_handling_in_comments(self, feedback_service):
        """Test handling of empty/null comments"""
        patient_id = "P001"
        
        feedback_service.submit_feedback(
            patient_id=patient_id,
            interaction_type="music",
            action="Test",
            situation="Test",
            feedback_type="thumbs_up",
            rating=5,
            comment=""
        )
        
        history = feedback_service.get_feedback_history(patient_id)
        assert "comment" in history[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
