"""
Debug script to inspect Grok API response structure.
"""

from openai import OpenAI
from config import GROK_API_KEY, MODELS_INFO, GROK_BASE_URL
import json

def debug_grok_response():
    """Debug the Grok API response to see cache token structure."""
    try:
        client = OpenAI(
            api_key=GROK_API_KEY,
            base_url=GROK_BASE_URL,
        )
        
        completion = client.chat.completions.create(
            model=MODELS_INFO["grok"]["model"],
            messages=[{"role": "user", "content": "Give me one sentence about what a penguin is."}]
        )
        
        print("=== FULL GROK API RESPONSE ===")
        print(f"Model: {completion.model}")
        print(f"Usage object: {completion.usage}")
        
        if hasattr(completion.usage, 'prompt_tokens'):
            print(f"prompt_tokens: {completion.usage.prompt_tokens}")
        
        if hasattr(completion.usage, 'completion_tokens'):
            print(f"completion_tokens: {completion.usage.completion_tokens}")
            
        if hasattr(completion.usage, 'total_tokens'):
            print(f"total_tokens: {completion.usage.total_tokens}")
        
        print("\n=== CHECKING FOR PROMPT_TOKENS_DETAILS ===")
        if hasattr(completion.usage, 'prompt_tokens_details'):
            print(f"prompt_tokens_details exists: {completion.usage.prompt_tokens_details}")
            details = completion.usage.prompt_tokens_details
            
            # Check all attributes of prompt_tokens_details
            print("prompt_tokens_details attributes:")
            for attr in dir(details):
                if not attr.startswith('_'):
                    value = getattr(details, attr, None)
                    print(f"  {attr}: {value}")
        else:
            print("prompt_tokens_details NOT found")
            
        print("\n=== CHECKING FOR COMPLETION_TOKENS_DETAILS ===")
        if hasattr(completion.usage, 'completion_tokens_details'):
            print(f"completion_tokens_details exists: {completion.usage.completion_tokens_details}")
            details = completion.usage.completion_tokens_details
            
            # Check all attributes
            print("completion_tokens_details attributes:")
            for attr in dir(details):
                if not attr.startswith('_'):
                    value = getattr(details, attr, None)
                    print(f"  {attr}: {value}")
        else:
            print("completion_tokens_details NOT found")
            
        print("\n=== ALL USAGE ATTRIBUTES ===")
        for attr in dir(completion.usage):
            if not attr.startswith('_'):
                value = getattr(completion.usage, attr, None)
                print(f"{attr}: {value}")
                
        # Try to convert to dict to see raw structure
        print("\n=== RAW USAGE DICT (if possible) ===")
        try:
            if hasattr(completion.usage, 'model_dump'):
                usage_dict = completion.usage.model_dump()
                print(json.dumps(usage_dict, indent=2))
            elif hasattr(completion.usage, 'dict'):
                usage_dict = completion.usage.dict()
                print(json.dumps(usage_dict, indent=2))
        except Exception as e:
            print(f"Could not convert to dict: {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_grok_response()
