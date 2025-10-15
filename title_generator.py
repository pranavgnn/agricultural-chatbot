"""
Title generator for chat sessions using simple text generation with Gemma.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def generate_chat_title(user_message: str) -> str:
    """
    Generate a short, descriptive title based on the user's first message.
    
    Args:
        user_message: The first message from the user
    
    Returns:
        A short title (3-7 words) for the chat session
    """
    
    try:
        print(f"[TITLE GEN] Starting title generation for message: {user_message[:100]}")
        
        # Initialize small Gemma model for fast title generation
        model = ChatGoogleGenerativeAI(
            model="gemma-3-1b-it",  # Small, fast model
            api_key=os.environ.get("GOOGLE_API_KEY"),
            temperature=0.2,  # Low temperature for consistent, focused output
        )
        
        print("[TITLE GEN] Model initialized")
        
        # Create a single prompt with instructions and examples (Gemma doesn't support system messages)
        prompt = f"""Task: Generate a short, descriptive title for a chat conversation.

Instructions:
- Output ONLY the title text, nothing else
- Keep it 3-7 words maximum
- Use sentence case (capitalize first word only)
- No quotes, no punctuation at the end
- Make it clear and descriptive

Examples:
Input: "What's the weather in Delhi today?"
Output: Weather forecast for Delhi

Input: "How do I grow tomatoes in the monsoon season?"
Output: Growing tomatoes in monsoon

Input: "Which fertilizer is best for wheat crops?"
Output: Best fertilizer for wheat

Input: "Tell me about pest control methods for cotton"
Output: Pest control for cotton

Input: "Government schemes for farmers"
Output: Government schemes for farmers

Now generate a title for this input:
Input: "{user_message}"
Output:"""
        
        print("[TITLE GEN] Invoking model...")
        # Get response - use invoke with string prompt (no system messages)
        response = model.invoke(prompt)
        
        # Extract title from response
        title = response.content.strip()
        
        # Clean up the title (remove quotes if present, remove "Title:" prefix if added)
        title = title.strip('"').strip("'").strip()
        if title.lower().startswith("title:"):
            title = title[6:].strip()
        
        # Take only the first line (in case model generates extra text)
        title = title.split('\n')[0].strip()
        
        # Truncate if too long
        if len(title) > 60:
            title = title[:60].strip()
        
        print(f"[TITLE GEN] Generated title: {title}")
        
        return title
    
    except Exception as e:
        print(f"[TITLE GEN] ERROR: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to simple truncation
        title = user_message[:50].split('.')[0].strip()
        if len(user_message) > 50:
            title += "..."
        print(f"[TITLE GEN] Returning fallback title: {title}")
        return title
