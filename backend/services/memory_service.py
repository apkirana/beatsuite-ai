import vertexai
from google.adk.sessions import VertexAiSessionService
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

# TODO: Make these configurable
PROJECT_ID = "beatsuite-478714"
LOCATION = "us-central1"

# Fallback local storage for demo purposes
MEMORIES_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'memories.json')

class MemoryService:
    def __init__(self):
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        self.session_service = VertexAiSessionService(project=PROJECT_ID, location=LOCATION)

    def add_memory(self, user_id: str, content: str, feedback: str = None):
        """
        Adds a memory entry to the Vertex AI Memory Bank with local fallback.

        Args:
            user_id (str): The ID of the user associated with the memory.
            content (str): The main content of the memory (e.g., interaction summary, specific fact).
            feedback (str, optional): User feedback related to the content ('positive', 'negative', or None).
        """
        # Use local storage for demo purposes (Vertex AI has async issues)
        logger.info("Using local storage for memory")
        return self._add_memory_local(user_id, content, feedback)

    def _add_memory_local(self, user_id: str, content: str, feedback: str = None):
        """Local fallback for memory storage"""
        # Load existing memories
        memories = self._load_memories()

        # Create new memory entry
        memory_entry = {
            "user_id": user_id,
            "content": content,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat(),
            "event_type": "USER_INTERACTION"
        }

        # Add to user's memories
        if user_id not in memories:
            memories[user_id] = []
        memories[user_id].append(memory_entry)

        # Save back to file
        self._save_memories(memories)
        logger.info(f"Added local memory for user {user_id}: {content[:50]}...")

    def _load_memories(self):
        """Load memories from local JSON file"""
        try:
            if os.path.exists(MEMORIES_FILE):
                with open(MEMORIES_FILE, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading memories: {e}")
            return {}

    def _save_memories(self, memories):
        """Save memories to local JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(MEMORIES_FILE), exist_ok=True)
            with open(MEMORIES_FILE, 'w') as f:
                json.dump(memories, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving memories: {e}")


    def search_memory(self, user_id: str, query: str):
        """
        Searches for relevant memories in the Vertex AI Memory Bank for a specific user.

        Args:
            user_id (str): The ID of the user.
            query (str): The query to search for relevant memories.

        Returns:
            list: A list of relevant memory entries (dictionaries).
        """
        try:
            session = self.session_service.get_session(session_id=user_id)
            # This is a simplification. In a real application, you would need to
            # implement a more sophisticated search within the events.
            return session.events
        except Exception:
            return []

    def get_all_memories(self):
        """
        Retrieves all memories from local storage.
        """
        try:
            memories = self._load_memories()
            all_memories = []
            for user_id, user_memories in memories.items():
                all_memories.extend(user_memories)
            return all_memories
        except Exception as e:
            logger.error(f"Error getting all memories: {e}")
            return []

    def get_memories_by_user(self, user_id: str):
        """
        Retrieves all memories for a specific user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            list: A list of all memory entries for the user.
        """
        try:
            # Try Vertex AI first
            session = self.session_service.get_session(session_id=user_id)
            return session.events
        except Exception:
            # Fall back to local storage
            memories = self._load_memories()
            return memories.get(user_id, [])


# Initialize the memory service
memory_service = MemoryService()