"""
Automatic Speech Recognition (ASR) module using Gemini and LangChain.
"""

import os
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

class Transcription(BaseModel):
    """Transcription of audio content to text."""
    text: str = Field(description="The exact transcription of the speech from the audio file. Only transcribe what is spoken, nothing else.")

def transcribe_audio(audio_data: bytes, mime_type: str = "audio/webm") -> str:
    """
    Transcribe audio using Gemini with structured output.
    
    Args:
        audio_data: Raw audio data as bytes
        mime_type: MIME type of the audio (e.g., "audio/webm", "audio/mpeg")
    
    Returns:
        Transcribed text from the audio
    """
    
    # Initialize Gemini model with structured output
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        api_key=os.environ.get("GOOGLE_API_KEY"),
    )
    
    # Use with_structured_output to force schema compliance
    structured_model = model.with_structured_output(Transcription)
    
    # Create message with audio content
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "Transcribe the speech from this audio file. Only transcribe what is spoken, nothing else."
            },
            {
                "type": "media",
                "mime_type": mime_type,
                "data": audio_data,
            }
        ]
    )
    
    # Get structured transcription
    result: Transcription = structured_model.invoke([message])
    
    return result.text
