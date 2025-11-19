"""
Beat Suite AI - Application Entry Point
Run this file to start the Flask server
"""

import os
from backend.app import create_app

# Create Flask app instance
app = create_app()

if __name__ == '__main__':
    # Get port from environment (for Cloud Run compatibility)
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('ENVIRONMENT', 'development') != 'production'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
