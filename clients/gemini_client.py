"""
Enhanced Gemini client using base client architecture.
"""

from google import genai
from google.genai import types
from typing import Optional
from .base_client import BaseLLMClient
from config import GEMINI_API_KEY, MODELS_INFO, GEMINI_THINKING_BUDGET


class GeminiClient(BaseLLMClient):
    """Enhanced Gemini client with standardized interface"""
    
    def __init__(self):
        super().__init__("gemini")
        self.client = genai.Client(api_key=GEMINI_API_KEY)
    
    def _make_api_call(self, prompt: str, system_prompt: str = "", model: Optional[str] = None) -> tuple:
        """Make API call to Gemini"""
        if model is None:
            model = MODELS_INFO["gemini"]["model"]
        
        # Create thinking configuration
        thinking_config = types.ThinkingConfig(thinking_budget=GEMINI_THINKING_BUDGET)
        
        if system_prompt:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                thinking_config=thinking_config
            )
        else:
            config = types.GenerateContentConfig(
                thinking_config=thinking_config
            )
            
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