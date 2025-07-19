"""
Abstract base client for LLM providers.
Provides consistent interface and shared functionality.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
from config import MODELS_INFO


@dataclass
class TokenUsage:
    """Token usage information from API response"""
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int


@dataclass
class LLMResponse:
    """Standardized response from LLM providers"""
    output: str
    usage: TokenUsage
    cost: float
    model: str


class BaseLLMClient(ABC):
    """Abstract base class for all LLM clients"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
    
    @abstractmethod
    def _make_api_call(self, prompt: str, system_prompt: str = "", model: Optional[str] = None) -> tuple:
        """
        Make the actual API call to the provider.
        
        Returns:
            tuple: (output, input_tokens, cached_input_tokens, output_tokens)
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the default model name for this provider"""
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model configuration and pricing info"""
        return MODELS_INFO[self.provider_name]
    
    def calculate_cost(self, usage: TokenUsage) -> float:
        """Standardized cost calculation across all providers"""
        model_info = self.get_model_info()
        uncached_input = max(usage.input_tokens - usage.cached_input_tokens, 0)
        
        input_cost = uncached_input * model_info['input_cost_per_million'] / 1_000_000
        cached_cost = usage.cached_input_tokens * model_info['cached_input_cost_per_million'] / 1_000_000
        output_cost = usage.output_tokens * model_info['output_cost_per_million'] / 1_000_000
        
        return round(input_cost + cached_cost + output_cost, 6)
    
    def process(self, prompt: str, system_prompt: str = "", model: Optional[str] = None) -> LLMResponse:
        """
        Process a prompt and return standardized response.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system instructions
            model: Optional model override
            
        Returns:
            LLMResponse with output, usage, and cost information
        """
        try:
            output, input_tokens, cached_input_tokens, output_tokens = self._make_api_call(
                prompt, system_prompt, model
            )
            
            # Handle error responses
            if isinstance(output, str) and output.startswith("Error:"):
                return LLMResponse(
                    output=output,
                    usage=TokenUsage(0, 0, 0),
                    cost=0.0,
                    model=model or self.get_model_name()
                )
            
            usage = TokenUsage(
                input_tokens=input_tokens or 0,
                cached_input_tokens=cached_input_tokens or 0,
                output_tokens=output_tokens or 0
            )
            
            cost = self.calculate_cost(usage)
            
            return LLMResponse(
                output=output,
                usage=usage,
                cost=cost,
                model=model or self.get_model_name()
            )
            
        except Exception as e:
            return LLMResponse(
                output=f"Error: {str(e)}",
                usage=TokenUsage(0, 0, 0),
                cost=0.0,
                model=model or self.get_model_name()
            )