"""
Enhanced OpenAI client using base client architecture.
"""

from openai import OpenAI
from typing import Optional
from .base_client import BaseLLMClient
from config import OPENAI_API_KEY, MODELS_INFO


class OpenAIClient(BaseLLMClient):
    """Enhanced OpenAI client with standardized interface"""
    
    def __init__(self):
        super().__init__("openai")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def _make_api_call(self, prompt: str, system_prompt: str = "", model: Optional[str] = None) -> tuple:
        """Make API call to OpenAI"""
        if model is None:
            model = MODELS_INFO["openai"]["model"]
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages
        )
        
        output = response.choices[0].message.content
        input_tokens = getattr(response.usage, 'prompt_tokens', None)
        output_tokens = getattr(response.usage, 'completion_tokens', None)
        
        # Get cached input tokens if available
        cached_input_tokens = 0
        prompt_tokens_details = getattr(response.usage, 'prompt_tokens_details', None)
        if prompt_tokens_details:
            if isinstance(prompt_tokens_details, dict):
                cached_input_tokens = prompt_tokens_details.get('cached_tokens', 0) or 0
            else:
                cached_input_tokens = getattr(prompt_tokens_details, 'cached_tokens', 0) or 0
        
        return output, input_tokens, cached_input_tokens, output_tokens
    
    def get_model_name(self) -> str:
        """Get the default model name for OpenAI"""
        return MODELS_INFO["openai"]["model"]