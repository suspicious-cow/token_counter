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

2. **Set up API keys** using a `.env` file (recommended) or environment variables:

   **Option A: Using .env file (Recommended for project isolation)**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env file with your actual API keys
   # The .env file is automatically ignored by git
   ```

   **Option B: Using environment variables**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   export GEMINI_API_KEY="your-gemini-api-key"
   export GROK_API_KEY="your-grok-api-key"
   ```

### API Key Configuration Details

#### .env File Setup (Recommended)

The `.env` file approach is recommended for:
- **Project isolation** - Keys are specific to this project
- **Billing validation** - Easier to track usage with dedicated keys
- **Security** - File is automatically ignored by git
- **Convenience** - No need to set environment variables each time

**⏰ Billing Data Timing**: Usage and cost data typically appears in provider billing dashboards 24-48 hours after API calls. Use dedicated API keys in your `.env` file for cleaner validation tracking.

**Setup steps:**
1. Copy `.env.example` to `.env`: `cp .env.example .env`
2. Edit `.env` with your actual API keys
3. The application will automatically load keys from `.env` first
4. Falls back to system environment variables if `.env` not found

**Example .env file:**
```bash
OPENAI_API_KEY=sk-proj-abc123...
ANTHROPIC_API_KEY=sk-ant-api03-xyz789...
GEMINI_API_KEY=AIzaSyABC123...
GROK_API_KEY=xai-def456...
```

#### Key Priority Order
1. **`.env` file** (highest priority)
2. **System environment variables** (fallback)
3. **Default placeholder** (will cause errors)

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

```
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

## 🧠 Reasoning Model Handling

This system is configured to avoid reasoning tokens that could skew token count comparisons:

### Model Selection

**Note**: All effort was made to use non-reasoning models for accurate cost comparison. However, Grok-4 does not provide an option to disable internal reasoning.

- **OpenAI**: `gpt-4.1` (non-reasoning model)
- **Gemini**: `gemini-2.5-pro` (non-reasoning model with tiered pricing)
- **Anthropic**: `claude-sonnet-4-20250514` (non-reasoning model)
- **Grok**: `grok-4` (reasoning model - **reasoning cannot be disabled**)

### Reasoning Configuration

- **OpenAI**: Uses gpt-4.1 (non-reasoning model)
- **Gemini**: Uses gemini-2.5-pro (non-reasoning model)
- **Anthropic**: Uses claude-sonnet-4 (non-reasoning model)
- **Grok**: Uses grok-4 (reasoning model)
  - **Limitation**: Internal reasoning cannot be disabled via API
  - **Impact**: Costs include hidden reasoning tokens (5-10x multiplier)
  - **Billing**: Reasoning tokens appear in xAI console but not in API responses

This ensures fair token count comparisons without hidden reasoning overhead that could affect cost analysis.

## 💰 Pricing Configuration

### Centralized Pricing Management

All pricing is configured in `config.py` under the `MODELS_INFO` dictionary - **not in individual client files**. This provides:

- **Single source of truth** for all provider pricing
- **Easy maintenance** - update prices in one location
- **Consistent cost calculations** across all experiments

### Current Pricing (USD per 1M tokens)

_Last updated: January 2025_

| Provider  | Model                      | Input | Cached Input     | Output |
| --------- | -------------------------- | ----- | ---------------- | ------ |
| OpenAI    | gpt-4.1                    | $2.00 | $1.00 (50% off)  | $8.00 |
| Gemini    | gemini-2.5-pro             | $1.25/$2.50* | $0.31/$0.63* (75% off) | $10.00/$15.00* |
| Anthropic | claude-sonnet-4-20250514   | $3.00 | $0.30/$3.75/$6.00** | $15.00 |
| Grok      | grok-4                     | $3.00/$6.00*** | $0.75/$1.50*** (75% off) | $15.00/$30.00*** |

*Gemini uses tiered pricing: lower rates for ≤200K tokens, higher rates for >200K tokens
**Anthropic cache pricing: $0.30 cache reads, $3.75 ephemeral writes (5min), $6.00 persistent writes (1hr)
***Grok uses higher context pricing AND hidden reasoning tokens: actual costs can be 5-10x higher than calculated

### Caching Details by Provider

#### OpenAI (gpt-4.1)

- **Base Pricing**: $2.00 input, $1.00 cached input (50% off), $8.00 output per 1M tokens
- **Caching**: 50% off cached input tokens (≥1024 tokens, automatic)
- **Type**: Automatic prompt caching for repeated prefixes
- **Management**: No explicit cache control needed

**Web Search Tool Calls:**
- **Cost**: $25.00 per 1,000 calls (for gpt-4.1 and gpt-4.1-mini models)
- **Search content tokens**: Included in the $25/1K calls cost (not charged separately)
- **Billing**: Appears as 'web search tool calls | gpt-4o' in dashboard

**⚠️ Important Web Search Billing Behavior:**
- **Hidden sub-searches**: Each web search tool call can trigger multiple internal sub-searches
- **Billing per sub-search**: You're charged for each internal sub-search, not just the visible call
- **Unpredictable costs**: One tool call might generate 2-5+ billable sub-searches behind the scenes
- **Dashboard limitation**: Usage dashboard only shows tool invocations, not internal sub-searches
- **Cost impact**: Actual costs can be 2-3x higher than expected based on visible tool calls

**Example**: 57 visible web search calls → 147 actual billable sub-searches (2.6x multiplier)

**Note**: Only applies when using built-in web search tools, not standard API calls

#### Gemini (gemini-2.5-pro)

- **Tiered Pricing**: Different rates based on total token usage per request
  - **≤200K tokens**: $1.25 input, $10.00 output (per 1M tokens)
  - **>200K tokens**: $2.50 input, $15.00 output (per 1M tokens)
- **Caching**: Token counts displayed when available, but pricing unknown
  - Google has not yet documented caching rates for Gemini 2.5 Pro
  - Full input token price charged (no caching discount applied)
  - Cached token costs shown as $0.00 (unknown pricing)
- **Management**: Automatic tier detection based on total tokens per request

#### Anthropic (claude-sonnet-4-20250514)

- **Base Input**: $3.00 per 1M tokens for regular (non-cached) input
- **Cache Types**: Configurable via `ANTHROPIC_CACHE_TYPE` setting
  - **Ephemeral** (~5 min TTL): $3.75 per 1M cache writes (25% markup)
  - **Persistent** (~1 hour TTL): $6.00 per 1M cache writes (100% markup)
- **Cache Reads**: $0.30 per 1M tokens for both cache types (90% discount)
- **Output**: $15.00 per 1M tokens (standard rate)
- **Configuration**: Set `ANTHROPIC_CACHE_TYPE = "ephemeral"` or `"persistent"` in config.py
- **Minimum**: 1024+ tokens required for caching
- **Type**: Explicit prompt caching with cache control blocks
- **Cost Calculation**: Automatically uses correct pricing based on configured cache type

#### Grok (grok-4)

- **Higher Context Pricing**: Different rates based on total context size
  - **≤128K tokens**: $3.00 input, $0.75 cached, $15.00 output (per 1M tokens)
  - **>128K tokens**: $6.00 input, $1.50 cached, $30.00 output (per 1M tokens)
- **Context Calculation**: Based on total input + output tokens per request
- **Caching**: 75% discount on cached input tokens (applied to appropriate tier rate)
- **Type**: Automatic prompt caching (OpenAI-compatible)

**⚠️ Critical Grok-4 Billing Behavior:**
- **Hidden reasoning tokens**: Grok-4 uses internal reasoning that dramatically increases costs
- **Token multiplier**: Reasoning tokens can be 3-5x the visible prompt/completion tokens
- **Billing transparency**: xAI console shows breakdown, but API doesn't report reasoning tokens
- **Cost unpredictability**: Actual costs can be 10-50x higher than calculated from visible tokens
- **No control**: Internal reasoning appears to be always active (cannot be disabled)

**Example**: 22 visible tokens → 185 actual billable tokens (8.4x multiplier due to 141 reasoning tokens)

**Management**: Automatic tier detection, but reasoning tokens make cost prediction impossible

### Updating Pricing

To update pricing when providers change rates:

1. **Edit `config.py`**:

   ```python
   MODELS_INFO = {
       "openai": {
           "input_cost_per_million": 2.50,    # Update this value
           "cached_input_cost_per_million": 1.25,  # Update this value
           "output_cost_per_million": 10.00   # Update this value
       },
       # ... other providers
   }
   ```

2. **Update the "Last updated" comment** in `config.py`

3. **No client code changes needed** - pricing is automatically applied

### Cost Calculation Method

The system calculates costs using official API token counts:

```
uncached_input_cost = (total_input_tokens - cached_tokens) × input_rate
cached_input_cost = cached_tokens × cached_input_rate
output_cost = output_tokens × output_rate
total_cost = uncached_input_cost + cached_input_cost + output_cost
```

### Cost Verification

For manual cost verification:

1. Run controlled experiment with a specific verification prompt
2. **Wait 24-48 hours** for usage data to appear in billing dashboards
3. Check each vendor's billing dashboard manually
4. Compare token counts and costs with experiment output
5. Verify pricing configuration matches actual billing rates

**⏰ Important**: Billing data can take 1-2 days to appear in provider dashboards after API usage. Plan your validation timeline accordingly.

Check the following dashboards:

- OpenAI: https://platform.openai.com/usage
- Anthropic: https://console.anthropic.com/
- Gemini: https://console.cloud.google.com/billing
- Grok: https://console.x.ai/

## 📊 Enhanced Output Files

Each experiment now generates:

- **Raw Data CSV**: Complete results with token counts and costs
- **Analysis Report**: Statistical summary with efficiency metrics
- **Cost Comparison Charts**: Visual analysis (PNG format)
- **Failed Calls Log**: Detailed error tracking for troubleshooting

## 🏗️ Architecture Overview

### New File Structure

```
├── clients/                   # Enhanced client architecture
│   ├── base_client.py        # Abstract base client
│   ├── openai_client.py      # Enhanced OpenAI client
│   ├── gemini_client.py      # Enhanced Gemini client
│   ├── anthropic_client.py   # Enhanced Anthropic client
│   └── grok_client.py        # Enhanced Grok client
├── config/                   # Configuration management
│   └── validation.py         # API key validation utilities
├── utils/                    # Utility modules
│   ├── retry.py              # Retry logic with backoff
│   └── rate_limiter.py       # Rate limiting utilities
├── analytics/                # Advanced analytics
│   └── analyzer.py           # Comprehensive analysis tools
├── cli/                      # Interactive CLI
│   └── interactive.py        # Guided experiment setup
├── tests/                    # Test suite
│   └── test_clients.py       # Client testing
├── examples/                 # Demo and example scripts
│   └── demo.py               # Feature demonstration
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
