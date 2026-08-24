"""
Beat Suite AI - Main Application (Modular Architecture)
Production-ready Flask application with authentication
"""

import os
import logging
from flask import Flask, render_template, redirect, url_for, request
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import consolidated blueprints
from backend.api.auth_routes import auth_bp
from backend.api.user_routes import users_bp
from backend.api.healthcare_routes import patients_bp, health_history_bp, reports_bp, notifications_bp
from backend.api.monitoring_routes import room_bp, rooms_crud_bp
from backend.api.ai_routes import ai_bp
from backend.api.assistant_routes import assistant_bp
from backend.api.report_analysis_routes import report_analysis_bp
from backend.api.google_home_routes import google_home_bp
from backend.api.test_routes import test_bp
from backend.api.feedback_routes import feedback_bp # Import feedback blueprint
from backend.api.memory_routes import memory_bp # Import memory blueprint
# Import services
from backend.core.smartwatch import smartwatch_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    """Application factory pattern"""
    
    # Get the base directory (project root)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'frontend', 'templates'),
        static_folder=os.path.join(base_dir, 'frontend', 'static'),
        static_url_path='/static'
    )
    
    # Configuration
    #
    # SECRET_KEY signs session data — a known key lets anyone forge a session.
    # Outside development we refuse to start rather than fall back to a default.
    secret_key = os.environ.get('SECRET_KEY')
    is_development = os.environ.get('FLASK_ENV', 'production').lower() == 'development'
    if not secret_key:
        if not is_development:
            raise RuntimeError(
                "SECRET_KEY is not set. Generate one with "
                "`python -c \"import secrets; print(secrets.token_urlsafe(32))\"` "
                "and set it in the environment before starting the app."
            )
        secret_key = 'dev-only-key-not-for-deployment'
        logger.warning("SECRET_KEY unset — using an insecure development key.")
    app.config['SECRET_KEY'] = secret_key
    app.config['JSON_SORT_KEYS'] = False
    
    # Enable CORS.
    # supports_credentials=True sends cookies cross-origin, so the allowed
    # origins must be an explicit list — never "*" — or any site could drive
    # the API as a logged-in user.
    allowed_origins = [
        origin.strip()
        for origin in os.environ.get('ALLOWED_ORIGINS', 'http://localhost:5001').split(',')
        if origin.strip()
    ]
    CORS(app, supports_credentials=True, origins=allowed_origins)
    
    # Register consolidated blueprints
    # Authentication & User Management
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    
    # Healthcare Management (patients, health history, reports)
    app.register_blueprint(patients_bp)
    app.register_blueprint(health_history_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(notifications_bp)
    
    # Room Monitoring (real-time monitoring, CRUD operations)
    app.register_blueprint(room_bp)
    app.register_blueprint(rooms_crud_bp)
    
    # AI Services (analysis, assistant, report generation)
    app.register_blueprint(ai_bp)
    app.register_blueprint(assistant_bp)
    app.register_blueprint(report_analysis_bp)
    
    # Integrations & Testing
    app.register_blueprint(google_home_bp)
    app.register_blueprint(test_bp)
    app.register_blueprint(feedback_bp) # Register feedback blueprint
    app.register_blueprint(memory_bp) # Register memory blueprint
    
    # Initialize AI system
    smartwatch_manager.register_device("P001", "simulated")
    smartwatch_manager.register_device("P002", "simulated")
    smartwatch_manager.register_device("P003", "simulated")
    smartwatch_manager.register_device("P004", "simulated")
    smartwatch_manager.register_device("P005", "simulated")
    logger.info("AI feedback loop initialized for all patients")
    
    # Web routes
    @app.route('/')
    def index():
        """Redirect to login page"""
        return redirect(url_for('login_page'))
    
    @app.route('/login')
    def login_page():
        """Serve login page"""
        return render_template('login.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Serve main dashboard (requires authentication via JS)"""
        return render_template('dashboard.html')
    
    @app.route('/admin')
    def admin():
        """Serve admin management page (requires admin role via JS)"""
        return render_template('admin.html')
    
    @app.route('/iot-simulator')
    def iot_simulator():
        """Serve IoT device simulator page"""
        return render_template('iot_simulator.html')

    @app.route('/memory-admin')
    def memory_admin():
        """Serve memory admin page"""
        return render_template('memory_admin.html')

    @app.route('/feedback')
    def feedback_page():
        """Serve feedback form page"""
        return render_template('feedback_form.html')

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}")
        return {'error': 'Internal server error'}, 500
    
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    # Debug mode exposes the Werkzeug console — never enable it on a deployment.
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    port = int(os.environ.get('PORT', 5001))

    logger.info("="*60)
    logger.info("Beat Suite AI Dashboard")
    logger.info("="*60)
    logger.info(f"Listening on port {port} (debug={debug})")
    logger.info("No accounts exist until you run: python scripts/seed_users.py")
    logger.info("="*60)

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
