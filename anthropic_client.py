"""
Anthropic client module for token counting.
"""

import anthropic
from config import ANTHROPIC_API_KEY, MODELS_INFO, ANTHROPIC_MAX_TOKENS


def process_with_anthropic(prompt, system_prompt, model=None):
    """
    Process a prompt using Anthropic's Claude API.
    
    Args:
        prompt (str): The user prompt
        system_prompt (str): The system prompt (can be empty)
        model (str): The model to use (defaults to config setting)
    
    Returns:
        tuple: (output, input_tokens, cached_input_tokens, output_tokens)
        Note: For Anthropic, cached_input_tokens includes both cache_creation_input_tokens and cache_read_input_tokens
    """
    if model is None:
        model = MODELS_INFO["anthropic"]["model"]
    
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # Create message with system prompt only if not empty
        kwargs = {
            "model": model,
            "max_tokens": ANTHROPIC_MAX_TOKENS,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system_prompt:  # Only add system if not empty
            kwargs["system"] = system_prompt
            
        message = client.messages.create(**kwargs)
        
        output = message.content[0].text if hasattr(message.content[0], 'text') else str(message.content[0])
        
        # Get token counts from usage
        input_tokens = getattr(message.usage, 'input_tokens', None)
        output_tokens = getattr(message.usage, 'output_tokens', None)
        
        # Get caching-related tokens (these may be 0 or None if no caching occurred)
        cache_creation_tokens = getattr(message.usage, 'cache_creation_input_tokens', 0) or 0
        cache_read_tokens = getattr(message.usage, 'cache_read_input_tokens', 0) or 0
        
        # Total cached tokens = tokens written to cache + tokens read from cache
        cached_input_tokens = cache_creation_tokens + cache_read_tokens
        
        return output, input_tokens, cached_input_tokens, output_tokens
    except Exception as e:
        return f"Anthropic error: {str(e)}", None, 0, None


def get_model_name():
    """Get the default model name for Anthropic."""
    return MODELS_INFO["anthropic"]["model"]
