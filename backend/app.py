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

# Import blueprints
from backend.api.auth_routes import auth_bp
from backend.api.room_routes import room_bp
from backend.api.ai_routes import ai_bp
from backend.api.reports_routes import reports_bp, notifications_bp
from backend.api.patient_routes import patients_bp
from backend.api.room_crud_routes import rooms_crud_bp
from backend.api.user_routes import users_bp
from backend.api.test_routes import test_bp

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
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JSON_SORT_KEYS'] = False
    
    # Enable CORS
    CORS(app, supports_credentials=True)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(room_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(notifications_bp)
    
    # Register CRUD blueprints
    app.register_blueprint(patients_bp)
    app.register_blueprint(rooms_crud_bp)
    app.register_blueprint(users_bp)
    
    # Register testing blueprints
    app.register_blueprint(test_bp)
    
    # Register assistant blueprint
    from .api.assistant_routes import assistant_bp
    app.register_blueprint(assistant_bp)
    
    # Register Google Home integration
    from .api.google_home_routes import google_home_bp
    app.register_blueprint(google_home_bp)
    
    # Register Health History API
    from .api.health_history_routes import health_history_bp
    app.register_blueprint(health_history_bp)
    
    # Register AI Report Analysis API
    from .api.report_analysis_routes import report_analysis_bp
    app.register_blueprint(report_analysis_bp)
    
    # Initialize AI system
    smartwatch_manager.register_device("P001", "simulated")
    smartwatch_manager.register_device("P002", "simulated")
    smartwatch_manager.register_device("P003", "simulated")
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
    logger.info("="*60)
    logger.info("Beat Suite AI Dashboard - Production Mode")
    logger.info("="*60)
    logger.info("Access at: http://localhost:5001")
    logger.info("="*60)
    logger.info("\n📋 Demo Credentials:")
    logger.info("  Admin:  username=admin   password=admin123")
    logger.info("  Nurse:  username=nurse1  password=nurse123")
    logger.info("  Family: username=family1 password=family123")
    logger.info("="*60)
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
