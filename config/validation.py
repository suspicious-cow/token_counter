"""
Configuration validation utilities.
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class APIConfig:
    """Configuration for an API provider"""
    key: str
    model: str
    base_url: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate that API key is properly set"""
        return (
            self.key and 
            self.key != "your-openai-api-key" and
            self.key != "your-anthropic-api-key" and
            self.key != "your-gemini-api-key" and
            self.key != "your-grok-api-key" and
            not self.key.startswith("your-")
        )


def validate_api_keys() -> Dict[str, bool]:
    """
    Validate all API keys are properly set.
    
    Returns:
        Dict mapping provider names to validation status
    """
    from config import (
        OPENAI_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY, GROK_API_KEY,
        MODELS_INFO, GROK_BASE_URL
    )
    
    configs = {
        'openai': APIConfig(OPENAI_API_KEY, MODELS_INFO['openai']['model']),
        'gemini': APIConfig(GEMINI_API_KEY, MODELS_INFO['gemini']['model']),
        'anthropic': APIConfig(ANTHROPIC_API_KEY, MODELS_INFO['anthropic']['model']),
        'grok': APIConfig(GROK_API_KEY, MODELS_INFO['grok']['model'], GROK_BASE_URL)
    }
    
    return {name: config.validate() for name, config in configs.items()}


def get_valid_providers():
    """Get list of providers with valid API keys"""
    validation_results = validate_api_keys()
    return [provider for provider, is_valid in validation_results.items() if is_valid]


def print_validation_report():
    """Print a validation report for all providers"""
    validation_results = validate_api_keys()
    
    print("API Key Validation Report:")
    print("-" * 30)
    
    for provider, is_valid in validation_results.items():
        status = "✅ Valid" if is_valid else "❌ Invalid/Missing"
        print(f"{provider.capitalize():12} {status}")
    
    valid_count = sum(validation_results.values())
    total_count = len(validation_results)
    
    print(f"\nValid providers: {valid_count}/{total_count}")
    
    if valid_count == 0:
        print("\n⚠️  No valid API keys found. Please set your environment variables:")
        print("   export OPENAI_API_KEY='your-key-here'")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        print("   export GEMINI_API_KEY='your-key-here'")
        print("   export GROK_API_KEY='your-key-here'")
    
    return validation_results