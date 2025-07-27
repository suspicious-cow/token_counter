"""
Enhanced Grok client using base client architecture.
Includes backward compatibility functions.
"""

from openai import OpenAI
from typing import Optional
from .base_client import BaseLLMClient
from config import GROK_API_KEY, MODELS_INFO, GROK_BASE_URL


class GrokClient(BaseLLMClient):
    """Enhanced Grok client with standardized interface"""
    
    def __init__(self):
        super().__init__("grok")
        self.client = OpenAI(
            api_key=GROK_API_KEY,
            base_url=GROK_BASE_URL,
        )
    
    def _make_api_call(self, prompt: str, system_prompt: str = "", model: Optional[str] = None) -> tuple:
        """Make API call to Grok"""
        if model is None:
            model = MODELS_INFO["grok"]["model"]
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        completion = self.client.chat.completions.create(
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
        
        # BREAKTHROUGH: Get reasoning tokens from completion_tokens_details!
        reasoning_tokens = 0
        if (hasattr(completion, 'usage') and completion.usage and 
            hasattr(completion.usage, 'completion_tokens_details') and 
            completion.usage.completion_tokens_details):
            reasoning_tokens = getattr(completion.usage.completion_tokens_details, 'reasoning_tokens', 0) or 0
        
        return output, input_tokens, cached_tokens, output_tokens, reasoning_tokens
    
    def get_model_name(self) -> str:
        """Get the default model name for Grok"""
        return MODELS_INFO["grok"]["model"]


# Backward compatibility functions
def process_with_grok(prompt, system_prompt, model=None):
    """
    Backward compatibility wrapper for the enhanced client.
    
    Args:
        prompt (str): The user prompt
        system_prompt (str): The system prompt (can be empty)
        model (str): The model to use (defaults to config setting)
    
    Returns:
        tuple: (output, input_tokens, cached_input_tokens, output_tokens, reasoning_tokens)
    """
    try:
        client = GrokClient()
        output, input_tokens, cached_tokens, output_tokens, reasoning_tokens = client._make_api_call(prompt, system_prompt, model)
        return output, input_tokens, cached_tokens, output_tokens, reasoning_tokens
    except Exception as e:
        return f"Grok error: {str(e)}", None, 0, None, 0


def get_model_name():
    """Backward compatibility wrapper"""
    return GrokClient().get_model_name()