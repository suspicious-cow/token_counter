"""
Validation script to ensure Grok cached token counting is 100% accurate.
"""

from clients.grok_client import process_with_grok
from openai import OpenAI
from config import GROK_API_KEY, MODELS_INFO, GROK_BASE_URL

def validate_grok_cached_tokens():
    """Compare our client implementation with direct API call."""
    
    test_prompt = "Give me one sentence about what a penguin is."
    
    print("=== TESTING GROK CACHED TOKEN EXTRACTION ===")
    print(f"Test prompt: {test_prompt}")
    print()
    
    # Direct API call
    print("1. Direct API call:")
    client = OpenAI(api_key=GROK_API_KEY, base_url=GROK_BASE_URL)
    completion = client.chat.completions.create(
        model=MODELS_INFO["grok"]["model"],
        messages=[{"role": "user", "content": test_prompt}]
    )
    
    api_prompt_tokens = completion.usage.prompt_tokens
    api_completion_tokens = completion.usage.completion_tokens
    api_cached_tokens = completion.usage.prompt_tokens_details.cached_tokens if completion.usage.prompt_tokens_details else 0
    
    print(f"  API prompt_tokens: {api_prompt_tokens}")
    print(f"  API completion_tokens: {api_completion_tokens}")
    print(f"  API cached_tokens: {api_cached_tokens}")
    print()
    
    # Our client implementation
    print("2. Our client implementation:")
    output, client_input_tokens, client_cached_tokens, client_output_tokens = process_with_grok(test_prompt, "")
    
    print(f"  Client input_tokens: {client_input_tokens}")
    print(f"  Client output_tokens: {client_output_tokens}")
    print(f"  Client cached_tokens: {client_cached_tokens}")
    print()
    
    # Validation
    print("3. Validation:")
    input_match = api_prompt_tokens == client_input_tokens
    output_match = api_completion_tokens == client_output_tokens
    cached_match = api_cached_tokens == client_cached_tokens
    
    print(f"  Input tokens match: {input_match} ({api_prompt_tokens} == {client_input_tokens})")
    print(f"  Output tokens match: {output_match} ({api_completion_tokens} == {client_output_tokens})")
    print(f"  Cached tokens match: {cached_match} ({api_cached_tokens} == {client_cached_tokens})")
    
    all_match = input_match and output_match and cached_match
    print(f"  ALL TOKENS MATCH: {all_match}")
    
    if all_match:
        print("\n✅ GROK TOKEN COUNTING IS 100% ACCURATE!")
    else:
        print("\n❌ GROK TOKEN COUNTING HAS DISCREPANCIES!")
        
    # Additional verification: calculated uncached tokens
    api_uncached = api_prompt_tokens - api_cached_tokens
    client_uncached = client_input_tokens - client_cached_tokens if client_cached_tokens is not None else client_input_tokens
    
    print(f"\n4. Uncached token calculation:")
    print(f"  API uncached: {api_uncached} (total: {api_prompt_tokens} - cached: {api_cached_tokens})")
    print(f"  Client uncached: {client_uncached} (total: {client_input_tokens} - cached: {client_cached_tokens})")
    print(f"  Uncached match: {api_uncached == client_uncached}")

if __name__ == "__main__":
    validate_grok_cached_tokens()
