#!/bin/bash
# Test script for Google Home webhook integration

echo "====================================="
echo "Testing Google Home Integration"
echo "====================================="
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "-------------------------------------"
curl -s http://localhost:5001/api/google-home/health | python3 -m json.tool
echo ""
echo ""

# Test 2: Get Room Status (Room 101)
echo "Test 2: Get Room Status - Room 101"
echo "-------------------------------------"
curl -s -X POST http://localhost:5001/api/google-home/fulfillment \
  -H "Content-Type: application/json" \
  -d '{"queryResult":{"intent":{"displayName":"GetRoomStatus"},"parameters":{"room_number":"101"}}}' | python3 -m json.tool
echo ""
echo ""

# Test 3: Get Patient Vitals (Room 102)
echo "Test 3: Get Patient Vitals - Room 102"
echo "-------------------------------------"
curl -s -X POST http://localhost:5001/api/google-home/fulfillment \
  -H "Content-Type: application/json" \
  -d '{"queryResult":{"intent":{"displayName":"GetPatientVitals"},"parameters":{"room_number":"102"}}}' | python3 -m json.tool
echo ""
echo ""

# Test 4: Control Light - Turn On (Room 101)
echo "Test 4: Control Light - Turn On Room 101"
echo "-------------------------------------"
curl -s -X POST http://localhost:5001/api/google-home/fulfillment \
  -H "Content-Type: application/json" \
  -d '{"queryResult":{"intent":{"displayName":"ControlLight"},"parameters":{"room_number":"101","action":"on"}}}' | python3 -m json.tool
echo ""
echo ""

# Test 5: Control Light - Set Blue at 70% (Room 101)
echo "Test 5: Control Light - Blue 70% Room 101"
echo "-------------------------------------"
curl -s -X POST http://localhost:5001/api/google-home/fulfillment \
  -H "Content-Type: application/json" \
  -d '{"queryResult":{"intent":{"displayName":"ControlLight"},"parameters":{"room_number":"101","color":"blue","brightness":"70"}}}' | python3 -m json.tool
echo ""
echo ""

# Test 6: Control Music - Play (Room 102)
echo "Test 6: Control Music - Play Room 102"
echo "-------------------------------------"
curl -s -X POST http://localhost:5001/api/google-home/fulfillment \
  -H "Content-Type: application/json" \
  -d '{"queryResult":{"intent":{"displayName":"ControlMusic"},"parameters":{"room_number":"102","action":"play"}}}' | python3 -m json.tool
echo ""
echo ""

# Test 7: Enable AI (Room 101)
echo "Test 7: Enable AI - Room 101"
echo "-------------------------------------"
curl -s -X POST http://localhost:5001/api/google-home/fulfillment \
  -H "Content-Type: application/json" \
  -d '{"queryResult":{"intent":{"displayName":"EnableAI"},"parameters":{"room_number":"101"}}}' | python3 -m json.tool
echo ""
echo ""

# Test 8: Disable AI (Room 102)
echo "Test 8: Disable AI - Room 102"
echo "-------------------------------------"
curl -s -X POST http://localhost:5001/api/google-home/fulfillment \
  -H "Content-Type: application/json" \
  -d '{"queryResult":{"intent":{"displayName":"DisableAI"},"parameters":{"room_number":"102"}}}' | python3 -m json.tool
echo ""
echo ""

echo "====================================="
echo "All tests completed!"
echo "====================================="
