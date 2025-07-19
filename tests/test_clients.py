"""
Test suite for client implementations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clients.base_client import BaseLLMClient, TokenUsage, LLMResponse
from clients.openai_client import OpenAIClient
from clients.gemini_client import GeminiClient
from clients.anthropic_client import AnthropicClient
from clients.grok_client import GrokClient
from client_factory import ClientFactory


class TestBaseLLMClient:
    """Test the base client functionality"""
    
    def test_token_usage_dataclass(self):
        """Test TokenUsage dataclass"""
        usage = TokenUsage(input_tokens=100, cached_input_tokens=20, output_tokens=50)
        assert usage.input_tokens == 100
        assert usage.cached_input_tokens == 20
        assert usage.output_tokens == 50
    
    def test_llm_response_dataclass(self):
        """Test LLMResponse dataclass"""
        usage = TokenUsage(100, 20, 50)
        response = LLMResponse(
            output="Hello world",
            usage=usage,
            cost=0.001,
            model="test-model"
        )
        assert response.output == "Hello world"
        assert response.usage.input_tokens == 100
        assert response.cost == 0.001
        assert response.model == "test-model"


class TestClientFactory:
    """Test the client factory"""
    
    def test_get_available_providers(self):
        """Test getting available providers"""
        providers = ClientFactory.get_available_providers()
        expected = ['openai', 'gemini', 'anthropic', 'grok']
        assert set(providers) == set(expected)
    
    def test_get_client_valid_provider(self):
        """Test getting a valid client"""
        client = ClientFactory.get_client('openai')
        assert isinstance(client, OpenAIClient)
        
        client = ClientFactory.get_client('gemini')
        assert isinstance(client, GeminiClient)
    
    def test_get_client_invalid_provider(self):
        """Test getting an invalid client"""
        client = ClientFactory.get_client('invalid')
        assert client is None
    
    def test_validate_providers(self):
        """Test provider validation"""
        valid = ClientFactory.validate_providers(['openai', 'gemini', 'invalid'])
        assert set(valid) == {'openai', 'gemini'}
        
        valid = ClientFactory.validate_providers(['OPENAI', 'Gemini'])
        assert set(valid) == {'openai', 'gemini'}


class TestCostCalculations:
    """Test cost calculation accuracy"""
    
    @patch('config.MODELS_INFO')
    def test_cost_calculation_no_cache(self, mock_models_info):
        """Test cost calculation without caching"""
        mock_models_info.__getitem__.return_value = {
            'input_cost_per_million': 2.0,
            'cached_input_cost_per_million': 0.5,
            'output_cost_per_million': 8.0
        }
        
        # Mock client
        client = Mock(spec=BaseLLMClient)
        client.provider_name = 'test'
        client.get_model_info.return_value = mock_models_info['test']
        
        # Test calculation
        usage = TokenUsage(input_tokens=1000, cached_input_tokens=0, output_tokens=500)
        expected_cost = (1000 * 2.0 + 0 * 0.5 + 500 * 8.0) / 1_000_000
        
        # Use the actual calculation method
        from clients.base_client import BaseLLMClient
        actual_cost = BaseLLMClient.calculate_cost(client, usage)
        
        assert abs(actual_cost - expected_cost) < 1e-10
    
    @patch('config.MODELS_INFO')
    def test_cost_calculation_with_cache(self, mock_models_info):
        """Test cost calculation with caching"""
        mock_models_info.__getitem__.return_value = {
            'input_cost_per_million': 2.0,
            'cached_input_cost_per_million': 0.5,
            'output_cost_per_million': 8.0
        }
        
        client = Mock(spec=BaseLLMClient)
        client.provider_name = 'test'
        client.get_model_info.return_value = mock_models_info['test']
        
        usage = TokenUsage(input_tokens=1000, cached_input_tokens=200, output_tokens=500)
        # Uncached: 800, Cached: 200, Output: 500
        expected_cost = (800 * 2.0 + 200 * 0.5 + 500 * 8.0) / 1_000_000
        
        from clients.base_client import BaseLLMClient
        actual_cost = BaseLLMClient.calculate_cost(client, usage)
        
        assert abs(actual_cost - expected_cost) < 1e-10


class TestErrorHandling:
    """Test error handling across clients"""
    
    @patch('clients.openai_client.OpenAI')
    def test_openai_client_error_handling(self, mock_openai):
        """Test OpenAI client error handling"""
        # Mock API to raise an exception
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        client = OpenAIClient()
        response = client.process("test prompt")
        
        assert response.output.startswith("Error:")
        assert response.usage.input_tokens == 0
        assert response.cost == 0.0


if __name__ == "__main__":
    pytest.main([__file__])