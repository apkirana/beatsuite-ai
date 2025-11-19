"""
Smart Assistant API Routes
Handles AI chatbot queries for patient rooms
"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from ..auth.decorators import login_required

logger = logging.getLogger(__name__)

assistant_bp = Blueprint('assistant', __name__, url_prefix='/api/assistant')

# Import Gemini AI service
try:
    from ..ai.gemini_service import gemini_service
    AI_AVAILABLE = gemini_service.is_available()
    logger.info(f"Gemini AI available: {AI_AVAILABLE}")
except ImportError as e:
    logger.warning(f"Gemini AI service not available: {e}")
    gemini_service = None
    AI_AVAILABLE = False


@assistant_bp.route('/query', methods=['POST'])
@login_required
def handle_query():
    """Handle assistant query with AI response and conversation history"""
    try:
        data = request.json
        room_id = data.get('room_id')
        query = data.get('query')
        context = data.get('context', {})
        conversation_history = data.get('conversation_history', [])
        
        logger.info(f"🤖 Assistant query - Room: {room_id}, Query: '{query}', History: {len(conversation_history)} msgs")
        
        if not room_id or not query:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Generate AI response with conversation context
        response = generate_assistant_response(query, context, conversation_history)
        
        logger.info(f"✅ Response generated - Room: {room_id}, Length: {len(response)} chars")
        
        return jsonify({
            'response': response,
            'room_id': room_id,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Assistant query error: {e}", exc_info=True)
        return jsonify({'error': 'Failed to process query'}), 500


def generate_gemini_response(query: str, patient_name: str, room_number: str, vitals: dict, 
                             sleep_stage: str, pain_detected: bool, ai_active: bool, environment: dict, 
                             conversation_history: list = None) -> str:
    """Generate natural conversational response using Gemini AI with advanced medical reasoning and memory"""
    try:
        if conversation_history is None:
            conversation_history = []
        
        # Format conversation history for context
        history_text = ""
        if conversation_history:
            history_text = "\n\n💬 CONVERSATION HISTORY (for context):\n"
            history_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for msg in conversation_history[-6:]:  # Last 3 exchanges
                role = "User" if msg['role'] == 'user' else "You"
                history_text += f"{role}: {msg['content']}\n"
            history_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        # Calculate additional insights
        hr = vitals.get('heart_rate', 0)
        temp = vitals.get('temperature', 0)
        spo2 = vitals.get('spo2', 0)
        rr = vitals.get('respiratory_rate', 0)
        
        # Health status assessment
        hr_status = "normal" if 60 <= hr <= 100 else "elevated" if hr > 100 else "low" if hr > 0 else "unknown"
        temp_status = "normal" if 97 <= temp <= 99 else "elevated" if temp > 99 else "low" if temp > 0 else "unknown"
        spo2_status = "excellent" if spo2 >= 98 else "good" if spo2 >= 95 else "concerning" if spo2 > 0 else "unknown"
        rr_status = "normal" if 12 <= rr <= 20 else "elevated" if rr > 20 else "low" if rr > 0 else "unknown"
        
        # Overall health indicator
        critical_signs = []
        if hr_status in ["elevated", "low"]: critical_signs.append("heart rate")
        if temp_status == "elevated": critical_signs.append("fever")
        if spo2_status == "concerning": critical_signs.append("oxygen levels")
        if pain_detected: critical_signs.append("pain indicators")
        
        overall_status = "Critical - immediate attention needed" if len(critical_signs) >= 2 else \
                        "Needs monitoring" if len(critical_signs) == 1 else \
                        "Stable and comfortable"
        
        # Music description
        music_map = {
            'calm_ambient': 'Calm Ambient (peaceful nature sounds)',
            'soft_instrumental': 'Soft Instrumental (gentle piano)',
            'disney_classics': 'Disney Classics (familiar happy tunes)',
            'nature_sounds': 'Nature Sounds (rain, ocean waves)',
            'white_noise': 'White Noise (consistent soothing sound)',
            'lullabies': 'Lullabies (gentle sleep music)',
            'classical': 'Classical Music (Mozart, Beethoven)',
            'none': 'No music currently playing'
        }
        music_desc = music_map.get(environment.get('music_playlist_id', 'none'), 'Unknown music')
        
        prompt = f"""You are Dr. AI, an advanced medical AI assistant in Beat Suite AI - a smart pediatric oncology monitoring system at Prinses Máxima Centrum. You have deep medical knowledge and can interpret vital signs, recognize patterns, and provide actionable insights to healthcare staff and families.

🏥 PATIENT PROFILE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: {patient_name}
Location: {room_number}
Overall Status: {overall_status}

📊 VITAL SIGNS (Real-time):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Heart Rate: {hr} BPM → {hr_status.upper()} (Ref: 60-100)
• Body Temperature: {temp}°F → {temp_status.upper()} (Ref: 97-99°F)  
• Oxygen Saturation (SpO2): {spo2}% → {spo2_status.upper()} (Ref: 95-100%)
• Respiratory Rate: {rr} breaths/min → {rr_status.upper()} (Ref: 12-20)

🛌 CURRENT STATE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Sleep Stage: {sleep_stage.upper().replace('_', ' ')}
• Pain Detected: {'⚠️ YES - Patient showing discomfort signs' if pain_detected else '✅ NO - Patient appears comfortable'}
• Critical Concerns: {', '.join(critical_signs) if critical_signs else 'None detected'}

🤖 AI ENVIRONMENT CONTROL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: {'🟢 ACTIVE - AI is optimizing room environment based on patient needs' if ai_active else '🔴 MANUAL - Staff controlling environment'}
• Lighting: {int(environment.get('light_brightness', 0.5) * 100)}% brightness, Color: {environment.get('light_hex_color', '#FFFFFF')}
• Audio: {music_desc} at {int(environment.get('music_volume', 0) * 100)}% volume
• AI Reasoning: {environment.get('ai_reasoning', 'Maintaining optimal conditions')}

{history_text}
👤 CURRENT USER QUESTION:
"{query}"

🎯 YOUR COMMUNICATION STYLE:
• **Sound human and warm** - Use natural conversational language, like talking to a colleague
• **Be personable** - Add warmth: "I'm happy to share that..." or "Let me check on that for you..."
• **Use contractions** - Say "they're" not "they are", "I'll" not "I will"
• **Show care** - "I've been monitoring..." or "I noticed that..."
• **Be reassuring** - When things are good, say so warmly!
• **Stay professional but friendly** - Like a caring nurse, not a textbook

📋 RESPONSE GUIDELINES:
• If vitals are good → Be reassuring: "Great news! Everything's looking stable..."
• If vitals are concerning → Be caring but direct: "I've noticed [concern], let's address this..."
• If greeting → Be warm: "Hi there! I'm here to help with [patient_name]..."
• If asked "how is patient" → Paint the picture: "She's resting comfortably right now..."
• If technical question → Explain like a friend: "So basically what's happening is..."
• If asked about AI → Be conversational: "I've been adjusting things to help them rest better..."
• Keep responses SHORT and NATURAL - 1-3 sentences, like you're chatting!

⚠️ CRITICAL: Respond like you're speaking to someone, NOT writing a report. Use everyday language, be warm and personable!

Generate your natural, conversational response:"""

        response = gemini_service.model.generate_content(prompt)
        answer = response.text.strip()
        
        # Clean up markdown formatting
        answer = answer.replace('**', '').replace('*', '').replace('###', '').replace('##', '')
        
        logger.info(f"✅ Gemini AI response: {len(answer)} chars - Status: {overall_status}")
        return answer
        
    except Exception as e:
        logger.error(f"❌ Gemini generation error: {e}")
        return None


def generate_assistant_response(query: str, context: dict, conversation_history: list = None) -> str:
    """Generate context-aware AI response using Gemini with conversation history or fallback patterns"""
    
    patient_name = context.get('patient_name', 'the patient')
    room_number = context.get('room_number', 'this room')
    vitals = context.get('vitals', {})
    sleep_stage = context.get('sleep_stage', 'unknown')
    pain_detected = context.get('pain_detected', False)
    ai_active = context.get('ai_active', False)
    environment = context.get('environment', {})
    
    if conversation_history is None:
        conversation_history = []
    
    # Try using Gemini AI for natural conversation
    if AI_AVAILABLE and gemini_service:
        try:
            ai_response = generate_gemini_response(query, patient_name, room_number, vitals, sleep_stage, pain_detected, ai_active, environment, conversation_history)
            if ai_response:
                logger.info(f"✅ Using Gemini AI response (with {len(conversation_history)} history msgs)")
                return ai_response
        except Exception as e:
            logger.warning(f"⚠️ Gemini AI failed, using fallback: {e}")
    
    # Fallback to pattern matching
    logger.info(f"📝 Using pattern-based response")
    query_lower = query.lower()
    
    # Greeting
    if any(word in query_lower for word in ['hi', 'hello', 'hey']):
        return f"Hi there! I'm here to help you with {patient_name}'s care. What would you like to know?"
    
    # Patient status - more flexible matching
    if any(word in query_lower for word in ['how is', 'status', 'condition', 'doing', 'feeling', 'patient']):
        hr = vitals.get('heart_rate', 0)
        temp = vitals.get('temperature', 0)
        spo2 = vitals.get('spo2', 0)
        rr = vitals.get('respiratory_rate', 0)
        
        status = 'doing well and resting comfortably'
        if pain_detected:
            status = 'showing signs of discomfort'
        elif hr > 100 or spo2 < 95:
            status = 'needs some attention'
        elif hr < 50:
            status = 'showing a low heart rate'
        
        sleep_desc = sleep_stage.replace('_', ' ')
        return f"{patient_name}'s {status} right now. Their heart rate's at {hr} BPM, temp is {temp}°F, and oxygen levels are at {spo2}%. They're currently in {sleep_desc} sleep."
    
    # Vitals specific
    if 'vital' in query_lower:
        hr = vitals.get('heart_rate', 0)
        temp = vitals.get('temperature', 0)
        rr = vitals.get('respiratory_rate', 0)
        spo2 = vitals.get('spo2', 0)
        return f"Let me share {patient_name}'s vitals: Heart rate's at {hr} BPM, temperature's {temp}°F, breathing at {rr} per minute, and oxygen is {spo2}%. Everything's looking pretty good!"
    
    # Heart rate - flexible matching
    if any(word in query_lower for word in ['heart', 'pulse', 'hr', 'bpm', 'beat']):
        hr = vitals.get('heart_rate', 0)
        if 60 <= hr <= 100:
            return f"{patient_name}'s heart rate is {hr} BPM - that's right in the healthy range!"
        elif hr > 100:
            return f"Their heart rate's a bit elevated at {hr} BPM. I've notified the care team to check on them."
        else:
            return f"Heart rate's on the lower side at {hr} BPM. The team's been alerted to take a look."
    
    # Temperature - flexible matching
    if any(word in query_lower for word in ['temperature', 'temp', 'fever', 'hot', 'cold']):
        temp = vitals.get('temperature', 0)
        if 97 <= temp <= 99:
            return f"Temperature's looking good at {temp}°F - right where we want it!"
        elif temp > 99:
            return f"They're running a bit warm at {temp}°F. I'm keeping a close eye on it."
        else:
            return f"Temperature's {temp}°F - a little on the cool side, but I'm monitoring it."
    
    # Oxygen - flexible matching
    if any(word in query_lower for word in ['oxygen', 'spo2', 'o2', 'saturation', 'breathing']):
        spo2 = vitals.get('spo2', 0)
        if spo2 >= 98:
            return f"Oxygen levels are excellent at {spo2}% - they're breathing really well!"
        elif spo2 >= 95:
            return f"Oxygen saturation's at {spo2}% - that's good and stable."
        else:
            return f"Oxygen's at {spo2}% - I'm watching this closely and the team's aware."
    
    # Sleep
    if 'sleep' in query_lower:
        sleep_info = sleep_stage.replace('_', ' ')
        if ai_active:
            return f"They're in {sleep_info} sleep right now. I'm adjusting the lights and music to help them rest better."
        else:
            return f"They're in {sleep_info} sleep at the moment. Looking peaceful!"
    
    # Pain
    if 'pain' in query_lower:
        if pain_detected:
            return f"I've noticed some signs of discomfort - their vitals show they might be uncomfortable. I've adjusted things to help and let the team know."
        else:
            return f"Good news - no pain indicators right now! They seem comfortable and relaxed."
    
    # AI control
    if 'ai' in query_lower and 'control' in query_lower:
        if ai_active:
            return f"I'm actively helping out! I'm watching {patient_name}'s vitals and adjusting the lights and sounds to keep them comfortable and help them heal."
        else:
            return f"I'm in standby mode right now - the care team has manual control of the room."
    
    # Environment
    if any(word in query_lower for word in ['light', 'music', 'environment', 'room']):
        light_color = environment.get('light_hex_color', '#FFFFFF')
        light_brightness = int(environment.get('light_brightness', 0.5) * 100)
        music_id = environment.get('music_playlist_id', 'none')
        music_volume = int(environment.get('music_volume', 0) * 100)
        
        music_desc = 'no music playing' if music_id == 'none' else f"playing {music_id.replace('_', ' ')} at {music_volume}% volume"
        
        return f"The room environment for {patient_name} is currently: Lighting is set to {light_color} at {light_brightness}% brightness, and {music_desc}. {environment.get('ai_reasoning', '')}"
    
    # Recommendation
    if 'recommend' in query_lower or 'suggest' in query_lower:
        if pain_detected:
            return "Based on pain indicators, I recommend checking on the patient, ensuring they're comfortable, and considering pain management options. The AI has dimmed lights and is playing calming music."
        elif sleep_stage == 'light_sleep':
            return "The patient is in light sleep. I recommend maintaining a quiet, calm environment with minimal disturbances. The AI has optimized lighting and audio accordingly."
        elif sleep_stage == 'awake':
            return "The patient is awake. This might be a good time for medication, vitals check, or family visits. The AI has set energizing lighting."
        else:
            return "All indicators appear normal. Continue current monitoring protocol."
    
    # Help
    if 'help' in query_lower or 'what can you' in query_lower:
        return f"I can help you with information about {patient_name} in {room_number}. You can ask me about:\n• Patient status and how they're doing\n• Vital signs (heart rate, temperature, oxygen levels)\n• Sleep stages and patterns\n• Pain indicators\n• AI control and room environment\n• Recommendations based on current conditions\n\nJust ask me naturally, like 'How is the patient?' or 'What's the heart rate?'"
    
    # Smart fallback - try to understand what they're asking about
    logger.info(f"No pattern matched for query: '{query}'")
    
    # If asking about anything numeric/measurements, give all vitals
    if any(word in query_lower for word in ['what', 'tell', 'show', 'give', 'check']):
        hr = vitals.get('heart_rate', 0)
        temp = vitals.get('temperature', 0)
        rr = vitals.get('respiratory_rate', 0)
        spo2 = vitals.get('spo2', 0)
        sleep_desc = sleep_stage.replace('_', ' ')
        
        response = f"Here's the current information for {patient_name} in {room_number}:\n\n"
        response += f"**Vital Signs:**\n"
        response += f"• Heart Rate: {hr} BPM (normal: 60-100)\n"
        response += f"• Temperature: {temp}°F (normal: 97-99°F)\n"
        response += f"• SpO2: {spo2}% (normal: 95-100%)\n"
        response += f"• Respiratory Rate: {rr}/min (normal: 12-20)\n\n"
        response += f"**Current State:**\n"
        response += f"• Sleep Stage: {sleep_desc}\n"
        response += f"• Pain Detected: {'Yes - patient needs attention' if pain_detected else 'No'}\n"
        response += f"• AI Control: {'Active - auto-adjusting environment' if ai_active else 'Disabled - manual control'}\n\n"
        response += "Ask me specific questions like 'What's the heart rate?' or 'Is the patient in pain?'"
        return response
    
    # Default fallback
    return f"I'm the AI assistant for {patient_name} in {room_number}. I can provide information about vital signs, sleep status, pain indicators, AI control, and room environment. Could you please rephrase your question? You can also ask 'What can you help with?' to see what I can do."


def register_routes(app):
    """Register assistant blueprint"""
    app.register_blueprint(assistant_bp)
