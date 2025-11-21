"""
User Feedback Service
Manages collection, storage, and retrieval of patient feedback on AI interactions
Integrates feedback into agent memory for adaptive behavior
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


class FeedbackService:
    """Service for managing patient feedback and memory"""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize feedback service
        
        Args:
            data_dir: Directory for storing feedback data (default: backend/data)
        """
        if data_dir is None:
            data_dir = str(Path(__file__).parent.parent / 'data')
        
        self.data_dir = Path(data_dir)
        self.feedback_file = self.data_dir / 'user_feedback.json'
        self.memory_file = self.data_dir / 'agent_memory.json'
        
        # Ensure feedback file exists
        if not self.feedback_file.exists():
            self._initialize_feedback_store()
        
        if not self.memory_file.exists():
            self._initialize_memory_store()
        
        logger.info("Feedback Service initialized")
    
    def _initialize_feedback_store(self):
        """Initialize empty feedback store"""
        self.feedback_file.write_text(json.dumps({}, indent=2))
        logger.info(f"Created feedback store at {self.feedback_file}")
    
    def _initialize_memory_store(self):
        """Initialize empty agent memory store"""
        self.memory_file.write_text(json.dumps({}, indent=2))
        logger.info(f"Created memory store at {self.memory_file}")
    
    def _load_feedback(self) -> Dict:
        """Load all feedback from storage"""
        try:
            content = self.feedback_file.read_text()
            return json.loads(content) if content else {}
        except Exception as e:
            logger.error(f"Error loading feedback: {e}")
            return {}
    
    def _save_feedback(self, feedback_data: Dict):
        """Save feedback to storage"""
        try:
            self.feedback_file.write_text(json.dumps(feedback_data, indent=2))
            logger.debug("Feedback saved to storage")
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
    
    def _load_memory(self) -> Dict:
        """Load agent memory from storage"""
        try:
            content = self.memory_file.read_text()
            return json.loads(content) if content else {}
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
            return {}
    
    def _save_memory(self, memory_data: Dict):
        """Save agent memory to storage"""
        try:
            self.memory_file.write_text(json.dumps(memory_data, indent=2))
            logger.debug("Memory saved to storage")
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def submit_feedback(self, patient_id: str, interaction_type: str, 
                       rating: str, rating_score: int = None,
                       user_comment: str = None,
                       interaction_context: Dict = None) -> Dict:
        """
        Submit feedback for a patient-agent interaction
        
        Args:
            patient_id: Patient identifier
            interaction_type: Type of interaction (music_suggestion, lighting, 
                            environment_control, pain_management, etc.)
            rating: 'positive', 'negative', or 'neutral'
            rating_score: Optional score 1-5 (higher is better)
            user_comment: Optional textual feedback
            interaction_context: Context about the interaction (action, situation, etc.)
        
        Returns:
            Dict with feedback submission result
        """
        try:
            # Validate inputs
            valid_ratings = ['positive', 'negative', 'neutral']
            if rating not in valid_ratings:
                return {
                    'success': False,
                    'error': f'Invalid rating. Must be one of: {valid_ratings}'
                }
            
            if rating_score and not (1 <= rating_score <= 5):
                return {
                    'success': False,
                    'error': 'Rating score must be between 1 and 5'
                }
            
            # Create feedback record
            feedback_id = f"FB{patient_id}_{uuid.uuid4().hex[:6].upper()}"
            
            feedback_record = {
                'feedback_id': feedback_id,
                'timestamp': datetime.now().isoformat(),
                'interaction_type': interaction_type,
                'interaction_context': interaction_context or {},
                'rating': rating,
                'rating_score': rating_score,
                'user_comment': user_comment
            }
            
            # Load and update feedback data
            feedback_data = self._load_feedback()
            
            if patient_id not in feedback_data:
                feedback_data[patient_id] = {
                    'feedback_history': [],
                    'interaction_preferences': {
                        'music_preferences': {
                            'positive_interactions': [],
                            'negative_interactions': [],
                            'neutral_interactions': []
                        },
                        'lighting_preferences': {
                            'positive_interactions': [],
                            'negative_interactions': [],
                            'neutral_interactions': []
                        },
                        'timing_preferences': {
                            'best_times': [],
                            'worst_times': []
                        }
                    },
                    'adaptation_settings': {
                        'learning_enabled': True,
                        'feedback_weight': 0.7,
                        'last_adapted': None
                    }
                }
            
            # Add to feedback history
            feedback_data[patient_id]['feedback_history'].append(feedback_record)
            
            # Update interaction preferences based on rating
            self._update_interaction_preferences(
                feedback_data[patient_id],
                interaction_type,
                rating,
                interaction_context
            )
            
            # Save updated feedback
            self._save_feedback(feedback_data)
            
            # Update agent memory
            self._update_agent_memory(patient_id, feedback_record)
            
            logger.info(f"Feedback submitted - Patient: {patient_id}, Type: {interaction_type}, Rating: {rating}")
            
            return {
                'success': True,
                'feedback_id': feedback_id,
                'message': 'Feedback recorded successfully',
                'patient_id': patient_id
            }
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            return {
                'success': False,
                'error': f'Failed to submit feedback: {str(e)}'
            }
    
    def _update_interaction_preferences(self, patient_data: Dict, interaction_type: str,
                                       rating: str, context: Dict):
        """Update interaction preferences based on feedback"""
        
        preferences = patient_data['interaction_preferences']
        
        # Extract specific preference category from context
        category_key = None
        if 'action' in context:
            action_lower = str(context['action']).lower()
            
            if any(term in action_lower for term in ['music', 'playlist', 'song']):
                category_key = 'music_preferences'
            elif any(term in action_lower for term in ['light', 'brightness', 'color']):
                category_key = 'lighting_preferences'
        
        if category_key and category_key in preferences:
            preference_category = preferences[category_key]
            action_detail = context.get('action', 'generic_action')
            
            # Update preferences based on rating
            rating_key = f'{rating}_interactions'
            if rating_key in preference_category:
                if action_detail not in preference_category[rating_key]:
                    preference_category[rating_key].append(action_detail)
                    logger.debug(f"Updated {category_key}: Added {action_detail} to {rating_key}")
    
    def _update_agent_memory(self, patient_id: str, feedback_record: Dict):
        """Update agent memory with new feedback information"""
        
        try:
            memory_data = self._load_memory()
            
            if patient_id not in memory_data:
                memory_data[patient_id] = {
                    'learned_patterns': [],
                    'adaptation_rules': [],
                    'last_updated': datetime.now().isoformat(),
                    'confidence_score': 0.0
                }
            
            # Create a learned pattern from the feedback
            pattern = {
                'feedback_id': feedback_record['feedback_id'],
                'learned_at': datetime.now().isoformat(),
                'interaction_type': feedback_record['interaction_type'],
                'rating': feedback_record['rating'],
                'context_summary': feedback_record.get('interaction_context', {})
            }
            
            memory_data[patient_id]['learned_patterns'].append(pattern)
            memory_data[patient_id]['last_updated'] = datetime.now().isoformat()
            
            # Keep only last 100 patterns
            if len(memory_data[patient_id]['learned_patterns']) > 100:
                memory_data[patient_id]['learned_patterns'] = \
                    memory_data[patient_id]['learned_patterns'][-100:]
            
            self._save_memory(memory_data)
            
        except Exception as e:
            logger.error(f"Error updating agent memory: {e}")
    
    def get_feedback_history(self, patient_id: str, limit: int = None) -> Dict:
        """
        Retrieve feedback history for a patient
        
        Args:
            patient_id: Patient identifier
            limit: Maximum number of feedback records to return
        
        Returns:
            Dict with feedback history
        """
        try:
            feedback_data = self._load_feedback()
            
            if patient_id not in feedback_data:
                return {
                    'success': True,
                    'patient_id': patient_id,
                    'feedback_history': [],
                    'total_count': 0
                }
            
            history = feedback_data[patient_id]['feedback_history']
            
            if limit:
                history = history[-limit:]
            
            return {
                'success': True,
                'patient_id': patient_id,
                'feedback_history': history,
                'total_count': len(feedback_data[patient_id]['feedback_history'])
            }
            
        except Exception as e:
            logger.error(f"Error retrieving feedback history: {e}")
            return {
                'success': False,
                'error': f'Failed to retrieve feedback: {str(e)}'
            }
    
    def get_interaction_preferences(self, patient_id: str) -> Dict:
        """
        Get learned interaction preferences for a patient
        
        Args:
            patient_id: Patient identifier
        
        Returns:
            Dict with interaction preferences
        """
        try:
            feedback_data = self._load_feedback()
            
            if patient_id not in feedback_data:
                return {
                    'success': False,
                    'error': 'Patient not found'
                }
            
            preferences = feedback_data[patient_id]['interaction_preferences']
            
            return {
                'success': True,
                'patient_id': patient_id,
                'preferences': preferences
            }
            
        except Exception as e:
            logger.error(f"Error retrieving preferences: {e}")
            return {
                'success': False,
                'error': f'Failed to retrieve preferences: {str(e)}'
            }
    
    def get_feedback_summary(self, patient_id: str) -> Dict:
        """
        Get a summary of patient feedback patterns
        
        Args:
            patient_id: Patient identifier
        
        Returns:
            Dict with feedback summary and insights
        """
        try:
            feedback_data = self._load_feedback()
            
            if patient_id not in feedback_data:
                return {
                    'success': False,
                    'error': 'Patient not found'
                }
            
            patient_feedback = feedback_data[patient_id]
            history = patient_feedback['feedback_history']
            
            # Calculate statistics
            positive_count = sum(1 for f in history if f['rating'] == 'positive')
            negative_count = sum(1 for f in history if f['rating'] == 'negative')
            neutral_count = sum(1 for f in history if f['rating'] == 'neutral')
            
            total = len(history)
            satisfaction_rate = (positive_count / total * 100) if total > 0 else 0
            
            # Count interaction types
            interaction_types = {}
            for feedback in history:
                itype = feedback.get('interaction_type', 'unknown')
                interaction_types[itype] = interaction_types.get(itype, 0) + 1
            
            # Most preferred and least preferred actions
            prefs = patient_feedback['interaction_preferences']
            most_liked = []
            least_liked = []
            
            for pref_type, pref_data in prefs.items():
                if isinstance(pref_data, dict):
                    if 'positive_interactions' in pref_data:
                        most_liked.extend(pref_data['positive_interactions'])
                    if 'negative_interactions' in pref_data:
                        least_liked.extend(pref_data['negative_interactions'])
            
            return {
                'success': True,
                'patient_id': patient_id,
                'total_feedback_count': total,
                'satisfaction_rate': round(satisfaction_rate, 2),
                'feedback_distribution': {
                    'positive': positive_count,
                    'negative': negative_count,
                    'neutral': neutral_count
                },
                'interaction_types': interaction_types,
                'most_liked_actions': list(set(most_liked))[:5],
                'least_liked_actions': list(set(least_liked))[:5],
                'learning_enabled': patient_feedback['adaptation_settings']['learning_enabled']
            }
            
        except Exception as e:
            logger.error(f"Error generating feedback summary: {e}")
            return {
                'success': False,
                'error': f'Failed to generate summary: {str(e)}'
            }
    
    def get_memory_insights(self, patient_id: str) -> Dict:
        """
        Get agent memory insights about a patient
        
        Args:
            patient_id: Patient identifier
        
        Returns:
            Dict with memory insights and learned patterns
        """
        try:
            memory_data = self._load_memory()
            
            if patient_id not in memory_data:
                return {
                    'success': True,
                    'patient_id': patient_id,
                    'learned_patterns': [],
                    'pattern_count': 0
                }
            
            patient_memory = memory_data[patient_id]
            patterns = patient_memory.get('learned_patterns', [])
            
            # Analyze patterns
            interaction_success = {}
            for pattern in patterns:
                itype = pattern.get('interaction_type', 'unknown')
                rating = pattern.get('rating', 'neutral')
                
                if itype not in interaction_success:
                    interaction_success[itype] = {
                        'positive': 0,
                        'negative': 0,
                        'neutral': 0
                    }
                
                interaction_success[itype][rating] += 1
            
            # Calculate success rates
            success_rates = {}
            for itype, counts in interaction_success.items():
                total = sum(counts.values())
                success_rate = (counts['positive'] / total * 100) if total > 0 else 0
                success_rates[itype] = round(success_rate, 2)
            
            return {
                'success': True,
                'patient_id': patient_id,
                'pattern_count': len(patterns),
                'last_updated': patient_memory.get('last_updated'),
                'learned_patterns': patterns[-10:],  # Last 10 patterns
                'interaction_success_rates': success_rates
            }
            
        except Exception as e:
            logger.error(f"Error retrieving memory insights: {e}")
            return {
                'success': False,
                'error': f'Failed to retrieve insights: {str(e)}'
            }
    
    def should_avoid_action(self, patient_id: str, interaction_type: str, 
                           action: str) -> Tuple[bool, Optional[str]]:
        """
        Determine if an action should be avoided based on feedback history
        
        Args:
            patient_id: Patient identifier
            interaction_type: Type of interaction
            action: Specific action to consider
        
        Returns:
            Tuple of (should_avoid: bool, reason: Optional[str])
        """
        try:
            feedback_data = self._load_feedback()
            
            if patient_id not in feedback_data:
                return False, None
            
            prefs = feedback_data[patient_id]['interaction_preferences']
            
            # Check if action is in negative interactions
            for pref_category in prefs.values():
                if isinstance(pref_category, dict):
                    if 'negative_interactions' in pref_category:
                        if action in pref_category['negative_interactions']:
                            return True, f"Patient previously disliked: {action}"
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error checking action avoidance: {e}")
            return False, None
    
    def should_recommend_action(self, patient_id: str, interaction_type: str,
                               action: str) -> Tuple[bool, Optional[str]]:
        """
        Determine if an action should be recommended based on positive feedback
        
        Args:
            patient_id: Patient identifier
            interaction_type: Type of interaction
            action: Specific action to consider
        
        Returns:
            Tuple of (should_recommend: bool, reason: Optional[str])
        """
        try:
            feedback_data = self._load_feedback()
            
            if patient_id not in feedback_data:
                return False, None
            
            prefs = feedback_data[patient_id]['interaction_preferences']
            
            # Check if action is in positive interactions
            for pref_category in prefs.values():
                if isinstance(pref_category, dict):
                    if 'positive_interactions' in pref_category:
                        if action in pref_category['positive_interactions']:
                            return True, f"Patient previously enjoyed: {action}"
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error checking action recommendation: {e}")
            return False, None
    
    def get_adaptation_weight(self, patient_id: str) -> float:
        """
        Get the weight/influence of feedback on agent decisions for this patient
        
        Args:
            patient_id: Patient identifier
        
        Returns:
            Float between 0.0 and 1.0 representing adaptation weight
        """
        try:
            feedback_data = self._load_feedback()
            
            if patient_id in feedback_data:
                return feedback_data[patient_id]['adaptation_settings'].get('feedback_weight', 0.7)
            
            return 0.7  # Default weight
            
        except Exception as e:
            logger.error(f"Error getting adaptation weight: {e}")
            return 0.7
    
    def clear_patient_feedback(self, patient_id: str) -> Dict:
        """
        Clear all feedback for a patient (admin function)
        
        Args:
            patient_id: Patient identifier
        
        Returns:
            Dict with result
        """
        try:
            feedback_data = self._load_feedback()
            
            if patient_id in feedback_data:
                del feedback_data[patient_id]
                self._save_feedback(feedback_data)
                
                memory_data = self._load_memory()
                if patient_id in memory_data:
                    del memory_data[patient_id]
                    self._save_memory(memory_data)
                
                logger.info(f"Cleared all feedback for patient {patient_id}")
                
                return {
                    'success': True,
                    'message': f'All feedback cleared for patient {patient_id}'
                }
            
            return {
                'success': True,
                'message': 'Patient has no feedback to clear'
            }
            
        except Exception as e:
            logger.error(f"Error clearing feedback: {e}")
            return {
                'success': False,
                'error': f'Failed to clear feedback: {str(e)}'
            }


# Global instance
feedback_service = FeedbackService()

