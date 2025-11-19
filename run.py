"""
Beat Suite AI - Application Entry Point
Run this file to start the Flask server
"""

from backend.app import app

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
