"""
Enhanced Anthropic client using base client architecture.
"""

import anthropic
from typing import Optional
from .base_client import BaseLLMClient
from config import ANTHROPIC_API_KEY, MODELS_INFO, ANTHROPIC_MAX_TOKENS


class AnthropicClient(BaseLLMClient):
    """Enhanced Anthropic client with standardized interface"""
    
    def __init__(self):
        super().__init__("anthropic")
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    def _make_api_call(self, prompt: str, system_prompt: str = "", model: Optional[str] = None) -> tuple:
        """Make API call to Anthropic"""
        if model is None:
            model = MODELS_INFO["anthropic"]["model"]
        
        kwargs = {
            "model": model,
            "max_tokens": ANTHROPIC_MAX_TOKENS,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system_prompt:
            kwargs["system"] = system_prompt
            
        message = self.client.messages.create(**kwargs)
        
        output = message.content[0].text if hasattr(message.content[0], 'text') else str(message.content[0])
        input_tokens = getattr(message.usage, 'input_tokens', None)
        output_tokens = getattr(message.usage, 'output_tokens', None)
        
        # Get caching-related tokens
        cache_creation_tokens = getattr(message.usage, 'cache_creation_input_tokens', 0) or 0
        cache_read_tokens = getattr(message.usage, 'cache_read_input_tokens', 0) or 0
        cached_input_tokens = cache_creation_tokens + cache_read_tokens
        
        return output, input_tokens, cached_input_tokens, output_tokens
    
    def get_model_name(self) -> str:
        """Get the default model name for Anthropic"""
        return MODELS_INFO["anthropic"]["model"]