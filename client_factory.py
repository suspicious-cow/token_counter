"""
Client factory for creating LLM provider clients.
"""

from typing import List, Optional
from clients.base_client import BaseLLMClient
from clients.openai_client import OpenAIClient
from clients.gemini_client import GeminiClient
from clients.anthropic_client import AnthropicClient
from clients.grok_client import GrokClient


class ClientFactory:
    """Factory for creating LLM provider clients"""
    
    _clients = {
        'openai': OpenAIClient,
        'gemini': GeminiClient,
        'anthropic': AnthropicClient,
        'grok': GrokClient
    }
    
    @classmethod
    def get_client(cls, provider: str) -> Optional[BaseLLMClient]:
        """
        Get a client instance for the specified provider.
        
        Args:
            provider: Provider name (openai, gemini, anthropic, grok)
            
        Returns:
            BaseLLMClient instance or None if provider not found
        """
        client_class = cls._clients.get(provider.lower())
        if client_class:
            return client_class()
        return None
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available provider names"""
        return list(cls._clients.keys())
    
    @classmethod
    def validate_providers(cls, providers: List[str]) -> List[str]:
        """
        Validate provider names and return valid ones.
        
        Args:
            providers: List of provider names to validate
            
        Returns:
            List of valid provider names
        """
        available = cls.get_available_providers()
        return [p.lower() for p in providers if p.lower() in available]