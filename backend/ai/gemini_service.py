"""
Gemini AI Integration Service
Uses Google's Gemini AI for intelligent patient monitoring and analysis
"""

import google.generativeai as genai
import os
import logging
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for integrating Google Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini AI service"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found in environment variables")
            self.model = None
            return
        
        try:
            genai.configure(api_key=self.api_key)
            # Use Gemini 2.5 Flash (stable, fast, free tier available)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Gemini AI service initialized successfully with gemini-2.5-flash")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            self.model = None
    
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
