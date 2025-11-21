from flask import Blueprint, render_template, request, jsonify, url_for
from backend.services.feedback_service import FeedbackService
from backend.services.agent_memory_service import AgentMemoryService
import random

patient_bp = Blueprint('patient_bp', __name__)


@patient_bp.route('/patient/<patient_id>')
def patient_page(patient_id):
    """Serve a simple patient-facing page for kids to give feedback"""
    # Minimal page, template will handle the rest
    return render_template('patient.html', patient_id=patient_id)


@patient_bp.route('/public/feedback/submit', methods=['POST'])
def public_feedback_submit():
    """Public endpoint that accepts feedback submissions from patient UI.
    This endpoint is intentionally public-friendly for demo/testing (no auth).
    """
    payload = request.get_json() or {}
    # Basic validation
    required = ['patient_id', 'interaction_type', 'action', 'rating']
    for k in required:
        if k not in payload:
            return jsonify({'success': False, 'error': f'Missing {k}'}), 400

    patient_id = payload.get('patient_id')
    fs = FeedbackService()

    # Normalize rating: demo UI sends numeric rating (1-5).
    try:
        rating_score = int(payload.get('rating', 0))
    except Exception:
        rating_score = 0

    # Map numeric score to categorical rating expected by FeedbackService
    if rating_score >= 4:
        rating_label = 'positive'
    elif rating_score <= 2 and rating_score > 0:
        rating_label = 'negative'
    else:
        rating_label = 'neutral'

    interaction_context = {
        'action': payload.get('action'),
        'situation': payload.get('situation', '')
    }

    res = fs.submit_feedback(
        patient_id=patient_id,
        interaction_type=payload.get('interaction_type'),
        rating=rating_label,
        rating_score=rating_score,
        user_comment=payload.get('comment', ''),
        interaction_context=interaction_context
    )

    return jsonify(res)


@patient_bp.route('/public/assistant/engage/<patient_id>')
def public_assistant_engage(patient_id):
    """Return a kid-friendly joke and an image URL to cheer up the patient.
    For production, this could call the AgentMemoryService / Gemini AI to generate
    personalized content; here we use a simple fallback.
    """
    jokes = [
        "Why did the teddy bear say no to dessert? Because it was already stuffed!",
        "What do you call a sleeping bull? A bulldozer!",
        "Why did the cookie go to the nurse? Because it felt crummy!",
        "What do you call a dinosaur that is sleeping? A dino-snore!",
    ]

    images = [
        url_for('static', filename='images/kid_happy.svg'),
    ]

    joke = random.choice(jokes)
    image = random.choice(images)

    # Optionally ask agent memory for a small personalized message (non-blocking)
    try:
        ams = AgentMemoryService()
        # If agent provides a friendly message, prefer it (fallback to joke)
        msg = ams.explain_adaptation(patient_id, context="cheer_up") if hasattr(ams, 'explain_adaptation') else None
        if msg:
            # Keep it short
            joke = (msg[:240] + '...') if len(msg) > 240 else msg
    except Exception:
        # Ignore agent errors and continue with joke
        pass

    return jsonify({'joke': joke, 'image_url': image})
