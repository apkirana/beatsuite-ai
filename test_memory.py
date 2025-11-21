#!/usr/bin/env python3
"""
Test script to debug memory service
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.services.memory_service import memory_service

    print("Testing memory service...")

    # Test adding a simple memory
    memory_service._add_memory_local("TEST001", "This is a test memory", "positive")

    # Test reading memories
    memories = memory_service.get_memories_by_user("TEST001")
    print(f"Retrieved {len(memories)} memories for TEST001")

    all_memories = memory_service.get_all_memories()
    print(f"Total memories in system: {len(all_memories)}")

except Exception as e:
    import traceback
    print(f"Error: {e}")
    print(traceback.format_exc())