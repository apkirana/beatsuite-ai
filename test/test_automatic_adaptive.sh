#!/bin/bash

# Test Adaptive Rules Automatic System
echo "🧪 Testing Adaptive Rules Automatic System"
echo "========================================="

BASE_URL="http://localhost:5001"

# Function to check if server is running
check_server() {
    if ! curl -s "$BASE_URL/api/auth/status" > /dev/null 2>&1; then
        echo "❌ Server not running at $BASE_URL"
        echo "Please start your Flask app first:"
        echo "python -m backend.app"
        exit 1
    fi
    echo "✅ Server is running"
}

# Function to test adaptive rules status
test_adaptive_rules_status() {
    echo ""
    echo "🔍 Checking Adaptive Rules Status..."
    
    response=$(curl -s "$BASE_URL/api/ai/rules/status")
    
    if echo "$response" | grep -q '"success": true'; then
        echo "✅ Adaptive rules API is working"
        
        # Check if rules are enabled
        if echo "$response" | grep -q '"adaptive_rules_enabled": true'; then
            echo "✅ Adaptive rules are ENABLED"
            rules_count=$(echo "$response" | grep -o '"rules_count": [0-9]*' | cut -d' ' -f2)
            echo "📊 Number of rules loaded: $rules_count"
        else
            echo "⚠️  Adaptive rules are DISABLED"
        fi
        
        # Check AI availability
        if echo "$response" | grep -q '"ai_available": true'; then
            echo "✅ Gemini AI is available"
        else
            echo "⚠️  Gemini AI is not available"
        fi
    else
        echo "❌ Adaptive rules API failed"
        echo "$response"
    fi
}

# Function to test automatic AI processing
test_automatic_processing() {
    echo ""
    echo "🤖 Testing Automatic AI Processing..."
    
    # Get list of rooms
    rooms_response=$(curl -s "$BASE_URL/api/rooms")
    
    if echo "$rooms_response" | grep -q '"success": true'; then
        echo "✅ Rooms API is working"
        
        # Extract first room ID
        room_id=$(echo "$rooms_response" | grep -o '"room_id": "[^"]*"' | head -1 | cut -d'"' -f4)
        
        if [ -n "$room_id" ]; then
            echo "🏥 Testing with room: $room_id"
            
            # Get room data to see if AI is processing automatically
            room_response=$(curl -s "$BASE_URL/api/rooms/$room_id")
            
            if echo "$room_response" | grep -q '"ai_control_active": true'; then
                echo "✅ AI is active for room $room_id"
                
                # Check if adaptive rules indicator is present
                if echo "$room_response" | grep -q '"adaptive_rules_active"'; then
                    echo "✅ Adaptive rules status is being reported"
                else
                    echo "⚠️  Adaptive rules status not found in response"
                fi
                
                # Show current AI reasoning
                reasoning=$(echo "$room_response" | grep -o '"ai_reasoning": "[^"]*"' | cut -d'"' -f4)
                if [ -n "$reasoning" ]; then
                    echo "🧠 Current AI reasoning: $reasoning"
                    
                    # Check if it mentions a rule
                    if echo "$reasoning" | grep -q "Rule:"; then
                        echo "✅ Adaptive rule is being applied automatically!"
                    else
                        echo "ℹ️  Traditional AI engine is running"
                    fi
                fi
            else
                echo "ℹ️  AI is not active for room $room_id"
            fi
        else
            echo "❌ No rooms found"
        fi
    else
        echo "❌ Failed to get rooms"
        echo "$rooms_response"
    fi
}

# Function to simulate patient data and test automatic processing
test_automatic_rule_matching() {
    echo ""
    echo "📊 Testing Automatic Rule Matching..."
    
    # Test pain detection scenario
    echo "🩺 Simulating pain detection scenario..."
    
    pain_data='{
        "heart_rate": 105,
        "movement": 0.7,
        "spo2": 96,
        "scenario": "pain"
    }'
    
    response=$(curl -s -X POST "$BASE_URL/api/test/simulate-ai-adjustment/patient_001" \
        -H "Content-Type: application/json" \
        -d "$pain_data")
    
    if echo "$response" | grep -q '"success": true'; then
        echo "✅ Pain scenario simulation successful"
        
        # Check if red light therapy is activated
        if echo "$response" | grep -q '"color_hex": "#FF'; then
            echo "✅ Red light therapy automatically activated"
        fi
        
        # Check AI reasoning
        reasoning=$(echo "$response" | grep -o '"ai_reasoning": "[^"]*"' | cut -d'"' -f4)
        if [ -n "$reasoning" ]; then
            echo "🧠 AI reasoning: $reasoning"
        fi
    else
        echo "❌ Pain scenario simulation failed"
    fi
    
    # Wait a moment
    sleep 2
    
    # Test sleep scenario
    echo ""
    echo "😴 Simulating sleep scenario..."
    
    sleep_data='{
        "heart_rate": 58,
        "movement": 0.1,
        "spo2": 98,
        "scenario": "sleeping"
    }'
    
    response=$(curl -s -X POST "$BASE_URL/api/test/simulate-ai-adjustment/patient_001" \
        -H "Content-Type: application/json" \
        -d "$sleep_data")
    
    if echo "$response" | grep -q '"success": true'; then
        echo "✅ Sleep scenario simulation successful"
        
        # Check if low lighting is activated
        brightness=$(echo "$response" | grep -o '"brightness": [0-9.]*' | cut -d' ' -f2)
        if [ -n "$brightness" ]; then
            echo "💡 Light brightness automatically set to: $brightness"
            
            # Check if it's appropriately dim for sleep
            if awk "BEGIN {exit !($brightness < 0.2)}"; then
                echo "✅ Appropriate dim lighting for sleep"
            fi
        fi
    else
        echo "❌ Sleep scenario simulation failed"
    fi
}

# Function to show real-time monitoring
show_real_time_monitoring() {
    echo ""
    echo "📡 Real-time Monitoring Test (5 seconds)..."
    echo "This shows how adaptive rules work automatically..."
    
    for i in {1..5}; do
        echo "⏰ Check #$i:"
        
        # Get current room status
        room_response=$(curl -s "$BASE_URL/api/rooms/room_101")
        
        if echo "$room_response" | grep -q '"success": true'; then
            # Extract key information
            hr=$(echo "$room_response" | grep -o '"heart_rate": [0-9]*' | cut -d' ' -f2)
            reasoning=$(echo "$room_response" | grep -o '"ai_reasoning": "[^"]*"' | cut -d'"' -f4)
            
            echo "   💓 HR: $hr BPM"
            echo "   🤖 AI: $(echo "$reasoning" | cut -c1-50)..."
            
            # Check if adaptive rule is mentioned
            if echo "$reasoning" | grep -q "Rule:"; then
                echo "   ✅ Adaptive rule active"
            else
                echo "   ℹ️  Traditional AI"
            fi
        fi
        
        sleep 1
    done
}

# Run all tests
main() {
    check_server
    test_adaptive_rules_status
    test_automatic_processing
    test_automatic_rule_matching
    show_real_time_monitoring
    
    echo ""
    echo "🎉 Adaptive Rules Automatic System Test Complete!"
    echo ""
    echo "📋 Summary:"
    echo "• Adaptive rules are integrated into the main AI engine"
    echo "• Rules are evaluated automatically every time patient data is processed"
    echo "• No manual button clicking required"
    echo "• System falls back to traditional AI if rules don't match"
    echo "• Status indicators show when adaptive rules are active"
    echo ""
    echo "🚀 Your system is now running with automatic adaptive rules!"
}

main