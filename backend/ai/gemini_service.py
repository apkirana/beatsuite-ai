"""
Gemini AI Integration Service
Uses Google's Gemini AI for intelligent patient monitoring and analysis
"""

import google.generativeai as genai
import os
import logging
from typing import Dict, List, Optional
import json
from datetime import datetime, time
import re

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for integrating Google Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini AI service"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found in environment variables")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                # Use Gemini 2.5 Flash (stable, fast, free tier available)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("Gemini AI service initialized successfully with gemini-2.5-flash")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini AI: {e}")
                self.model = None
        
        # Load adaptive rules
        self.adaptive_rules = self.load_adaptive_rules()
    
    def load_adaptive_rules(self):
        """Load adaptive rules from configuration file"""
        rules_path = os.path.join(os.path.dirname(__file__), '../config/adaptive_rules.json')
        try:
            with open(rules_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Adaptive rules file not found, using fallback rules")
            return {"adaptive_rules": []}
        except Exception as e:
            logger.error(f"Error loading adaptive rules: {e}")
            return {"adaptive_rules": []}
    
    def is_available(self) -> bool:
        """Check if Gemini AI is available"""
        return self.model is not None
    
    def analyze_patient_vitals(self, patient_data: Dict) -> Dict:
        """
        Analyze patient vital signs and provide intelligent insights
        
        Args:
            patient_data: Dictionary containing patient vitals and state
            
        Returns:
            Dictionary with analysis results and recommendations
        """
        if not self.is_available():
            return self._fallback_analysis(patient_data)
        
        try:
            prompt = f"""
You are a medical AI assistant analyzing patient vital signs in a hospital room monitoring system.

Patient Data:
- Heart Rate: {patient_data.get('heart_rate', 'N/A')} bpm
- Temperature: {patient_data.get('temperature', 'N/A')}°F
- Respiratory Rate: {patient_data.get('respiratory_rate', 'N/A')}/min
- SpO2 (Oxygen Saturation): {patient_data.get('oxygen_level', 'N/A')}%
- Blood Pressure: {patient_data.get('blood_pressure', 'N/A')}
- Sleep Stage: {patient_data.get('sleep_stage', 'N/A')}
- Pain Detected: {patient_data.get('pain_detected', False)}
- Movement Level: {patient_data.get('movement_level', 'N/A')}

Please provide:
1. Overall health status assessment (1-2 sentences)
2. Any concerns or abnormalities detected (list key points)
3. Recommended actions (if any)
4. Risk level (Low/Medium/High)

Format your response as JSON:
{{
    "status": "brief status summary",
    "concerns": ["concern1", "concern2"],
    "recommendations": ["recommendation1", "recommendation2"],
    "risk_level": "Low/Medium/High",
    "confidence": "percentage"
}}
"""
            
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            return {
                'success': True,
                'analysis': result,
                'ai_provider': 'gemini-pro'
            }
            
        except Exception as e:
            logger.error(f"Error in Gemini analysis: {e}")
            return self._fallback_analysis(patient_data)
    
    def generate_health_summary(self, patient_name: str, room_data: Dict) -> str:
        """
        Generate a natural language health summary for the patient
        
        Args:
            patient_name: Name of the patient
            room_data: Complete room data including vitals and environment
            
        Returns:
            Human-readable health summary
        """
        if not self.is_available():
            return self._fallback_summary(patient_name, room_data)
        
        try:
            prompt = f"""
Generate a brief, professional medical status report for {patient_name}.

Current Status:
- Vitals: HR {room_data.get('heart_rate')} bpm, Temp {room_data.get('temperature')}°F, 
  RR {room_data.get('respiratory_rate')}/min, SpO2 {room_data.get('oxygen_level')}%
- Sleep Stage: {room_data.get('sleep_stage')}
- Pain: {'Yes' if room_data.get('pain_detected') else 'No'}
- Environment: Light {room_data.get('current_ai_settings', {}).get('light_brightness', 'N/A')}%, 
  Music {room_data.get('current_ai_settings', {}).get('music_volume', 'N/A')}%

Write a 2-3 sentence professional summary suitable for medical staff handoff.
"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return self._fallback_summary(patient_name, room_data)
    
    def predict_health_trends(self, historical_data: List[Dict]) -> Dict:
        """
        Analyze historical patient data and predict potential issues
        
        Args:
            historical_data: List of patient data points over time
            
        Returns:
            Predictions and trend analysis
        """
        if not self.is_available():
            return {'success': False, 'message': 'Gemini AI not available'}
        
        try:
            data_summary = "\n".join([
                f"Time {i+1}: HR={d.get('heart_rate')}, Temp={d.get('temperature')}, "
                f"SpO2={d.get('oxygen_level')}, Sleep={d.get('sleep_stage')}"
                for i, d in enumerate(historical_data[-10:])  # Last 10 readings
            ])
            
            prompt = f"""
Analyze this patient's vital sign trends over recent monitoring periods:

{data_summary}

Identify:
1. Any concerning trends (increasing/decreasing patterns)
2. Potential health risks in the next few hours
3. Recommended preventive actions

Format as JSON:
{{
    "trends": ["trend1", "trend2"],
    "predictions": ["prediction1"],
    "preventive_actions": ["action1"],
    "urgency": "Low/Medium/High"
}}
"""
            
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            return {
                'success': True,
                'predictions': result
            }
            
        except Exception as e:
            logger.error(f"Error in trend prediction: {e}")
            return {'success': False, 'error': str(e)}
    
    def optimize_environment(self, patient_data: Dict, current_environment: Dict) -> Dict:
        """
        Use AI to suggest optimal room environment settings
        
        Args:
            patient_data: Current patient vitals and state
            current_environment: Current room settings
            
        Returns:
            Optimized environment recommendations
        """
        if not self.is_available():
            return self._fallback_environment(patient_data)
        
        try:
            prompt = f"""
As a medical AI optimizing patient room environment:

Patient Status:
- Sleep Stage: {patient_data.get('sleep_stage')}
- Heart Rate: {patient_data.get('heart_rate')} bpm
- Pain Detected: {patient_data.get('pain_detected')}
- Movement: {patient_data.get('movement_level')}

Current Environment:
- Light: {current_environment.get('light_brightness')}%
- Music: {current_environment.get('music_volume')}%

Suggest optimal settings to promote healing and comfort. Return JSON:
{{
    "light_brightness": 0-100,
    "light_color": "warm/cool/neutral",
    "music_volume": 0-100,
    "music_type": "relaxing/nature/silence",
    "reasoning": "brief explanation"
}}
"""
            
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            return {
                'success': True,
                'recommendations': result,
                'ai_provider': 'gemini-pro'
            }
            
        except Exception as e:
            logger.error(f"Error optimizing environment: {e}")
            return self._fallback_environment(patient_data)
    
    def optimize_environment_adaptive(self, patient_data: Dict, current_environment: Dict) -> Dict:
        """
        Enhanced environment optimization using adaptive rules
        
        Args:
            patient_data: Current patient vitals and state
            current_environment: Current room settings
            
        Returns:
            Optimized environment recommendations using adaptive rules
        """
        try:
            current_time = datetime.now().time()
            
            # First, check adaptive rules
            matched_rule = self.evaluate_adaptive_rules(patient_data, current_time)
            
            if matched_rule:
                logger.info(f"Adaptive rule matched: {matched_rule['scenario']} (Rule: {matched_rule['rule_id']})")
                
                # Parse response ranges (e.g., "15-25%" -> random value in range)
                parsed_response = self._parse_response_ranges(matched_rule['response'])
                
                return {
                    'success': True,
                    'recommendations': parsed_response,
                    'ai_provider': 'adaptive-rules',
                    'rule_matched': matched_rule['scenario'],
                    'rule_id': matched_rule['rule_id'],
                    'reasoning': matched_rule['response'].get('reasoning', 'Adaptive rule applied')
                }
            
            # Fall back to Gemini AI if no rules match
            logger.info("No adaptive rules matched, falling back to Gemini AI")
            return self.optimize_environment(patient_data, current_environment)
            
        except Exception as e:
            logger.error(f"Error in adaptive optimization: {e}")
            return self.optimize_environment(patient_data, current_environment)
    
    def evaluate_adaptive_rules(self, patient_data: Dict, current_time: time) -> Optional[Dict]:
        """Evaluate adaptive rules and return matching rule"""
        
        # Sort rules by priority (lower number = higher priority)
        sorted_rules = sorted(
            self.adaptive_rules.get('adaptive_rules', []), 
            key=lambda x: x.get('priority', 5)
        )
        
        for rule in sorted_rules:
            try:
                if self.evaluate_condition(rule['condition'], patient_data, current_time):
                    return {
                        'scenario': rule['scenario'],
                        'response': rule['ai_response'],
                        'rule_id': rule.get('id', 'unknown'),
                        'priority': rule.get('priority', 5)
                    }
            except Exception as e:
                logger.warning(f"Error evaluating rule {rule.get('id', 'unknown')}: {e}")
                continue
        
        return None
    
    def evaluate_condition(self, condition_string: str, data: Dict, current_time: time) -> bool:
        """
        Safely evaluate rule conditions
        
        Args:
            condition_string: Rule condition (e.g., "heart_rate > 100 AND movement > 0.6")
            data: Patient data dictionary
            current_time: Current time for time-based conditions
            
        Returns:
            Boolean indicating if condition is met
        """
        try:
            # Extract values safely
            heart_rate = float(data.get('heart_rate', 0))
            movement = float(data.get('movement', 0))
            spo2 = float(data.get('spo2', 100))
            temperature = float(data.get('temperature', 98.6))
            
            # Handle special conditions first
            if 'time BETWEEN' in condition_string:
                return self.evaluate_time_condition(condition_string, current_time)
            
            if 'SPIKE DETECTED' in condition_string:
                return self.detect_movement_spike(data)
            
            if 'BETWEEN' in condition_string and 'time' not in condition_string:
                return self.evaluate_range_condition(condition_string, data)
            
            # Replace variables with values for basic conditions
            condition = condition_string
            condition = condition.replace('heart_rate', str(heart_rate))
            condition = condition.replace('movement', str(movement))
            condition = condition.replace('spo2', str(spo2))
            condition = condition.replace('temperature', str(temperature))
            condition = condition.replace('AND', ' and ')
            condition = condition.replace('OR', ' or ')
            
            # Safely evaluate the condition
            # Only allow safe operations
            allowed_chars = set('0123456789.<>=! and or()')
            if all(c in allowed_chars or c.isspace() for c in condition):
                return eval(condition)
            else:
                logger.warning(f"Unsafe condition detected: {condition_string}")
                return False
                
        except Exception as e:
            logger.warning(f"Error evaluating condition '{condition_string}': {e}")
            return False
    
    def evaluate_time_condition(self, condition: str, current_time: time) -> bool:
        """Evaluate time-based conditions like 'time BETWEEN 22:00 AND 06:00'"""
        try:
            time_match = re.search(r'time BETWEEN (\d{2}:\d{2}) AND (\d{2}:\d{2})', condition)
            if not time_match:
                return False
            
            start_str, end_str = time_match.groups()
            start_time = datetime.strptime(start_str, '%H:%M').time()
            end_time = datetime.strptime(end_str, '%H:%M').time()
            
            # Handle overnight ranges (e.g., 22:00 to 06:00)
            if start_time > end_time:
                return current_time >= start_time or current_time <= end_time
            else:
                return start_time <= current_time <= end_time
                
        except Exception as e:
            logger.warning(f"Error evaluating time condition: {e}")
            return False
    
    def evaluate_range_condition(self, condition: str, data: Dict) -> bool:
        """Evaluate range conditions like 'heart_rate BETWEEN 65 AND 85'"""
        try:
            # Match pattern: variable BETWEEN min AND max
            range_match = re.search(r'(\w+) BETWEEN ([\d.]+) AND ([\d.]+)', condition)
            if not range_match:
                return False
            
            variable, min_val, max_val = range_match.groups()
            value = float(data.get(variable, 0))
            min_val = float(min_val)
            max_val = float(max_val)
            
            return min_val <= value <= max_val
            
        except Exception as e:
            logger.warning(f"Error evaluating range condition: {e}")
            return False
    
    def detect_movement_spike(self, data: Dict) -> bool:
        """Detect sudden movement spikes during sleep phases"""
        try:
            current_movement = float(data.get('movement', 0))
            current_time = datetime.now().time()
            
            # Consider it a spike if high movement during typical sleep hours
            sleep_hours = (time(22, 0) <= current_time or current_time <= time(6, 0))
            
            # Movement spike: high movement (>0.5) during sleep hours
            return sleep_hours and current_movement > 0.5
            
        except Exception as e:
            logger.warning(f"Error detecting movement spike: {e}")
            return False
    
    def _parse_response_ranges(self, response: Dict) -> Dict:
        """Parse response ranges like '15-25%' into actual values"""
        parsed = response.copy()
        
        for key, value in response.items():
            if isinstance(value, str) and '-' in value and '%' in value:
                try:
                    # Extract range like "15-25%"
                    range_part = value.replace('%', '')
                    if '-' in range_part:
                        min_val, max_val = map(int, range_part.split('-'))
                        # Use middle of range for consistency
                        parsed[key] = (min_val + max_val) // 2
                    else:
                        parsed[key] = int(range_part)
                except:
                    pass  # Keep original value if parsing fails
        
        return parsed
    
    def chat_assistant(self, user_question: str, context: Dict) -> str:
        """
        Chat interface for medical staff to ask questions about patients
        
        Args:
            user_question: Question from medical staff
            context: Relevant patient data context
            
        Returns:
            AI-generated answer
        """
        if not self.is_available():
            return "AI assistant is currently unavailable. Please check system configuration."
        
        try:
            prompt = f"""
You are a medical AI assistant helping hospital staff monitor patients.

Context:
Patient: {context.get('patient_name', 'Unknown')}
Room: {context.get('room_number', 'Unknown')}
Current Vitals: HR {context.get('heart_rate')}bpm, Temp {context.get('temperature')}°F, 
SpO2 {context.get('oxygen_level')}%, Sleep: {context.get('sleep_stage')}

Staff Question: {user_question}

Provide a professional, concise answer (2-3 sentences). Be helpful but remind them to consult with physicians for critical decisions.
"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error in chat assistant: {e}")
            return f"I encountered an error processing your question. Please try again or contact support."
    
    def _parse_json_response(self, text: str) -> Dict:
        """Parse JSON from Gemini response, handling markdown formatting"""
        try:
            # Remove markdown code blocks if present
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
            logger.warning("Failed to parse JSON from Gemini response")
            return {}
    
    def _fallback_analysis(self, patient_data: Dict) -> Dict:
        """Fallback analysis when Gemini is unavailable"""
        hr = patient_data.get('heart_rate', 70)
        temp = patient_data.get('temperature', 98.6)
        spo2 = patient_data.get('oxygen_level', 98)
        
        concerns = []
        risk_level = "Low"
        
        if hr > 100 or hr < 60:
            concerns.append(f"Heart rate {hr} bpm is outside normal range")
            risk_level = "Medium"
        if temp > 99.5 or temp < 97:
            concerns.append(f"Temperature {temp}°F may indicate fever or hypothermia")
            risk_level = "Medium"
        if spo2 < 95:
            concerns.append(f"Oxygen saturation {spo2}% is below optimal level")
            risk_level = "High"
        
        return {
            'success': True,
            'analysis': {
                'status': 'Monitoring patient vitals' if not concerns else 'Attention required',
                'concerns': concerns if concerns else ['No immediate concerns detected'],
                'recommendations': ['Continue monitoring'] if not concerns else ['Alert medical staff'],
                'risk_level': risk_level,
                'confidence': '85%'
            },
            'ai_provider': 'fallback-rules'
        }
    
    def _fallback_summary(self, patient_name: str, room_data: Dict) -> str:
        """Fallback summary when Gemini is unavailable"""
        return f"{patient_name} is currently {room_data.get('sleep_stage', 'resting')}. " \
               f"Vitals are stable with HR {room_data.get('heart_rate')}bpm, " \
               f"SpO2 {room_data.get('oxygen_level')}%. Continuing routine monitoring."
    
    def _fallback_environment(self, patient_data: Dict) -> Dict:
        """Fallback environment optimization"""
        sleep_stage = patient_data.get('sleep_stage', 'AWAKE')
        
        if 'SLEEP' in sleep_stage or 'REM' in sleep_stage:
            settings = {
                'light_brightness': 10,
                'light_color': 'warm',
                'music_volume': 15,
                'music_type': 'nature',
                'reasoning': 'Low lighting and gentle sounds for sleep'
            }
        else:
            settings = {
                'light_brightness': 50,
                'light_color': 'neutral',
                'music_volume': 25,
                'music_type': 'relaxing',
                'reasoning': 'Moderate settings for waking hours'
            }
        
        return {
            'success': True,
            'recommendations': settings,
            'ai_provider': 'fallback-rules'
        }


# Global instance
gemini_service = GeminiService()
