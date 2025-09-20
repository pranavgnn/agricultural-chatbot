import uuid
from typing import Dict, Optional
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage
from collections import OrderedDict
import time

class SessionManager:
    """Manages chat sessions with memory for agricultural assistant"""
    
    def __init__(self, max_sessions: int = 25, memory_window: int = 10):
        self.max_sessions = max_sessions
        self.memory_window = memory_window
        self.sessions: OrderedDict[str, Dict] = OrderedDict()
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> tuple[str, ConversationBufferWindowMemory]:
        """Get existing session or create new one"""
        
        if session_id and session_id in self.sessions:
            # Update last accessed time
            self.sessions[session_id]["last_accessed"] = time.time()
            self.sessions.move_to_end(session_id)
            return session_id, self.sessions[session_id]["memory"]
        
        # Create new session
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Remove oldest session if we exceed max_sessions
        if len(self.sessions) >= self.max_sessions:
            oldest_session = next(iter(self.sessions))
            del self.sessions[oldest_session]
        
        # Create new memory for this session
        memory = ConversationBufferWindowMemory(
            k=self.memory_window,
            memory_key="chat_history",
            return_messages=True
        )
        
        self.sessions[session_id] = {
            "memory": memory,
            "created_at": time.time(),
            "last_accessed": time.time()
        }
        
        return session_id, memory
    
    def get_session_memory(self, session_id: str) -> Optional[ConversationBufferWindowMemory]:
        """Get memory for a specific session"""
        if session_id in self.sessions:
            self.sessions[session_id]["last_accessed"] = time.time()
            return self.sessions[session_id]["memory"]
        return None
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a specific session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_session_count(self) -> int:
        """Get current number of active sessions"""
        return len(self.sessions)
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Remove sessions older than max_age_hours"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        sessions_to_remove = []
        for session_id, session_data in self.sessions.items():
            if current_time - session_data["last_accessed"] > max_age_seconds:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
        
        return len(sessions_to_remove)

# Global session manager instance
session_manager = SessionManager(max_sessions=25, memory_window=10)