"""
AI-Powered Health Report Analysis Routes
Generates comprehensive health reports using Gemini AI
"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from ..auth.decorators import login_required
from ..ai.gemini_service import gemini_service

logger = logging.getLogger(__name__)

report_analysis_bp = Blueprint('report_analysis', __name__, url_prefix='/api/report-analysis')


@report_analysis_bp.route('/generate/<patient_id>', methods=['GET'])
@login_required
def generate_ai_report(patient_id):
    """
    Generate AI-powered comprehensive health report analysis
    
    Args:
        patient_id: Patient identifier
        
    Returns:
        JSON with AI-generated report sections
    """
    try:
        import json
        import os
        
        logger.info(f"🤖 Generating AI health report for patient: {patient_id}")
        
        # Load room data from JSON file
        data_file = os.path.join(os.path.dirname(__file__), '../../backend/data/room_monitoring.json')
        with open(data_file, 'r') as f:
            rooms_data = json.load(f)
        
        # Find patient room data
        room_data = None
        for room_id, data in rooms_data.items():
            if data.get('patient_id') == patient_id:
                room_data = {
                    'patient_id': patient_id,
                    'patient_name': data.get('patient_name'),
                    'room_number': room_id,
                    'heart_rate': data.get('heart_rate'),
                    'temperature': data.get('temperature'),
                    'respiratory_rate': data.get('respiratory_rate'),
                    'oxygen_level': data.get('spo2'),
                    'blood_pressure': data.get('blood_pressure', 'N/A'),
                    'sleep_stage': data.get('sleep_stage'),
                    'pain_detected': data.get('pain_detected'),
                    'movement_level': data.get('movement_level'),
                    'ai_active': data.get('ai_is_active'),
                    'light_level': data.get('current_ai_settings', {}).get('light_level'),
                    'music_state': data.get('current_ai_settings', {}).get('music_state'),
                    'ai_actions': data.get('current_ai_settings', {})
                }
                break
        
        if not room_data:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Fetch health history from health_history_service
        from ..services import health_history_service
        history_records = health_history_service.get_patient_history(patient_id, hours=168)
        
        # Check if AI is available
        if not gemini_service or not gemini_service.is_available():
            return jsonify({
                'success': False,
                'error': 'AI service not available',
                'fallback': True
            }), 503
        
        # Generate AI analysis
        ai_report = generate_comprehensive_ai_report(room_data, history_records)
        
        logger.info(f"✅ AI report generated successfully for patient: {patient_id}")
        
        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'patient_name': room_data.get('patient_name'),
            'report': ai_report,
            'generated_at': datetime.now().isoformat(),
            'ai_provider': 'gemini-2.5-flash'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error generating AI report: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def generate_comprehensive_ai_report(room_data: dict, history_records: list) -> dict:
    """
    Generate comprehensive AI health report using Gemini
    
    Args:
        room_data: Current patient room data
        history_records: Historical health data records
        
    Returns:
        Dictionary with AI-generated report sections
    """
    
    # Calculate statistics from history
    stats = calculate_health_statistics(history_records)
    
    # Detect patterns and anomalies
    patterns = detect_health_patterns(history_records)
    
    # Build comprehensive prompt for Gemini
    prompt = f"""
You are an expert medical AI assistant creating a comprehensive health report for a hospitalized patient. 
Analyze the patient's current status and health history to provide detailed, professional medical insights.

## PATIENT INFORMATION
- Name: {room_data.get('patient_name', 'Unknown')}
- Room: {room_data.get('room_number', 'N/A')}
- Patient ID: {room_data.get('patient_id', 'N/A')}

## CURRENT VITAL SIGNS (Latest Reading)
- Heart Rate: {room_data.get('heart_rate', 'N/A')} bpm
- Body Temperature: {room_data.get('temperature', 'N/A')}°F
- Respiratory Rate: {room_data.get('respiratory_rate', 'N/A')} breaths/min
- SpO2 (Oxygen Saturation): {room_data.get('oxygen_level', 'N/A')}%
- Blood Pressure: {room_data.get('blood_pressure', 'N/A')}
- Sleep Stage: {room_data.get('sleep_stage', 'N/A')}
- Pain Status: {'Detected' if room_data.get('pain_detected') else 'None detected'}
- Activity Level: {room_data.get('movement_level', 'N/A')}

## HEALTH HISTORY STATISTICS (Last 7 Days)
Total Readings: {stats['total_readings']}

### Heart Rate:
- Average: {stats['heart_rate']['avg']:.1f} bpm
- Range: {stats['heart_rate']['min']:.0f} - {stats['heart_rate']['max']:.0f} bpm
- Trend: {stats['heart_rate']['trend']}

### Temperature:
- Average: {stats['temperature']['avg']:.1f}°F
- Range: {stats['temperature']['min']:.1f} - {stats['temperature']['max']:.1f}°F
- Trend: {stats['temperature']['trend']}

### Oxygen Saturation:
- Average: {stats['oxygen']['avg']:.1f}%
- Range: {stats['oxygen']['min']:.0f} - {stats['oxygen']['max']:.0f}%
- Trend: {stats['oxygen']['trend']}

## DETECTED PATTERNS
{format_patterns(patterns)}

## AI ENVIRONMENTAL CONTROL STATUS
- AI System Active: {'Yes' if room_data.get('ai_active') else 'No'}
- Light Level: {room_data.get('light_level', 'N/A')}%
- Music State: {room_data.get('music_state', 'Off')}
- AI Actions Reasoning: {room_data.get('ai_actions', {}).get('reasoning', 'N/A')}

---

Please generate a comprehensive medical report with the following sections:

1. **EXECUTIVE SUMMARY** (2-3 sentences)
   - Overall health status assessment
   - Key highlights and immediate concerns

2. **VITAL SIGNS ANALYSIS** (detailed paragraph)
   - Current readings interpretation
   - Comparison with normal ranges
   - Clinical significance of any abnormalities

3. **HEALTH TRENDS** (detailed paragraph)
   - Analysis of 7-day trends
   - Improvement or deterioration patterns
   - Stability assessment

4. **DETECTED CONCERNS** (bullet points)
   - List any abnormalities or concerning patterns
   - Severity assessment for each concern
   - Potential causes or contributing factors

5. **POSITIVE INDICATORS** (bullet points)
   - Healthy vital signs
   - Improving trends
   - Well-managed conditions

6. **SLEEP & RECOVERY** (paragraph)
   - Sleep quality assessment
   - Recovery indicators
   - Rest recommendations

7. **CLINICAL RECOMMENDATIONS** (detailed bullet points)
   - Immediate actions needed (if any)
   - Monitoring priorities
   - Preventive measures
   - Environmental adjustments

8. **RISK ASSESSMENT**
   - Overall risk level: Low/Medium/High/Critical
   - Specific risk factors
   - Risk mitigation strategies

9. **PROGNOSIS** (paragraph)
   - Short-term outlook
   - Expected recovery trajectory
   - Factors influencing outcomes

10. **AI SYSTEM EFFECTIVENESS** (paragraph)
    - How AI environmental controls are supporting recovery
    - Recommendations for AI adjustments

Format your response as JSON with this exact structure:
{{
    "executive_summary": "...",
    "vital_signs_analysis": "...",
    "health_trends": "...",
    "detected_concerns": ["concern1", "concern2", ...],
    "positive_indicators": ["indicator1", "indicator2", ...],
    "sleep_recovery": "...",
    "clinical_recommendations": ["rec1", "rec2", ...],
    "risk_assessment": {{
        "level": "Low/Medium/High/Critical",
        "factors": ["factor1", "factor2", ...],
        "mitigation": ["strategy1", "strategy2", ...]
    }},
    "prognosis": "...",
    "ai_effectiveness": "...",
    "confidence_score": 85
}}

Provide professional, evidence-based medical insights. Be specific and actionable.
"""
    
    try:
        # Generate report using Gemini
        response = gemini_service.model.generate_content(prompt)
        
        # Parse JSON response
        report_data = parse_gemini_json(response.text)
        
        logger.info(f"✅ Gemini AI report generated - Confidence: {report_data.get('confidence_score', 0)}%")
        
        return report_data
        
    except Exception as e:
        logger.error(f"❌ Error generating Gemini report: {e}")
        # Return fallback report
        return generate_fallback_report(room_data, stats, patterns)


def calculate_health_statistics(records: list) -> dict:
    """Calculate statistical analysis from health history records"""
    
    if not records:
        return {
            'total_readings': 0,
            'heart_rate': {'avg': 0, 'min': 0, 'max': 0, 'trend': 'No data'},
            'temperature': {'avg': 0, 'min': 0, 'max': 0, 'trend': 'No data'},
            'oxygen': {'avg': 0, 'min': 0, 'max': 0, 'trend': 'No data'}
        }
    
    heart_rates = [r['heart_rate'] for r in records if r.get('heart_rate')]
    temps = [r['temperature'] for r in records if r.get('temperature')]
    oxygen = [r['oxygen_level'] for r in records if r.get('oxygen_level')]
    
    def calc_trend(values):
        if len(values) < 2:
            return 'Insufficient data'
        recent = sum(values[:len(values)//3]) / (len(values)//3) if len(values) >= 3 else values[0]
        older = sum(values[-len(values)//3:]) / (len(values)//3) if len(values) >= 3 else values[-1]
        diff = recent - older
        if abs(diff) < 2:
            return 'Stable'
        return 'Increasing' if diff > 0 else 'Decreasing'
    
    return {
        'total_readings': len(records),
        'heart_rate': {
            'avg': sum(heart_rates) / len(heart_rates) if heart_rates else 0,
            'min': min(heart_rates) if heart_rates else 0,
            'max': max(heart_rates) if heart_rates else 0,
            'trend': calc_trend(heart_rates)
        },
        'temperature': {
            'avg': sum(temps) / len(temps) if temps else 0,
            'min': min(temps) if temps else 0,
            'max': max(temps) if temps else 0,
            'trend': calc_trend(temps)
        },
        'oxygen': {
            'avg': sum(oxygen) / len(oxygen) if oxygen else 0,
            'min': min(oxygen) if oxygen else 0,
            'max': max(oxygen) if oxygen else 0,
            'trend': calc_trend(oxygen)
        }
    }


def detect_health_patterns(records: list) -> dict:
    """Detect patterns and anomalies in health data"""
    
    if not records or len(records) < 10:
        return {
            'anomalies': [],
            'stable_periods': 0,
            'concerning_periods': 0
        }
    
    anomalies = []
    concerning = 0
    stable = 0
    
    for record in records:
        hr = record.get('heart_rate', 0)
        temp = record.get('temperature', 0)
        o2 = record.get('oxygen_level', 0)
        
        is_concerning = False
        
        # Check for abnormal vitals
        if hr < 60 or hr > 100:
            anomalies.append(f"Abnormal heart rate: {hr} bpm")
            is_concerning = True
        if temp < 97 or temp > 99.5:
            anomalies.append(f"Abnormal temperature: {temp}°F")
            is_concerning = True
        if o2 < 95:
            anomalies.append(f"Low oxygen: {o2}%")
            is_concerning = True
        
        if is_concerning:
            concerning += 1
        else:
            stable += 1
    
    # Remove duplicates
    anomalies = list(set(anomalies))[:5]  # Limit to 5 unique anomalies
    
    return {
        'anomalies': anomalies,
        'stable_periods': stable,
        'concerning_periods': concerning,
        'stability_ratio': stable / len(records) if records else 0
    }


def format_patterns(patterns: dict) -> str:
    """Format patterns dictionary into readable text"""
    
    lines = []
    lines.append(f"- Stable readings: {patterns['stable_periods']} out of {patterns['stable_periods'] + patterns['concerning_periods']}")
    lines.append(f"- Stability ratio: {patterns['stability_ratio']*100:.1f}%")
    
    if patterns['anomalies']:
        lines.append("- Detected anomalies:")
        for anomaly in patterns['anomalies']:
            lines.append(f"  • {anomaly}")
    else:
        lines.append("- No significant anomalies detected")
    
    return '\n'.join(lines)


def parse_gemini_json(response_text: str) -> dict:
    """Parse JSON from Gemini response, handling markdown code blocks"""
    
    import json
    import re
    
    # Remove markdown code blocks if present
    text = response_text.strip()
    
    # Try to extract JSON from code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', text, re.DOTALL)
    if json_match:
        text = json_match.group(1)
    
    # Try direct parsing
    try:
        return json.loads(text)
    except:
        # Try finding JSON object
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        
        logger.error("Failed to parse JSON from Gemini response")
        raise ValueError("Could not parse Gemini response as JSON")


def generate_fallback_report(room_data: dict, stats: dict, patterns: dict) -> dict:
    """Generate basic report when AI is unavailable"""
    
    return {
        "executive_summary": f"Patient {room_data.get('patient_name')} in room {room_data.get('room_number')} - Basic vital signs monitoring active. {stats['total_readings']} readings collected.",
        "vital_signs_analysis": f"Current heart rate: {room_data.get('heart_rate')} bpm, Temperature: {room_data.get('temperature')}°F, SpO2: {room_data.get('oxygen_level')}%.",
        "health_trends": f"Heart rate trend: {stats['heart_rate']['trend']}, Temperature trend: {stats['temperature']['trend']}",
        "detected_concerns": patterns['anomalies'] if patterns['anomalies'] else ["No AI analysis available"],
        "positive_indicators": ["Continuous monitoring active", "Data being collected"],
        "sleep_recovery": "AI analysis not available for detailed sleep assessment.",
        "clinical_recommendations": ["Continue monitoring", "Review trends regularly"],
        "risk_assessment": {
            "level": "Unknown",
            "factors": ["AI analysis required"],
            "mitigation": ["Enable AI service for detailed assessment"]
        },
        "prognosis": "AI analysis required for detailed prognosis.",
        "ai_effectiveness": "AI service not available.",
        "confidence_score": 30
    }
