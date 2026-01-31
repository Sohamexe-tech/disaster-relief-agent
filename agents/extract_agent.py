from groq import Groq
import json
from models.schema import Need

# OLD (remove this):
# GROQ_API_KEY = "gsk_..."  

# NEW (add this):
import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
SYSTEM_PROMPT = """Extract disaster needs as JSON ONLY. No extra text.
Schema:
{
  "need_type": "food|medical|rescue|shelter|other",
  "location": "exact location or null",
  "urgency": 1-5,
  "summary": "brief description"
}"""

def extract_need(text: str, source: str = "social_media") -> Need:
    """Extract structured need from raw text using Groq LLM"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"Text: {text}"
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0,
            max_tokens=200
        )
        
        content = chat_completion.choices[0].message.content
        
        # Extract JSON from response
        start = content.find('{')
        end = content.rfind('}') + 1
        
        if start == -1 or end == 0:
            return None
        
        json_str = content[start:end]
        data = json.loads(json_str)
        
        # Add source
        data['source'] = source
        
        return Need(**data)
        
    except Exception as e:
        # Silently fail and let main.py use keyword fallback
        return None