# Token Counter - Enhanced LLM Comparison Tool

A comprehensive, production-ready Python system for comparing token usage, costs, and outputs across multiple Large Language Model (LLM) providers with advanced analytics and monitoring capabilities.

## 🚀 New Enhanced Features

### Architecture Improvements

- **Modular Client Architecture**: Clean base client with standardized interfaces
- **Client Factory Pattern**: Centralized client management and validation
- **Enhanced Error Handling**: Retry logic with exponential backoff
- **Rate Limiting**: Intelligent rate limiting to prevent API throttling
- **Comprehensive Analytics**: Advanced cost analysis and visualization

### Enhanced User Experience

- **Interactive CLI Mode**: Guided experiment setup
- **Rich Console Output**: Beautiful terminal interface with progress indicators
- **Comprehensive Reporting**: Detailed analysis with charts and statistics
- **API Key Validation**: Automatic validation and status reporting

### Advanced Analytics

- **Cost Comparison Charts**: Visual cost analysis across providers
- **Token Efficiency Analysis**: Output tokens per dollar calculations
- **Outlier Detection**: Identify unusual responses or costs
- **Success Rate Tracking**: Monitor API reliability by provider

## 🎯 Quick Start

### Enhanced Mode (Recommended)

```bash
# Interactive mode with guided setup
python cli/interactive.py

# Enhanced CLI with all features
python main.py --enhanced --prompt "Explain AI" --trials 5

# Validate API keys
python main.py --validate-only

# Custom experiment with analytics
python main.py --enhanced --prompt "Explain AI" --trials 5 --vendors openai,gemini
```

### Classic Mode (Backward Compatible)

```bash
# Original functionality preserved
python main.py --prompt "Hello world" --trials 3
```

## 📊 Enhanced Output Files

Each experiment now generates:

- **Raw Data CSV**: Complete results with token counts and costs
- **Comprehensive Analysis**: Statistical summary with efficiency metrics
- **Cost Comparison Charts**: Visual analysis (PNG format)
- **Failed Calls Log**: Detailed error tracking for troubleshooting

## 🏗️ Architecture Overview

### New File Structure

```
├── clients/                    # Enhanced client architecture
│   ├── base_client.py         # Abstract base client
│   ├── openai_client.py       # Enhanced OpenAI client
│   ├── gemini_client.py       # Enhanced Gemini client
│   ├── anthropic_client.py    # Enhanced Anthropic client
│   └── grok_client.py         # Enhanced Grok client
├── config/                    # Configuration management
│   └── validation.py          # API key validation utilities
├── utils/                     # Utility modules
│   ├── retry.py              # Retry logic with backoff
│   └── rate_limiter.py       # Rate limiting utilities
├── analytics/                 # Advanced analytics
│   └── analyzer.py           # Comprehensive analysis tools
├── cli/                      # Interactive CLI
│   └── interactive.py        # Guided experiment setup
├── tests/                    # Test suite
│   └── test_clients.py       # Client testing
├── examples/                  # Demo and example scripts
│   └── demo.py              # Feature demonstration
├── client_factory.py         # Client factory pattern
├── main.py                   # Main script (classic + enhanced modes)
└── [other files...]          # Configuration, requirements, etc.
```

### Client Architecture

All clients now inherit from `BaseLLMClient` providing:

- Standardized response format (`LLMResponse` dataclass)
- Consistent error handling
- Unified cost calculations
- Token usage tracking (`TokenUsage` dataclass)

```python
from client_factory import ClientFactory

# Get any client
client = ClientFactory.get_client('openai')
response = client.process("Hello world")

print(f"Output: {response.output}")
print(f"Cost: ${response.cost}")
print(f"Tokens: {response.usage.input_tokens} in, {response.usage.output_tokens} out")
```

## 🔧 Enhanced Configuration

### API Key Validation

```python
from config.validation import validate_api_keys, print_validation_report

# Check all API keys
validation_results = validate_api_keys()
print_validation_report()
```

### Rate Limiting Configuration

```python
from utils.rate_limiter import RateLimiter

# Custom rate limits
limiter = RateLimiter({
    'openai': 0.1,    # 10 calls/second
    'gemini': 1.0,    # 1 call/second
})
```

## 📈 Advanced Analytics

### Comprehensive Analysis

```python
from analytics.analyzer import ExperimentAnalyzer

analyzer = ExperimentAnalyzer(results_df)

# Generate cost comparison charts
analyzer.generate_cost_comparison_chart()

# Calculate token efficiency
efficiency = analyzer.generate_token_efficiency_report()

# Detect outliers
outliers = analyzer.detect_outliers()

# Generate full report
analyzer.generate_comprehensive_report()
```

### Sample Analytics Output

```
Token Efficiency (Output Tokens per Dollar):
  Gemini: 83,333 tokens/$
  OpenAI: 12,500 tokens/$
  Grok: 6,667 tokens/$
  Anthropic: 3,333 tokens/$

Outlier Detection:
  High cost outliers: 2
  High token outliers: 1
  Unusual responses: 0
```

## 🧪 Testing

### Run Test Suite

```bash
# Install test dependencies
pip install pytest

# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_clients.py -v
```

### Test Coverage

- Client architecture validation
- Cost calculation accuracy
- Error handling scenarios
- Provider validation
- Token counting precision

## 🚦 Error Handling & Resilience

### Retry Logic

- Exponential backoff with jitter
- Configurable retry attempts
- Smart error classification

### Rate Limiting

- Provider-specific limits
- Automatic throttling
- Configurable intervals

### Comprehensive Error Reporting

- Detailed failed call logs
- Success rate tracking by provider
- Error categorization and analysis

## 🎨 Interactive Mode Features

The new interactive CLI provides:

- **Guided Setup**: Step-by-step experiment configuration
- **API Key Validation**: Real-time status checking
- **Provider Selection**: Choose from available providers
- **Rich Interface**: Beautiful terminal output with tables and panels
- **Confirmation Steps**: Review before execution

```bash
python cli/interactive.py
```

## 📊 Enhanced Reporting

### Experiment Summary

- Success rates by provider
- Cost analysis with statistics
- Token efficiency rankings
- Outlier identification

### Visual Analytics

- Cost distribution box plots
- Token usage comparisons
- Efficiency bar charts
- Success rate visualizations

## 🔄 Backward Compatibility

All original functionality is preserved:

- Original `main.py` works unchanged
- All client functions maintain same signatures
- Existing scripts continue to work
- Configuration remains compatible

## 🚀 Performance Improvements

### Concurrent Processing

- Rate-limited concurrent API calls
- Intelligent request batching
- Optimized retry strategies

### Memory Efficiency

- Streaming result processing
- Efficient data structures
- Minimal memory footprint

## 🛠️ Development Features

### Extensibility

- Easy to add new providers
- Plugin architecture ready
- Configurable components

### Monitoring

- Comprehensive logging
- Performance metrics
- Error tracking

### Testing

- Unit test coverage
- Integration tests
- Mock API responses

## 📋 Migration Guide

### From Original to Enhanced

1. **Install new dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Try enhanced mode**:

   ```bash
   python main.py --validate-only
   ```

3. **Use interactive mode**:

   ```bash
   python cli/interactive.py
   ```

4. **Existing scripts work unchanged** - no migration required!

## 🤝 Contributing

The enhanced architecture makes contributions easier:

- Clear separation of concerns
- Comprehensive test suite
- Standardized interfaces
- Detailed documentation

## 📄 License

This project is for educational and research purposes. Please respect each API provider's terms of service.

---

**Enhanced Token Counter** - Production-ready LLM comparison with advanced analytics and monitoring capabilities.
