#!/bin/bash

# Beat Suite AI - Server Control Script
# Usage: ./app [start|stop|restart|status]

PID_FILE=".server.pid"
LOG_FILE="server.log"

cd "$(dirname "$0")"

# Function to start server
start_server() {
    echo "🏥 Beat Suite AI - Starting Server..."
    echo "========================================"

    # Check if server is already running
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  Server is already running (PID: $PID)"
            echo "Use './app restart' to restart or './app stop' to stop"
            exit 1
        else
            rm -f "$PID_FILE"
        fi
    fi

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "❌ Virtual environment not found. Creating..."
        python3 -m venv venv
        echo "✅ Virtual environment created"
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Load environment variables from .env file
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
        echo "🔑 Environment variables loaded from .env"
    fi

    # Install dependencies
    echo "📦 Checking dependencies..."
    pip install -q -r requirements.txt

    # Start server in background
    echo "🚀 Starting Flask server on http://localhost:5001"
    echo "========================================"
    echo ""
    if [ ! -f backend/data/users.json ]; then
        echo "⚠️  No accounts yet. Create them with:"
        echo "     python scripts/seed_users.py"
    else
        echo "📋 Sign in with an account from scripts/seed_users.py"
    fi
    echo "========================================"
    echo ""

    nohup python run.py > "$LOG_FILE" 2>&1 &
    SERVER_PID=$!
    echo $SERVER_PID > "$PID_FILE"

    # Wait a moment and check if server started
    sleep 2
    if ps -p $SERVER_PID > /dev/null 2>&1; then
        echo "✅ Server started successfully (PID: $SERVER_PID)"
        echo "📝 Logs: tail -f $LOG_FILE"
        echo "🌐 URL: http://localhost:5001"
    else
        echo "❌ Failed to start server. Check $LOG_FILE for errors"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Function to stop server
stop_server() {
    echo "🛑 Beat Suite AI - Stopping Server..."
    echo "========================================"

    if [ ! -f "$PID_FILE" ]; then
        echo "⚠️  No server PID file found"
        # Try to kill by port anyway
        PORT_PID=$(lsof -ti:5001 2>/dev/null)
        if [ ! -z "$PORT_PID" ]; then
            echo "🔍 Found process on port 5001 (PID: $PORT_PID)"
            kill -15 $PORT_PID 2>/dev/null
            sleep 1
            if ps -p $PORT_PID > /dev/null 2>&1; then
                kill -9 $PORT_PID 2>/dev/null
            fi
            echo "✅ Server stopped"
        else
            echo "ℹ️  Server is not running"
        fi
        exit 0
    fi

    PID=$(cat "$PID_FILE")
    
    if ps -p $PID > /dev/null 2>&1; then
        echo "🔍 Found server process (PID: $PID)"
        kill -15 $PID 2>/dev/null
        
        # Wait for graceful shutdown
        for i in {1..5}; do
            if ! ps -p $PID > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  Forcing shutdown..."
            kill -9 $PID 2>/dev/null
        fi
        
        rm -f "$PID_FILE"
        echo "✅ Server stopped"
    else
        echo "⚠️  Server process not found (PID: $PID)"
        rm -f "$PID_FILE"
        echo "ℹ️  Cleaned up stale PID file"
    fi
}

# Function to check server status
check_status() {
    echo "🏥 Beat Suite AI - Server Status"
    echo "========================================"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "✅ Server is running (PID: $PID)"
            echo "🌐 URL: http://localhost:5001"
            echo "📝 Logs: tail -f $LOG_FILE"
            
            # Check if port is listening
            if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1; then
                echo "🔌 Port 5001 is open and listening"
            else
                echo "⚠️  Process running but port 5001 not listening"
            fi
        else
            echo "⚠️  PID file exists but process not running"
            rm -f "$PID_FILE"
        fi
    else
        PORT_PID=$(lsof -ti:5001 2>/dev/null)
        if [ ! -z "$PORT_PID" ]; then
            echo "⚠️  No PID file but process found on port 5001 (PID: $PORT_PID)"
        else
            echo "❌ Server is not running"
        fi
    fi
}

# Function to restart server
restart_server() {
    echo "🔄 Beat Suite AI - Restarting Server..."
    echo "========================================"
    stop_server
    echo ""
    sleep 1
    start_server
}

# Main script logic
case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        check_status
        ;;
    *)
        echo "🏥 Beat Suite AI - Server Control"
        echo ""
        echo "Usage: ./app [command]"
        echo ""
        echo "Commands:"
        echo "  start    - Start the server"
        echo "  stop     - Stop the server"
        echo "  restart  - Restart the server"
        echo "  status   - Check server status"
        echo ""
        echo "Examples:"
        echo "  ./app start"
        echo "  ./app stop"
        echo "  ./app restart"
        echo "  ./app status"
        exit 1
        ;;
esac
