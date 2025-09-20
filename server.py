from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
import mimetypes
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from main import create_agent_with_memory
from session_manager import session_manager

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