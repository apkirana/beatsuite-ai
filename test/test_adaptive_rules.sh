#!/bin/bash

# Test Adaptive Rules System
echo "🧪 Testing Beat Suite AI Adaptive Rules System"
echo "============================================="
echo ""

# Test 1: Check if rules file exists
echo "Test 1: Checking adaptive rules configuration..."
if [ -f "backend/config/adaptive_rules.json" ]; then
    echo "✅ Adaptive rules file exists"
    echo "📋 Rules count: $(jq '.adaptive_rules | length' backend/config/adaptive_rules.json)"
else
    echo "❌ Adaptive rules file not found!"
    exit 1
fi

echo ""

# Test 2: Check rules status endpoint
echo "Test 2: Testing adaptive rules status endpoint..."
echo "Starting test server if needed..."

# Check if server is running
if ! curl -s http://localhost:5001/health > /dev/null; then
    echo "⚠️  Server not running. Please start your Flask app first:"
    echo "   python -m backend.app"
    exit 1
fi

echo "🔄 Checking adaptive rules status..."
RULES_STATUS=$(curl -s http://localhost:5001/api/ai/rules/status)
echo "📊 Rules Status: $RULES_STATUS"

echo ""

# Test 3: Test adaptive optimization with sample data
echo "Test 3: Testing adaptive optimization..."

# Test pain scenario
echo "🚨 Testing pain detection scenario..."
PAIN_TEST=$(curl -s -X POST http://localhost:5001/api/ai/optimize-adaptive/101 \
  -H "Content-Type: application/json" \
  -H "Cookie: session=test" \
  -d '{}')

echo "📊 Pain scenario result: $PAIN_TEST"

echo ""

# Test 4: Test with synthetic data
echo "Test 4: Testing with synthetic pain data..."
echo "🧪 Generating synthetic pain scenario..."

SYNTHETIC_PAIN=$(curl -s -X GET "http://localhost:5001/api/test/synthetic-data/test_patient?scenario=pain")
echo "📊 Synthetic pain data: $SYNTHETIC_PAIN"

echo ""

# Test 5: Test Gemini availability
echo "Test 5: Testing Gemini AI availability..."
GEMINI_STATUS=$(curl -s http://localhost:5001/api/ai/status)
echo "🤖 Gemini Status: $GEMINI_STATUS"

echo ""
echo "🎉 Adaptive Rules Testing Complete!"
echo ""
echo "✅ Next Steps:"
echo "1. Open your dashboard: http://localhost:5001"
echo "2. Click on a room card"
echo "3. Click the purple 'Adaptive AI' button"
echo "4. Check the console logs for rule matching"
echo ""
echo "🔍 Monitoring Commands:"
echo "• Watch logs: tail -f backend/logs/app.log"
echo "• Test rules directly: curl http://localhost:5001/api/ai/rules/status"
echo "• Manual optimization: curl -X POST http://localhost:5001/api/ai/optimize-adaptive/101"