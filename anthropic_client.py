"""
Anthropic client module for token counting.
"""

import anthropic
from config import ANTHROPIC_API_KEY, MODELS, ANTHROPIC_MAX_TOKENS


def process_with_anthropic(prompt, system_prompt, model=None):
    """
    Process a prompt using Anthropic's Claude API.
    
    Args:
        prompt (str): The user prompt
        system_prompt (str): The system prompt (can be empty)
        model (str): The model to use (defaults to config setting)
    
    Returns:
        tuple: (output, input_tokens, output_tokens)
    """
    if model is None:
        model = MODELS["anthropic"]
    
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
        input_tokens = getattr(message.usage, 'input_tokens', None)
        output_tokens = getattr(message.usage, 'output_tokens', None)
        
        return output, input_tokens, output_tokens
    except Exception as e:
        return f"Anthropic error: {str(e)}", None, None


def get_model_name():
    """Get the default model name for Anthropic."""
    return MODELS["anthropic"]
