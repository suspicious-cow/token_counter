"""
Grok client module for token counting.
"""

from openai import OpenAI
from config import GROK_API_KEY, MODELS_INFO, GROK_BASE_URL


def process_with_grok(prompt, system_prompt, model=None):
    """
    Process a prompt using X.AI's Grok API.
    
    Args:
        prompt (str): The user prompt
        system_prompt (str): The system prompt (can be empty)
        model (str): The model to use (defaults to config setting)
    
    Returns:
        tuple: (output, input_tokens, cached_input_tokens, output_tokens)
    """
    if model is None:
        model = MODELS_INFO["grok"]["model"]
    
    try:
        client = OpenAI(
            api_key=GROK_API_KEY,
            base_url=GROK_BASE_URL,
        )
        
        messages = []
        if system_prompt:  # Only add system message if not empty
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        completion = client.chat.completions.create(
            model=model,
            messages=messages
        )
        
        output = completion.choices[0].message.content
        input_tokens = getattr(completion.usage, 'prompt_tokens', None)
        output_tokens = getattr(completion.usage, 'completion_tokens', None)
        
        # Get cached tokens from prompt_tokens_details
        cached_tokens = 0
        if (hasattr(completion, 'usage') and completion.usage and 
            hasattr(completion.usage, 'prompt_tokens_details') and 
            completion.usage.prompt_tokens_details):
            cached_tokens = getattr(completion.usage.prompt_tokens_details, 'cached_tokens', 0) or 0
        
        return output, input_tokens, cached_tokens, output_tokens
    except Exception as e:
        return f"Grok error: {str(e)}", None, 0, None


def get_model_name():
    """Get the default model name for Grok."""
    return MODELS_INFO["grok"]["model"]
