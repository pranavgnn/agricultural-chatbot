from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from main import agent_executor

app = FastAPI()

class ChatRequest(BaseModel):
    text: str

@app.post("/chat")
async def chat(request: ChatRequest):
    response = agent_executor.invoke({"text": request.text})
    return response

if __name__ == "__main__":
    uvicorn.run(app)