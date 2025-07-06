"""
OpenAI client module for token counting.
"""

from openai import OpenAI
from config import OPENAI_API_KEY, MODELS


def process_with_openai(prompt, system_prompt, model=None):
    """
    Process a prompt using OpenAI's API.
    
    Args:
        prompt (str): The user prompt
        system_prompt (str): The system prompt (can be empty)
        model (str): The model to use (defaults to config setting)
    
    Returns:
        tuple: (output, input_tokens, cached_input_tokens, output_tokens)
    """
    if model is None:
        model = MODELS["openai"]
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        messages = []
        if system_prompt:  # Only add system message if not empty
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        
        output = response.choices[0].message.content
        input_tokens = getattr(response.usage, 'prompt_tokens', None)
        output_tokens = getattr(response.usage, 'completion_tokens', None)
        
        # Get cached input tokens if available (OpenAI only)
        cached_input_tokens = None
        prompt_tokens_details = getattr(response.usage, 'prompt_tokens_details', None)
        if prompt_tokens_details:
            if isinstance(prompt_tokens_details, dict):
                cached_input_tokens = prompt_tokens_details.get('cached_tokens', None)
            else:
                cached_input_tokens = getattr(prompt_tokens_details, 'cached_tokens', None)
        return output, input_tokens, cached_input_tokens, output_tokens
    except Exception as e:
        return f"OpenAI ChatCompletions error: {str(e)}", None, None, None


def get_model_name():
    """Get the default model name for OpenAI."""
    return MODELS["openai"]
