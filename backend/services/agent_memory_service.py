"""
Agent Memory & Feedback Integration Service
Uses Google AI Generative AI SDK for intelligent feedback processing
Creates a subagent that integrates user feedback into main agent's decision making
"""

import google.generativeai as genai
import os
import logging
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
from .feedback_service import feedback_service

logger = logging.getLogger(__name__)


class AgentMemoryService:
    """
    Subagent service for integrating feedback into agent decision-making
    Uses Google AI SDK to analyze feedback and adapt behavior
    """
    
    def __init__(self):
        """Initialize agent memory service with Google AI"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.model_name = 'gemini-2.5-flash'
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"Agent Memory Service initialized with {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Google AI for memory service: {e}")
                self.model = None
        else:
            logger.warning("GOOGLE_API_KEY not set for Agent Memory Service")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.model is not None
    
    def analyze_feedback_patterns(self, patient_id: str) -> Dict:
        """
        Use AI to analyze feedback patterns and identify adaptation opportunities
        
        Args:
            patient_id: Patient identifier
        
        Returns:
            Dict with pattern analysis and recommendations
        """
        if not self.is_available():
            return self._fallback_pattern_analysis(patient_id)
        
        try:
            # Get patient feedback data
            feedback_summary = feedback_service.get_feedback_summary(patient_id)
            memory_insights = feedback_service.get_memory_insights(patient_id)
            history = feedback_service.get_feedback_history(patient_id, limit=20)
            
            if not feedback_summary.get('success') or feedback_summary.get('total_feedback_count', 0) == 0:
                return {
                    'success': True,
                    'patient_id': patient_id,
                    'message': 'Insufficient feedback data for pattern analysis',
                    'patterns': []
                }
            
            # Format feedback data for AI analysis
            feedback_summary_text = json.dumps(feedback_summary, indent=2)
            memory_text = json.dumps(memory_insights, indent=2)
            
            prompt = f"""You are an advanced AI feedback analyst for a pediatric patient care system.
Analyze the following patient feedback and interaction patterns to identify:
1. Key preferences and dislikes
2. Optimal interaction strategies
3. Adaptation opportunities for the main agent
4. Confidence level in recommendations

FEEDBACK SUMMARY:
{feedback_summary_text}

MEMORY INSIGHTS:
{memory_text}

Provide a JSON response with:
{{
    "key_preferences": ["preference1", "preference2"],
    "key_dislikes": ["dislike1", "dislike2"],
    "success_patterns": {{"interaction_type": "success_rate"}},
    "adaptation_strategies": ["strategy1", "strategy2"],
    "confidence_score": 0.0-1.0,
    "next_recommended_actions": ["action1", "action2"]
}}

Be concise and specific based on the actual data provided."""
            
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            return {
                'success': True,
                'patient_id': patient_id,
                'patterns': result,
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing feedback patterns: {e}")
            return self._fallback_pattern_analysis(patient_id)
    
    def generate_adaptive_decision(self, patient_id: str, interaction_type: str,
                                   available_actions: List[str],
                                   current_context: Dict) -> Dict:
        """
        Generate adaptive decision based on patient feedback history
        This is the core decision-making function that incorporates learned preferences
        
        Args:
            patient_id: Patient identifier
            interaction_type: Type of interaction (music, lighting, etc.)
            available_actions: List of possible actions to choose from
            current_context: Current patient state and environment
        
        Returns:
            Dict with recommended action and reasoning
        """
        if not self.is_available():
            return self._fallback_adaptive_decision(
                patient_id, interaction_type, available_actions, current_context
            )
        
        try:
            # Get patient preferences
            prefs_result = feedback_service.get_interaction_preferences(patient_id)
            memory_insights = feedback_service.get_memory_insights(patient_id)
            
            if not prefs_result.get('success'):
                # No feedback yet, return default
                return {
                    'success': True,
                    'recommended_action': available_actions[0] if available_actions else None,
                    'reasoning': 'No prior feedback available, selecting default action',
                    'adaptation_applied': False,
                    'confidence': 0.5
                }
            
            preferences = prefs_result.get('preferences', {})
            
            # Format data for AI
            prefs_json = json.dumps(preferences, indent=2)
            memory_json = json.dumps(memory_insights, indent=2)
            actions_json = json.dumps(available_actions, indent=2)
            context_json = json.dumps(current_context, indent=2)
            
            prompt = f"""You are an intelligent decision-making subagent for patient care.
Based on patient feedback history and current context, recommend the best action.

PATIENT ID: {patient_id}
INTERACTION TYPE: {interaction_type}

AVAILABLE ACTIONS:
{actions_json}

PATIENT PREFERENCES (from feedback):
{prefs_json}

PATIENT MEMORY (learned patterns):
{memory_json}

CURRENT CONTEXT:
{context_json}

Consider:
1. Actions previously rated positively should be prioritized
2. Actions previously rated negatively should be avoided
3. Current context should influence the choice
4. Be confident only if feedback is consistent

Return a JSON response:
{{
    "recommended_action": "specific action from available list",
    "confidence_score": 0.0-1.0,
    "reasoning": "brief explanation",
    "adaptation_applied": true/false,
    "alternative_actions": ["action2", "action3"]
}}"""
            
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            # Validate recommended action is in available list
            if result.get('recommended_action') not in available_actions:
                result['recommended_action'] = available_actions[0]
                logger.warning("AI recommended action not in available list, using default")
            
            return {
                'success': True,
                'patient_id': patient_id,
                'interaction_type': interaction_type,
                'decision': result,
                'decision_made_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in adaptive decision: {e}")
            return self._fallback_adaptive_decision(
                patient_id, interaction_type, available_actions, current_context
            )
    
    def predict_optimal_action(self, patient_id: str, interaction_type: str,
                              situation: str) -> Dict:
        """
        Predict the optimal action for a given situation based on feedback patterns
        
        Args:
            patient_id: Patient identifier
            interaction_type: Type of interaction
            situation: Description of the current situation
        
        Returns:
            Dict with prediction and confidence
        """
        if not self.is_available():
            return {'success': False, 'error': 'AI service not available'}
        
        try:
            # Get patient's memory and preferences
            prefs = feedback_service.get_interaction_preferences(patient_id)
            summary = feedback_service.get_feedback_summary(patient_id)
            
            prefs_json = json.dumps(prefs.get('preferences', {}), indent=2)
            summary_json = json.dumps(summary, indent=2)
            
            prompt = f"""Analyze the patient's feedback history and predict the optimal action.

SITUATION: {situation}

INTERACTION TYPE: {interaction_type}

PATIENT PREFERENCES:
{prefs_json}

FEEDBACK SUMMARY:
{summary_json}

Based on patterns, predict what the patient would prefer in this situation.

Return JSON:
{{
    "predicted_preference": "what patient likely prefers",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation based on patterns",
    "suggested_actions": ["action1", "action2"]
}}"""
            
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            return {
                'success': True,
                'patient_id': patient_id,
                'prediction': result
            }
            
        except Exception as e:
            logger.error(f"Error predicting optimal action: {e}")
            return {'success': False, 'error': str(e)}
    
    def explain_adaptation(self, patient_id: str, action: str, context: Dict) -> str:
        """
        Generate explanation for why an action was recommended based on feedback
        
        Args:
            patient_id: Patient identifier
            action: Action that was selected
            context: Current context information
        
        Returns:
            Human-readable explanation
        """
        if not self.is_available():
            return "Action selected based on patient preferences."
        
        try:
            # Get relevant preferences
            prefs = feedback_service.get_interaction_preferences(patient_id)
            history = feedback_service.get_feedback_history(patient_id, limit=10)
            
            prefs_json = json.dumps(prefs.get('preferences', {}), indent=2)
            history_json = json.dumps(history.get('feedback_history', []), indent=2)
            
            prompt = f"""Generate a brief, patient-friendly explanation for why this action was chosen.

ACTION: {action}
CONTEXT: {json.dumps(context)}

PATIENT PREFERENCES:
{prefs_json}

RECENT FEEDBACK:
{history_json}

Explain in 1-2 sentences why this is a good choice for this patient.
Keep it conversational and warm."""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error explaining adaptation: {e}")
            return "Action selected based on patient preferences."
    
    def evaluate_interaction_success(self, patient_id: str, interaction_type: str,
                                    action: str, actual_outcome: str) -> Dict:
        """
        Use AI to evaluate if an interaction was successful and suggest improvements
        
        Args:
            patient_id: Patient identifier
            interaction_type: Type of interaction
            action: Action that was taken
            actual_outcome: What actually happened
        
        Returns:
            Dict with evaluation and improvement suggestions
        """
        if not self.is_available():
            return {'success': False, 'error': 'AI service not available'}
        
        try:
            # Get historical context
            history = feedback_service.get_feedback_history(patient_id, limit=20)
            
            history_json = json.dumps(history.get('feedback_history', []), indent=2)
            
            prompt = f"""Evaluate this patient interaction and suggest improvements.

INTERACTION TYPE: {interaction_type}
ACTION TAKEN: {action}
ACTUAL OUTCOME: {actual_outcome}

PATIENT INTERACTION HISTORY:
{history_json}

Evaluate:
1. Was this a good choice for this patient?
2. What signals indicate success or failure?
3. What should be adjusted next time?

Return JSON:
{{
    "success_level": "high/medium/low",
    "reasoning": "why it worked or didn't work",
    "improvements": ["improvement1", "improvement2"],
    "suggested_alternative": "if this didn't work well, try this"
}}"""
            
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            return {
                'success': True,
                'patient_id': patient_id,
                'evaluation': result
            }
            
        except Exception as e:
            logger.error(f"Error evaluating interaction: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_adaptation_report(self, patient_id: str) -> Dict:
        """
        Generate comprehensive report of agent adaptations for this patient
        
        Args:
            patient_id: Patient identifier
        
        Returns:
            Dict with detailed adaptation report
        """
        if not self.is_available():
            return {'success': False, 'error': 'AI service not available'}
        
        try:
            summary = feedback_service.get_feedback_summary(patient_id)
            memory = feedback_service.get_memory_insights(patient_id)
            prefs = feedback_service.get_interaction_preferences(patient_id)
            
            if not summary.get('success'):
                return {
                    'success': True,
                    'patient_id': patient_id,
                    'report': 'No adaptation data available yet'
                }
            
            summary_json = json.dumps(summary, indent=2)
            memory_json = json.dumps(memory, indent=2)
            prefs_json = json.dumps(prefs.get('preferences', {}), indent=2)
            
            prompt = f"""Generate a concise adaptation report for this patient's care.

FEEDBACK SUMMARY:
{summary_json}

LEARNED PATTERNS:
{memory_json}

PREFERENCES:
{prefs_json}

Create a report that includes:
1. Overall adaptation progress
2. Key learned preferences
3. Most successful interaction strategies
4. Areas for further learning
5. Recommendations for medical staff

Format as readable text (not JSON)."""
            
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'patient_id': patient_id,
                'report': response.text.strip(),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating adaptation report: {e}")
            return {'success': False, 'error': str(e)}
    
    def _parse_json_response(self, text: str) -> Dict:
        """Parse JSON from AI response, handling markdown formatting"""
        try:
            text = text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from AI response")
            return {}
    
    def _fallback_pattern_analysis(self, patient_id: str) -> Dict:
        """Fallback pattern analysis without AI"""
        summary = feedback_service.get_feedback_summary(patient_id)
        
        return {
            'success': True,
            'patient_id': patient_id,
            'patterns': {
                'satisfaction_rate': summary.get('satisfaction_rate', 0),
                'key_preferences': summary.get('most_liked_actions', []),
                'key_dislikes': summary.get('least_liked_actions', [])
            }
        }
    
    def _fallback_adaptive_decision(self, patient_id: str, interaction_type: str,
                                   available_actions: List[str],
                                   current_context: Dict) -> Dict:
        """Fallback adaptive decision without AI"""
        
        # Check if any actions should be avoided
        for action in available_actions:
            should_avoid, reason = feedback_service.should_avoid_action(
                patient_id, interaction_type, action
            )
            if should_avoid:
                # Return remaining actions, preferring recommended ones
                remaining = [a for a in available_actions if a != action]
                if remaining:
                    for remaining_action in remaining:
                        should_recommend, rec_reason = feedback_service.should_recommend_action(
                            patient_id, interaction_type, remaining_action
                        )
                        if should_recommend:
                            return {
                                'success': True,
                                'recommended_action': remaining_action,
                                'reasoning': rec_reason,
                                'adaptation_applied': True,
                                'confidence': 0.8
                            }
        
        # Check for recommended actions
        for action in available_actions:
            should_recommend, reason = feedback_service.should_recommend_action(
                patient_id, interaction_type, action
            )
            if should_recommend:
                return {
                    'success': True,
                    'recommended_action': action,
                    'reasoning': reason,
                    'adaptation_applied': True,
                    'confidence': 0.8
                }
        
        # Default
        return {
            'success': True,
            'recommended_action': available_actions[0] if available_actions else None,
            'reasoning': 'No prior feedback, selecting default option',
            'adaptation_applied': False,
            'confidence': 0.5
        }


# Global instance
agent_memory_service = AgentMemoryService()

