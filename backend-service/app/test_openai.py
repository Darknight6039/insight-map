"""
Test direct OpenAI pour identifier le problème
"""

import os
from openai import OpenAI

def test_simple_openai():
    """Test basique OpenAI"""
    api_key = os.getenv("OPENAI_API_KEY", "")
    
    if not api_key:
        return {"error": "No API key"}
    
    try:
        # Test direct avec nouvelle syntaxe
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=50
        )
        
        return {"success": True, "response": response.choices[0].message.content}
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    result = test_simple_openai()
    print(result)
