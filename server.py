from fastapi import FastAPI, HTTPException, Header, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
import uvicorn
import os
import mimetypes
import tempfile
import time
from pathlib import Path
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from main import create_agent_with_memory
from supabase_session_manager import supabase_session_manager
from session_manager import SessionManager
import google.generativeai as genai
from auth_service import auth_service, get_current_user_dependency

# Initialize in-memory session manager for anonymous users or when DB is unavailable
in_memory_session_manager = SessionManager()

# Optional auth dependency for endpoints that can work without auth
async def get_optional_user(authorization: str = Header(None)) -> Optional[dict]:
    """Get user if authenticated, otherwise return None"""
    if not authorization:
        return None
    
    try:
        token = authorization.replace("Bearer ", "")
        user = await auth_service.get_current_user(token)
        return user
    except:
        return None

# Ensure correct MIME types are registered
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')

app = FastAPI(title="Kheti - Agricultural AI Assistant", description="AI-powered agricultural assistant for Indian farmers")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files FIRST (before route definitions)
static_dir = Path(__file__).parent / "frontend" / "dist"
if static_dir.exists():
    # Mount the entire dist directory to serve all static files
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")
    # Also mount any other static files from dist root
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

class ChatRequest(BaseModel):
    text: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    output: str
    session_id: str
    title: Optional[str] = None

class SessionCreate(BaseModel):
    title: Optional[str] = "New Chat"
    is_public: bool = False

class SessionUpdate(BaseModel):
    title: Optional[str] = None
    is_public: Optional[bool] = None

# Authentication Models
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class MagicLinkRequest(BaseModel):
    email: EmailStr

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Authentication Endpoints
@app.post("/auth/signup")
async def sign_up(request: SignUpRequest):
    """Sign up a new user with email and password"""
    metadata = {"name": request.name} if request.name else {}
    return await auth_service.sign_up_with_email(request.email, request.password, metadata)

@app.post("/auth/signin")
async def sign_in(request: SignInRequest):
    """Sign in with email and password"""
    return await auth_service.sign_in_with_email(request.email, request.password)

@app.post("/auth/magic-link")
async def send_magic_link(request: MagicLinkRequest):
    """Send a magic link to user's email"""
    return await auth_service.sign_in_with_magic_link(request.email)

@app.get("/auth/google")
async def google_auth():
    """Initiate Google OAuth sign in"""
    return await auth_service.sign_in_with_google()

@app.post("/auth/signout")
async def sign_out(authorization: str = Header(None)):
    """Sign out the current user"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    token = authorization.replace("Bearer ", "")
    return await auth_service.sign_out(token)

@app.post("/auth/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """Refresh the user's session"""
    return await auth_service.refresh_session(request.refresh_token)

@app.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user_dependency)):
    """Get current authenticated user"""
    return current_user

@app.get("/auth/callback")
async def auth_callback():
    """OAuth callback endpoint"""
    return RedirectResponse(url="/?auth=success")

# ASR (Speech-to-Text) Endpoint
@app.post("/asr/transcribe")
async def transcribe_audio_endpoint(audio: UploadFile = File(...)):
    """Transcribe audio file using Gemini ASR with structured output"""
    try:
        # Read the uploaded audio file
        audio_data = await audio.read()
        
        # Import the ASR module
        from asr import transcribe_audio
        
        # Get transcription using LangChain structured output
        transcription = transcribe_audio(
            audio_data=audio_data,
            mime_type=audio.content_type or "audio/webm"
        )
        
        return {"transcription": transcription, "success": True}
    
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")

# Chat Session Endpoints
@app.post("/chat/sessions")
async def create_chat_session(
    request: SessionCreate,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Create a new chat session"""
    try:
        session_id = await supabase_session_manager.create_session(
            user_id=current_user["id"],
            title=request.title,
            is_public=request.is_public
        )
        return {"session_id": session_id, "title": request.title, "is_public": request.is_public}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@app.get("/chat/sessions")
async def get_user_sessions(current_user: dict = Depends(get_current_user_dependency)):
    """Get all sessions for the current user"""
    try:
        sessions = await supabase_session_manager.get_user_sessions(current_user["id"])
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sessions: {str(e)}")

@app.get("/chat/sessions/{session_id}")
async def get_session(
    session_id: str, 
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Get a specific session with its messages - works for both authenticated and public access"""
    try:
        # Try to get the session
        session = await supabase_session_manager.get_session(
            session_id, 
            user_id=current_user["id"] if current_user else None
        )
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check access permissions
        if current_user:
            # Authenticated user - can access own sessions or public sessions
            if session["user_id"] != current_user["id"] and not session["is_public"]:
                raise HTTPException(status_code=403, detail="Access denied to this private session")
        else:
            # Anonymous user - can only access public sessions
            if not session["is_public"]:
                raise HTTPException(status_code=403, detail="This session is private. Please sign in to view.")
        
        messages = await supabase_session_manager.get_messages(session_id)
        return {
            "session": session,
            "messages": messages
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching session: {str(e)}")

@app.get("/chat/sessions/{session_id}/public")
async def get_public_session(session_id: str):
    """Get a public session (no auth required)"""
    try:
        session = await supabase_session_manager.get_session(session_id, user_id=None)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if not session["is_public"]:
            raise HTTPException(status_code=403, detail="This session is private")
        
        messages = await supabase_session_manager.get_messages(session_id)
        return {
            "session": session,
            "messages": messages
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching session: {str(e)}")

@app.post("/chat/sessions/{session_id}/fork")
async def fork_session(
    session_id: str,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Fork/copy a public session to continue chatting.
    - If authenticated: Creates a copy in user's account
    - If anonymous: Creates a temporary session with the history
    """
    try:
        # Get the original session (must be public or owned by user)
        original_session = await supabase_session_manager.get_session(
            session_id,
            user_id=current_user["id"] if current_user else None
        )
        
        if not original_session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if user can fork this session
        if current_user:
            # Authenticated users can fork their own sessions or public sessions
            if original_session["user_id"] != current_user["id"] and not original_session["is_public"]:
                raise HTTPException(status_code=403, detail="Cannot fork private sessions")
        else:
            # Anonymous users can only fork public sessions
            if not original_session["is_public"]:
                raise HTTPException(status_code=403, detail="Cannot fork private sessions")
        
        # Get original messages
        original_messages = await supabase_session_manager.get_messages(session_id)
        
        # Create new session
        if current_user:
            # Authenticated user - create persistent session
            try:
                new_session_id = await supabase_session_manager.create_session(
                    user_id=current_user["id"],
                    title=f"Fork of {original_session['title']}",
                    is_public=False  # Forked sessions are private by default
                )
                
                # Copy all messages to new session
                for msg in original_messages:
                    await supabase_session_manager.add_message(
                        new_session_id,
                        msg["role"],
                        msg["content"]
                    )
                
                return {
                    "session_id": new_session_id,
                    "message": "Session forked successfully",
                    "type": "persistent"
                }
            except Exception as e:
                print(f"Could not create database session: {e}")
                # Fallback to temp session
                import uuid
                new_session_id = f"temp-{str(uuid.uuid4())}"
        else:
            # Anonymous user - create temporary session
            import uuid
            new_session_id = f"anon-{str(uuid.uuid4())}"
        
        # For temporary/anonymous sessions, copy messages to in-memory
        _, memory = in_memory_session_manager.get_or_create_session(new_session_id)
        for msg in original_messages:
            if msg["role"] == "user":
                memory.chat_memory.add_user_message(msg["content"])
            else:
                memory.chat_memory.add_ai_message(msg["content"])
        
        return {
            "session_id": new_session_id,
            "message": "Session forked successfully",
            "type": "temporary" if current_user else "anonymous"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error forking session: {str(e)}")

@app.patch("/chat/sessions/{session_id}")
async def update_session(
    session_id: str,
    request: SessionUpdate,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Update session (title, is_public, etc.)"""
    try:
        update_data = {}
        if request.title is not None:
            update_data["title"] = request.title
        if request.is_public is not None:
            update_data["is_public"] = request.is_public
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        success = await supabase_session_manager.update_session(
            session_id, current_user["id"], **update_data
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found or update failed")
        
        return {"message": "Session updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating session: {str(e)}")

@app.delete("/chat/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Delete a session"""
    try:
        success = await supabase_session_manager.delete_session(session_id, current_user["id"])
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Chat endpoint - works with or without authentication.
    - Authenticated users: Sessions saved to database (if available)
    - Anonymous users: Sessions are temporary (in-memory only)
    """
    try:
        session_id = request.session_id
        use_database = False
        
        # If no session_id provided, create a new one
        if not session_id:
            if current_user:
                # Authenticated user - try to create persistent session
                try:
                    session_id = await supabase_session_manager.create_session(
                        user_id=current_user["id"],
                        title="New Chat"
                    )
                    use_database = True
                except Exception as e:
                    print(f"Could not create database session, using in-memory: {e}")
                    # Fallback to in-memory session
                    import uuid
                    session_id = f"temp-{str(uuid.uuid4())}"
                    use_database = False
            else:
                # Anonymous user - create temporary session
                import uuid
                session_id = f"anon-{str(uuid.uuid4())}"
                use_database = False
        else:
            # Check if this is a persistent session or temporary
            if current_user and not (session_id.startswith("anon-") or session_id.startswith("temp-")):
                # Try to use database
                try:
                    session = await supabase_session_manager.get_session(session_id, current_user["id"])
                    if session:
                        use_database = True
                    else:
                        raise HTTPException(status_code=403, detail="Access denied to this session")
                except HTTPException:
                    raise
                except Exception as e:
                    print(f"Could not access database session, using in-memory: {e}")
                    use_database = False
        
        # Get or create memory for this session
        if use_database:
            # Authenticated user with persistent session - use database
            try:
                memory = await supabase_session_manager.get_or_create_memory(session_id)
                await supabase_session_manager.add_message(session_id, "user", request.text)
            except Exception as e:
                print(f"Database error, falling back to in-memory: {e}")
                use_database = False
                _, memory = in_memory_session_manager.get_or_create_session(session_id)
        
        if not use_database:
            # Anonymous user or temporary session - use in-memory only
            _, memory = in_memory_session_manager.get_or_create_session(session_id)
        
        # Generate response
        agent_executor = create_agent_with_memory(memory)
        response = agent_executor.invoke({"text": request.text})
        
        generated_title = None
        
        # Save assistant response (only for database sessions)
        if use_database:
            try:
                await supabase_session_manager.add_message(session_id, "assistant", response["output"])
                
                # Auto-generate title from first message if still "New Chat"
                session = await supabase_session_manager.get_session(session_id, current_user["id"])
                print(f"Session after response: {session}")
                
                if session and session["title"] == "New Chat":
                    print(f"Generating title for session {session_id}...")
                    new_title = await supabase_session_manager.generate_session_title(session_id)
                    print(f"Generated title: {new_title}")
                    
                    await supabase_session_manager.update_session(session_id, current_user["id"], title=new_title)
                    generated_title = new_title
                else:
                    generated_title = session.get("title") if session else None
                    
            except Exception as e:
                print(f"Could not save to database or generate title: {e}")
                import traceback
                traceback.print_exc()
        
        return ChatResponse(
            output=response["output"],
            session_id=session_id,
            title=generated_title
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/chat/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe audio to text using Gemini"""
    try:
        # Configure Gemini API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not configured")
        
        genai.configure(api_key=api_key)
        
        # Read the audio file
        audio_data = await audio.read()
        
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file received")
        
        # Save to temporary file with proper extension
        suffix = ".webm" if audio.content_type == "audio/webm" else ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name
        
        try:
            # Upload the audio file to Gemini
            print(f"Uploading audio file: {temp_audio_path}, size: {len(audio_data)} bytes")
            audio_file = genai.upload_file(temp_audio_path)
            
            # Wait for file to be processed
            while audio_file.state.name == "PROCESSING":
                time.sleep(0.5)
                audio_file = genai.get_file(audio_file.name)
            
            if audio_file.state.name == "FAILED":
                raise Exception("Audio file processing failed")
            
            # Use Gemini to transcribe
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = "Transcribe the speech in this audio file. Return ONLY the transcribed text without any additional commentary, formatting, or explanations."
            
            response = model.generate_content([prompt, audio_file])
            transcribed_text = response.text.strip()
            
            # Delete the uploaded file from Gemini
            genai.delete_file(audio_file.name)
            
            print(f"Transcription successful: {transcribed_text[:100]}...")
            
            return {
                "transcription": transcribed_text,
                "success": True
            }
        
        except Exception as inner_error:
            print(f"Inner error during transcription: {str(inner_error)}")
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(inner_error)}")
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")

# Deprecated endpoints (kept for backwards compatibility)
@app.post("/chat/new-session")
async def new_session_deprecated(current_user: dict = Depends(get_current_user_dependency)):
    """Create a new chat session (deprecated, use POST /chat/sessions)"""
    try:
        session_id = await supabase_session_manager.create_session(
            user_id=current_user["id"],
            title="New Chat"
        )
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@app.delete("/chat/session/{session_id}")
async def clear_session_deprecated(
    session_id: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Clear a specific session (deprecated, use DELETE /chat/sessions/{session_id})"""
    try:
        success = await supabase_session_manager.delete_session(session_id, current_user["id"])
        if success:
            return {"message": "Session cleared successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing session: {str(e)}")

# Frontend routes (using static_dir defined at the top)
@app.get("/")
async def serve_frontend():
    """Serve the React frontend"""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Frontend not built. Run: cd frontend && npm run build"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Kheti - Agricultural AI Assistant"}

# Catch-all route for React Router (SPA routing) - MUST be last
@app.get("/{path:path}")
async def serve_spa(path: str):
    """Serve React app for any unmatched routes (SPA routing)"""
    # Only skip actual API routes
    if path.startswith(("api/", "health", "chat/sessions")):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Check if it's an auth API route
    if path.startswith("auth/"):
        raise HTTPException(status_code=404, detail="Not found")
    
    # For everything else including /chat/:id (frontend routes), serve index.html
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Frontend not built. Run: cd frontend && npm run build"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)