from fastapi import FastAPI, HTTPException, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
import mimetypes
import tempfile
import time
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from main import create_agent_with_memory
from session_manager import session_manager
import google.generativeai as genai

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

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        session_id, memory = session_manager.get_or_create_session(request.session_id)
        agent_executor = create_agent_with_memory(memory)
        response = agent_executor.invoke({"text": request.text})
        
        return ChatResponse(
            output=response["output"],
            session_id=session_id
        )
    
    except Exception as e:
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

@app.post("/chat/new-session")
async def new_session():
    """Create a new chat session"""
    session_id, _ = session_manager.get_or_create_session()
    return {"session_id": session_id}

@app.delete("/chat/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a specific session"""
    success = session_manager.clear_session(session_id)
    if success:
        return {"message": "Session cleared successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/chat/sessions/stats")
async def get_session_stats():
    """Get session statistics"""
    active_sessions = session_manager.get_session_count()
    cleaned_sessions = session_manager.cleanup_old_sessions()
    
    return {
        "active_sessions": active_sessions,
        "cleaned_old_sessions": cleaned_sessions,
        "max_sessions": session_manager.max_sessions
    }

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
    # Skip API routes - assets are handled by mount above
    if path.startswith(("chat", "health")):
        raise HTTPException(status_code=404, detail="Not found")
    
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Frontend not built. Run: cd frontend && npm run build"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)