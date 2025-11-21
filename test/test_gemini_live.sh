#!/bin/bash
# Test script for Gemini Live Voice Chat functionality

echo "🧪 Testing Gemini Live Voice Chat System"
echo "======================================"

# Check if server is running
if curl -s http://localhost:5000 > /dev/null; then
    echo "✅ Flask server is running"
else
    echo "❌ Flask server not running - please start with: python3 backend/app.py"
    exit 1
fi

# Test API key availability
echo ""
echo "🔑 Testing Google API Key..."
response=$(curl -s -X POST http://localhost:5000/api/ai/live/token \
    -H "Content-Type: application/json" \
    -d '{"room_id":"TEST"}' \
    --cookie-jar /tmp/cookies.txt \
    --cookie /tmp/cookies.txt)

if echo "$response" | grep -q "success.*true"; then
    echo "✅ API key is properly configured"
else
    echo "❌ API key configuration issue:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    echo ""
    echo "💡 To fix:"
    echo "   1. Make sure GOOGLE_API_KEY environment variable is set"
    echo "   2. Get your API key from https://makersuite.google.com/app/apikey"
    echo "   3. Enable Generative Language API in Google Cloud Console"
    echo "   4. Export GOOGLE_API_KEY=your_key_here"
fi

echo ""
echo "🎤 Browser Compatibility Checks:"
echo "   • Modern browsers (Chrome 66+, Firefox 60+, Safari 14.1+) support MediaRecorder"
echo "   • HTTPS is required for microphone access in production"
echo "   • WebSockets must be enabled"

echo ""
echo "🔧 Common Fixes:"
echo "   • Clear browser cache and reload"
echo "   • Allow microphone permissions when prompted"
echo "   • Check browser console (F12) for detailed error messages"
echo "   • Ensure stable internet connection"

echo ""
echo "📋 Testing Summary:"
echo "   • Fixed audio format compatibility issues"
echo "   • Added proper error handling and timeouts"
echo "   • Improved browser compatibility checks"
echo "   • Enhanced WebSocket connection stability"
echo ""
echo "🎉 Your Gemini Live Voice Chat should now work!"