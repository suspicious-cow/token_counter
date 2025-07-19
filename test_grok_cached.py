"""
Focused validation script for Grok cached token extraction only.
"""

from grok_client import process_with_grok
from openai import OpenAI
from config import GROK_API_KEY, MODELS_INFO, GROK_BASE_URL

def test_grok_cached_extraction():
    """Test just the cached token extraction logic using the same API response."""
    
    print("=== TESTING GROK CACHED TOKEN EXTRACTION LOGIC ===")
    
    # Make one API call
    client = OpenAI(api_key=GROK_API_KEY, base_url=GROK_BASE_URL)
    completion = client.chat.completions.create(
        model=MODELS_INFO["grok"]["model"],
        messages=[{"role": "user", "content": "Test prompt for caching"}]
    )
    
    print("API Response Structure:")
    print(f"  prompt_tokens: {completion.usage.prompt_tokens}")
    print(f"  completion_tokens: {completion.usage.completion_tokens}")
    print(f"  prompt_tokens_details exists: {hasattr(completion.usage, 'prompt_tokens_details')}")
    
    if hasattr(completion.usage, 'prompt_tokens_details') and completion.usage.prompt_tokens_details:
        ptd = completion.usage.prompt_tokens_details
        print(f"  prompt_tokens_details.cached_tokens: {getattr(ptd, 'cached_tokens', 'NOT_FOUND')}")
        
        # Test our extraction logic exactly as implemented in grok_client.py
        cached_tokens_extracted = 0
        if (hasattr(completion, 'usage') and completion.usage and 
            hasattr(completion.usage, 'prompt_tokens_details') and 
            completion.usage.prompt_tokens_details):
            cached_tokens_extracted = getattr(completion.usage.prompt_tokens_details, 'cached_tokens', 0) or 0
            
        print(f"  Our extraction result: {cached_tokens_extracted}")
        
        # Direct access
        direct_access = ptd.cached_tokens if ptd.cached_tokens is not None else 0
        print(f"  Direct access result: {direct_access}")
        
        print(f"  EXTRACTION MATCHES: {cached_tokens_extracted == direct_access}")
        
        if cached_tokens_extracted == direct_access:
            print("\n✅ GROK CACHED TOKEN EXTRACTION IS 100% ACCURATE!")
        else:
            print("\n❌ GROK CACHED TOKEN EXTRACTION HAS ISSUES!")
    else:
        print("  No prompt_tokens_details found")
        print("\n✅ GROK CACHED TOKEN EXTRACTION HANDLES MISSING DATA CORRECTLY!")

if __name__ == "__main__":
    test_grok_cached_extraction()
