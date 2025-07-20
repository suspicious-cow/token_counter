"""
Enhanced Gemini client using base client architecture.
Includes backward compatibility functions.
"""

from google import genai
from google.genai import types
from typing import Optional
from .base_client import BaseLLMClient
from config import GEMINI_API_KEY, MODELS_INFO


class GeminiClient(BaseLLMClient):
    """Enhanced Gemini client with standardized interface"""
    
    def __init__(self):
        super().__init__("gemini")
        self.client = genai.Client(api_key=GEMINI_API_KEY)
    
    def _make_api_call(self, prompt: str, system_prompt: str = "", model: Optional[str] = None) -> tuple:
        """Make API call to Gemini"""
        if model is None:
            model = MODELS_INFO["gemini"]["model"]
        
        if system_prompt:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt
            )
        else:
            config = types.GenerateContentConfig()
            
        response = self.client.models.generate_content(
            model=model,
            config=config,
            contents=prompt
        )
        
        output = getattr(response, 'text', str(response))
        usage = getattr(response, 'usage_metadata', None)
        input_tokens = usage.prompt_token_count if usage and hasattr(usage, 'prompt_token_count') else None
        output_tokens = usage.candidates_token_count if usage and hasattr(usage, 'candidates_token_count') else None
        
        # Check for cached token information
        cached_input_tokens = 0
        if usage and hasattr(usage, 'cached_content_token_count'):
            cached_input_tokens = usage.cached_content_token_count or 0
        
        return output, input_tokens, cached_input_tokens, output_tokens
    
    def get_model_name(self) -> str:
        """Get the default model name for Gemini"""
        return MODELS_INFO["gemini"]["model"]


# Backward compatibility functions
def process_with_gemini(prompt, system_prompt, model=None):
    """
    Backward compatibility wrapper for the enhanced client.
    
    Args:
        prompt (str): The user prompt
        system_prompt (str): The system prompt (can be empty)
        model (str): The model to use (defaults to config setting)
    
    Returns:
        tuple: (output, input_tokens, cached_input_tokens, output_tokens)
    """
    try:
        client = GeminiClient()
        response = client.process(prompt, system_prompt, model)
        return response.output, response.usage.input_tokens, response.usage.cached_input_tokens, response.usage.output_tokens
    except Exception as e:
        return f"Gemini error: {str(e)}", None, None, None


def get_model_name():
    """Backward compatibility wrapper"""
    return GeminiClient().get_model_name()