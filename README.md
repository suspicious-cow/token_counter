# Token Counter - Enhanced LLM Comparison Tool

A system for comparing token usage, costs, and outputs across multiple Large Language Model (LLM) providers with analytics and monitoring capabilities.

## 🚀 New Enhanced Features

### Architecture Improvements

- **Modular Client Architecture**: Base client with standardized interfaces
- **Client Factory Pattern**: Centralized client management and validation
- **Enhanced Error Handling**: Retry logic with exponential backoff
- **Rate Limiting**: Rate limiting to prevent API throttling
- **Analytics**: Cost analysis and visualization

### Enhanced User Experience

- **Interactive CLI Mode**: Guided experiment setup
- **Rich Console Output**: Terminal interface with progress indicators
- **Reporting**: Analysis with charts and statistics
- **API Key Validation**: Automatic validation and status reporting

### Advanced Analytics

- **Cost Comparison Charts**: Visual cost analysis across providers
- **Token Efficiency Analysis**: Output tokens per dollar calculations
- **Outlier Detection**: Identify unusual responses or costs
- **Success Rate Tracking**: Monitor API reliability by provider

## 🚀 How to Use the System

### Prerequisites

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API keys** as environment variables:

   ```bash
   
   export OPENAI_API_KEY="your-openai-api-key"
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   export GEMINI_API_KEY="your-gemini-api-key"
   export GROK_API_KEY="your-grok-api-key"
   ```

### Usage Methods

#### 1. Interactive Mode (Recommended for Beginners)

```bash
python cli/interactive.py
```

**What it does**: Guides you through experiment setup, validates API keys, and allows provider selection.

#### 2. Command Line Interface

```bash
python main.py [OPTIONS]
```

### 📋 Command Line Parameters

#### Core Parameters

| Parameter  | Short | Type    | Default                      | Description                            |
| ---------- | ----- | ------- | ---------------------------- | -------------------------------------- |
| `--prompt` | `-p`  | string  | "Give me the word 'halt'..." | The user prompt to send to all LLMs    |
| `--system` | `-s`  | string  | ""                           | System instructions for the LLMs       |
| `--trials` | `-t`  | integer | 3                            | Number of times to run each experiment |
| `--output` | `-o`  | string  | auto-generated               | Output CSV filename                    |

#### Provider Selection

| Parameter   | Short | Type   | Default | Description                               |
| ----------- | ----- | ------ | ------- | ----------------------------------------- |
| `--vendors` | `-v`  | string | all     | Comma-separated list of providers to test |

**Valid providers**: `openai`, `gemini`, `anthropic`, `grok`

#### Feature Flags

| Parameter         | Type | Description                                                      |
| ----------------- | ---- | ---------------------------------------------------------------- |
| `--enhanced`      | flag | Enable advanced features (rate limiting, retry logic, analytics) |
| `--validate-only` | flag | Only validate API keys and exit (no experiments)                 |

### 📚 Detailed Usage Examples

#### Basic Usage

```bash
# Simple experiment with default settings
python main.py

# Custom prompt with 5 trials
python main.py --prompt "Explain quantum computing in one sentence" --trials 5

# Test specific providers only
python main.py --vendors openai,gemini --trials 3
```

#### Enhanced Mode (Recommended)

```bash
# Enhanced mode with all features
python main.py --enhanced --prompt "Write a haiku about AI" --trials 5

# Enhanced mode with specific providers and custom output
python main.py --enhanced --vendors openai,anthropic --trials 10 --output "ai_haiku_test.csv"

# Enhanced mode with system prompt
python main.py --enhanced --prompt "Hello" --system "Be very concise" --trials 3
```

#### Validation and Setup

```bash
# Check which API keys are properly configured
python main.py --validate-only

# Demo the features without making API calls
python examples/demo.py
```

### 🔧 Parameter Details and Examples

#### `--prompt` / `-p`

**Purpose**: The main text you want to send to all LLM providers for comparison.

```bash
# Short prompt
python main.py --prompt "Hello world"

# Complex prompt
python main.py --prompt "Write a Python function that calculates fibonacci numbers"

# Prompt with quotes
python main.py --prompt "Explain the concept of 'machine learning' to a 5-year-old"
```

#### `--system` / `-s`

**Purpose**: System-level instructions that guide the LLM's behavior and response style.

```bash
# Concise responses
python main.py --system "Be very brief and direct" --prompt "What is AI?"

# Specific format
python main.py --system "Respond only in JSON format" --prompt "List 3 colors"

# Role-playing
python main.py --system "You are a helpful coding assistant" --prompt "Fix this Python code"
```

#### `--trials` / `-t`

**Purpose**: Number of times to repeat the experiment with each provider for statistical analysis.

```bash
# Single trial (fastest)
python main.py --trials 1 --prompt "Test"

# Multiple trials for statistical significance
python main.py --trials 10 --prompt "Generate a random number"

# High trial count for research
python main.py --trials 20 --enhanced --prompt "Creative writing sample"
```

**Recommendation**: Use 3-5 trials for general testing, 10+ for research or when response variability is important.

#### `--vendors` / `-v`

**Purpose**: Select specific LLM providers to test instead of all available ones.

```bash
# Test only OpenAI and Gemini
python main.py --vendors openai,gemini

# Test only Anthropic
python main.py --vendors anthropic --trials 5

# Test all except Grok
python main.py --vendors openai,gemini,anthropic
```

**Use cases**:

- Cost control (test cheaper providers first)
- Speed (fewer providers = faster results)
- Comparison studies (specific provider comparisons)

#### `--output` / `-o`

**Purpose**: Specify custom filename for results instead of auto-generated timestamped files.

```bash
# Custom filename
python main.py --output "my_experiment.csv"

# Organized by date
python main.py --output "results/2024-01-15-test.csv"

# Descriptive naming
python main.py --output "gpt_vs_claude_coding_test.csv"
```

**Default behavior**: Auto-generates timestamped files like `api_raw_20240115_143022_CST.csv`

#### `--enhanced`

**Purpose**: Enables advanced features for production use.

**What it adds**:

- Rate limiting to prevent API throttling
- Retry logic with exponential backoff
- Analytics and visualizations
- Error handling
- Cost comparison charts
- Token efficiency analysis

```bash
# Basic enhanced mode
python main.py --enhanced

# Enhanced with custom settings
python main.py --enhanced --trials 10 --vendors openai,anthropic
```

**When to use**: Always recommended except for quick tests or when dependencies aren't available.

#### `--validate-only`

**Purpose**: Check API key configuration without running experiments.

```bash
# Check all API keys
python main.py --validate-only
```

**Output example**:

```markdown
API Key Validation Report:
------------------------------
Openai       ✅ Valid
Gemini       ✅ Valid
Anthropic    ❌ Invalid/Missing
Grok         ✅ Valid

Valid providers: 3/4
```

### 💡 Best Practices

#### For Beginners

```bash
# Start with validation
python main.py --validate-only

# Try interactive mode
python cli/interactive.py

# Simple test
python main.py --enhanced --trials 1 --prompt "Hello"
```

#### For Research/Analysis

```bash
# Comprehensive comparison
python main.py --enhanced --trials 10 --prompt "Your research prompt here"

# Cost-focused analysis
python main.py --enhanced --vendors gemini,openai --trials 5 --prompt "Efficiency test"
```

#### For Development/Testing

```bash
# Quick iteration
python main.py --trials 1 --vendors openai --prompt "Test prompt"

# Specific provider testing
python main.py --enhanced --vendors anthropic --trials 3
```

## 📊 Enhanced Output Files

Each experiment now generates:

- **Raw Data CSV**: Complete results with token counts and costs
- **Analysis Report**: Statistical summary with efficiency metrics
- **Cost Comparison Charts**: Visual analysis (PNG format)
- **Failed Calls Log**: Detailed error tracking for troubleshooting

## 🏗️ Architecture Overview

### New File Structure

```markdown
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

```markdown
Token Efficiency (Output Tokens per Dollar):
  Gemini: 83,333 tokens/$
  OpenAI: 12,500 tokens/$
  Grok: 6,667 tokens/$w
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
- **Rich Interface**: Terminal output with tables and panels
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
