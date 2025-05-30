"""
Gemini client module for token counting.
"""

from google import genai
from google.genai import types
from config import GEMINI_API_KEY, MODELS


def process_with_gemini(prompt, system_prompt, model=None):
    """
    Process a prompt using Google's Gemini API.
    
    Args:
        prompt (str): The user prompt
        system_prompt (str): The system prompt (can be empty)
        model (str): The model to use (defaults to config setting)
    
    Returns:
        tuple: (output, input_tokens, output_tokens)
    """
    if model is None:
        model = MODELS["gemini"]
    
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Create config with system instruction only if not empty
        config = types.GenerateContentConfig()
        if system_prompt:
            # Add system instruction if provided
            config = types.GenerateContentConfig(system_instruction=system_prompt)
            
        response = client.models.generate_content(
            model=model,
            config=config,
            contents=prompt
        )
        
        # Use response.text to preserve the actual LLM output (including newlines for accurate token counting)
        output = getattr(response, 'text', str(response))
        usage = getattr(response, 'usage_metadata', None)
        input_tokens = usage.prompt_token_count if usage and hasattr(usage, 'prompt_token_count') else None
        output_tokens = usage.candidates_token_count if usage and hasattr(usage, 'candidates_token_count') else None
        
        return output, input_tokens, output_tokens
    except Exception as e:
        return f"Gemini error: {str(e)}", None, None


def get_model_name():
    """Get the default model name for Gemini."""
    return MODELS["gemini"]
