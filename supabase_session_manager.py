import uuid
from typing import Dict, List, Optional, Tuple
from supabase import create_client, Client
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage
import os
from dotenv import load_dotenv

load_dotenv()

class SupabaseSessionManager:
    """Manages chat sessions with Supabase storage"""
    
    def __init__(self, memory_window: int = 10):
        self.memory_window = memory_window
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Use service role for backend operations
        )
        # In-memory cache for active sessions
        self._memory_cache: Dict[str, ConversationBufferWindowMemory] = {}
    
    async def create_session(self, user_id: str, title: str = "New Chat", is_public: bool = False) -> str:
        """Create a new chat session in Supabase"""
        try:
            result = self.supabase.table("chat_sessions").insert({
                "user_id": user_id,
                "title": title,
                "is_public": is_public
            }).execute()
            
            session_id = result.data[0]["id"]
            return session_id
        except Exception as e:
            print(f"Error creating session: {e}")
            raise
    
    async def get_session(self, session_id: str, user_id: Optional[str] = None) -> Optional[Dict]:
        """Get session details"""
        try:
            query = self.supabase.table("chat_sessions").select("*").eq("id", session_id)
            
            result = query.execute()
            
            if not result.data:
                return None
            
            session = result.data[0]
            
            # Check access permissions
            # Allow if: session is public OR user owns the session
            if session["is_public"]:
                return session
            
            if user_id and session["user_id"] == user_id:
                return session
            
            # Not public and user doesn't own it (or no user)
            return None
        except Exception as e:
            print(f"Error getting session: {e}")
            return None
    
    async def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all sessions for a user"""
        try:
            result = self.supabase.table("chat_sessions")\
                .select("id, title, is_public, created_at, updated_at")\
                .eq("user_id", user_id)\
                .order("updated_at", desc=True)\
                .execute()
            
            return result.data
        except Exception as e:
            print(f"Error getting user sessions: {e}")
            return []
    
    async def update_session(self, session_id: str, user_id: str, **kwargs) -> bool:
        """Update session details (title, is_public, etc.)"""
        try:
            result = self.supabase.table("chat_sessions")\
                .update(kwargs)\
                .eq("id", session_id)\
                .eq("user_id", user_id)\
                .execute()
            
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating session: {e}")
            return False
    
    async def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a session and all its messages"""
        try:
            result = self.supabase.table("chat_sessions")\
                .delete()\
                .eq("id", session_id)\
                .eq("user_id", user_id)\
                .execute()
            
            # Clear from cache
            if session_id in self._memory_cache:
                del self._memory_cache[session_id]
            
            return len(result.data) > 0
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    async def add_message(self, session_id: str, role: str, content: str) -> bool:
        """Add a message to a session"""
        try:
            self.supabase.table("chat_messages").insert({
                "session_id": session_id,
                "role": role,
                "content": content
            }).execute()
            
            # Update session's updated_at
            self.supabase.table("chat_sessions")\
                .update({"updated_at": "now()"})\
                .eq("id", session_id)\
                .execute()
            
            return True
        except Exception as e:
            print(f"Error adding message: {e}")
            return False
    
    async def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get messages for a session"""
        try:
            query = self.supabase.table("chat_messages")\
                .select("role, content, created_at")\
                .eq("session_id", session_id)\
                .order("created_at", desc=False)
            
            if limit:
                # Get last N messages
                all_messages = query.execute().data
                return all_messages[-limit:] if len(all_messages) > limit else all_messages
            
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
    
    async def get_or_create_memory(self, session_id: str) -> ConversationBufferWindowMemory:
        """Get memory for a session, loading from DB if needed"""
        
        # Check cache first
        if session_id in self._memory_cache:
            return self._memory_cache[session_id]
        
        # Create new memory
        memory = ConversationBufferWindowMemory(
            k=self.memory_window,
            memory_key="chat_history",
            return_messages=True
        )
        
        # Load messages from DB
        messages = await self.get_messages(session_id, limit=self.memory_window)
        
        # Populate memory with recent messages
        for msg in messages:
            if msg["role"] == "user":
                memory.chat_memory.add_message(HumanMessage(content=msg["content"]))
            else:
                memory.chat_memory.add_message(AIMessage(content=msg["content"]))
        
        # Cache the memory
        self._memory_cache[session_id] = memory
        
        return memory
    
    def clear_memory_cache(self, session_id: str):
        """Clear memory cache for a session"""
        if session_id in self._memory_cache:
            del self._memory_cache[session_id]
    
    async def generate_session_title(self, session_id: str) -> str:
        """Generate a concise, descriptive title from the first user message using LangChain"""
        messages = None
        try:
            print(f"[TITLE] Fetching messages for session {session_id}...")
            # Get ALL messages and find the first user message
            all_messages = await self.get_messages(session_id, limit=None)
            print(f"[TITLE] Got {len(all_messages) if all_messages else 0} total messages")
            
            # Find the first user message
            user_message = None
            for msg in all_messages:
                if msg["role"] == "user":
                    user_message = msg
                    break
            
            if user_message:
                from title_generator import generate_chat_title
                content = user_message["content"]
                
                print(f"[TITLE] Calling title generator with content: {content[:100]}...")
                # Use LangChain to generate a smart title
                title = generate_chat_title(content)
                print(f"[TITLE] Title generator returned: {title}")
                return title
            else:
                print("[TITLE] No user messages found in session")
        except Exception as e:
            print(f"[TITLE] Error generating title: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to simple truncation if we have a user message
            if user_message:
                content = user_message["content"]
                title = content[:50].split('.')[0].strip()
                if len(content) > 50:
                    title += "..."
                return title
        
        print("[TITLE] Returning default 'New Chat'")
        return "New Chat"

# Global session manager instance
supabase_session_manager = SupabaseSessionManager(memory_window=10)
