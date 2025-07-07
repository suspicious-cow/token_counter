# Token Counter - LLM Comparison Tool

A modular Python system for comparing token usage and outputs across multiple Large Language Model (LLM) providers: OpenAI, Google Gemini, Anthropic Claude, and xAI Grok.

**Focus**: This tool analyzes **text-based inputs and outputs only**. It does not handle multimodal features like image processing, vision capabilities, or audio generation.

## Features

- **Multi-Provider Support**: OpenAI GPT-4, Google Gemini, Anthropic Claude, and xAI Grok (text generation only)
- **Official Token Counts**: Uses each provider's official API token counts (not estimates)
- **Cost Calculations**: Detailed cost breakdown using current pricing for each provider
- **Text-Only Analysis**: Focused on text input/output token analysis and cost comparisons
- **Centralized Configuration**: Easy prompt and model customization in `config.py`
- **CSV Export**: Raw data output for analysis and visualization
- **Experiment Summaries**: Comprehensive reports with cost analysis and failed call tracking
- **Modular Architecture**: Separate client modules for each provider
- **Error Handling**: Robust error handling and reporting

## Installation

1. Clone or download this repository

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up API keys as environment variables:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export GEMINI_API_KEY="your-gemini-api-key"
export GROK_API_KEY="your-grok-api-key"
```

## Usage

### Quick Start (Use defaults from config.py)

```bash
python main.py
```

### Custom Prompts and Settings

```bash
# Custom user prompt
python main.py --prompt "Explain quantum computing in one sentence"

# Custom number of trials
python main.py --trials 5

# Custom output file
python main.py --output "my_results.csv"

# Multiple options
python main.py --prompt "Hello world" --system "Be concise" --trials 1

# Show help
python main.py --help
```

### Run for Specific Vendors Only

You can run experiments for just one or more vendors using the `--vendors` argument (comma-separated):

```bash
# Only Gemini, 20 runs
python main.py --vendors gemini --trials 20

# Only OpenAI and Grok
python main.py --vendors openai,grok --trials 5
```

If you don't specify `--vendors`, all providers are used by default.

### Configuration

Edit `config.py` to customize:

- Default prompts
- Model selections
- Number of trials
- Output settings

## File Structure

```text
├── config.py              # Centralized configuration and pricing info
├── main.py                # Main execution script with CLI arguments
├── openai_client.py       # OpenAI API client
├── gemini_client.py       # Google Gemini API client
├── anthropic_client.py    # Anthropic Claude API client
├── grok_client.py         # xAI Grok API client
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── outputs/              # Generated experiment results
    ├── api_raw_*.csv          # Raw data with token counts and costs
    ├── experiment_summary_*.txt # Statistical summaries
    └── *_failed.log           # Failed API call details (if any)
```

## Cost Calculations

The system calculates costs for each API call using current pricing information stored in `config.py`:

### Current Pricing (USD per 1M tokens)

| Provider | Model | Input Cost | Cached Input Cost | Output Cost |
|----------|-------|------------|-------------------|-------------|
| OpenAI | gpt-4.1 | $2.00 | $0.50 | $8.00 |
| Gemini | gemini-2.5-flash | $0.30 | $0.075 | $2.50 |
| Anthropic | claude-sonnet-4-20250514 | $3.00 | $0.30 | $15.00 |
| Grok | grok-3 | $3.00 | $0.75 | $15.00 |

> **Note:** All model names and pricing are maintained in `config.py` under the `MODELS_INFO` dictionary. This is the single source of truth for model selection and cost calculations. If providers update their pricing, update `MODELS_INFO` accordingly.

### Gemini 2.5 Flash: Controllable Reasoning

Gemini 2.5 Flash supports controllable reasoning through the "thinking budget" parameter:

- **thinking_budget = 0**: Disables internal reasoning (behaves like non-reasoning models such as GPT-4.1)
- **thinking_budget > 0**: Enables internal reasoning with specified token limit (up to 24,576 tokens)

Configure this in `config.py`:

```python
GEMINI_THINKING_BUDGET = 0  # Disable reasoning for faster, cheaper responses
# OR
GEMINI_THINKING_BUDGET = 1000  # Enable reasoning with 1000 token budget
```

This allows you to balance between:

- **Speed & Cost**: Lower thinking budgets for simple tasks
- **Quality & Reasoning**: Higher thinking budgets for complex problems

### Cost Calculation Details

- **OpenAI**: Supports input token caching with 75% discount on cached tokens
- **Gemini**: Supports context caching with 75% discount on cached tokens (both implicit and explicit caching)
- **Anthropic**: Supports prompt caching with 90% discount on cached tokens (cache reads)
- **Grok**: Supports prompt caching with 75% discount on cached tokens
- **All costs** are calculated per API call and aggregated in the experiment summary

### Gemini Context Caching

Gemini 2.5 Flash supports context caching with significant cost savings:

- **Cache Discount**: 75% off regular input token pricing
- **Minimum Threshold**: 1,024 tokens for Gemini 2.5 Flash
- **Cache Types**:
  - **Implicit**: Automatic caching for similar prompts within short timeframes
  - **Explicit**: Manual caching via API for large documents/media
- **TTL**: Default 1 hour (customizable)

### Anthropic Prompt Caching

Anthropic's Claude models support prompt caching with the highest discount rates:

- **Cache Discount**: 90% off regular input token pricing for cache reads
- **Cache Charges**: 25% premium for initial cache writes (not tracked separately in this tool)
- **Minimum Threshold**: 1,024 tokens for Claude Sonnet models
- **Cache Expiration**: ~5 minutes after last access
- **API Fields**: 
  - `cache_creation_input_tokens`: Tokens written to cache
  - `cache_read_input_tokens`: Tokens read from cache (90% discount)
  - `input_tokens`: Regular uncached tokens (full price)

**Note**: This tool combines `cache_creation_input_tokens` and `cache_read_input_tokens` into "Cached Input Tokens" for consistency with other providers.

### Grok Prompt Caching

xAI's Grok models support prompt caching similar to OpenAI:

- **Cache Discount**: 75% off regular input token pricing
- **API Fields**:
  - `prompt_tokens`: Total input tokens
  - `prompt_tokens_details.cached_tokens`: Tokens served from cache (75% discount)
  - `completion_tokens`: Output tokens (no caching)
- **Cache Behavior**: Automatic caching for repeated prompt prefixes
- **Context Window**: 1M tokens for Grok 3

**Important Note**: Unlike OpenAI and Anthropic (which only cache prompts of 1024+ tokens), Grok has no documented minimum threshold for caching. In practice, Grok may cache and discount even very short prompts (as few as 1–2 tokens), especially if they match common phrases or substrings. This is expected behavior and not a bug in this tool.

**Note**: Grok's caching follows OpenAI's pattern with cached tokens being a subset of total prompt tokens.

## Token Counting Implementation

### ✅ Official API Token Counts (Text Only)

All clients use official token counts from each provider's API response for **text-based interactions only**:

- **OpenAI**: `response.usage.prompt_tokens` / `response.usage.completion_tokens` + caching details
- **Anthropic**: `message.usage.input_tokens` / `message.usage.output_tokens` + caching details
- **Gemini**: `response.usage_metadata.prompt_token_count` / `response.usage_metadata.candidates_token_count` + caching details
- **Grok**: `completion.usage.prompt_tokens` / `completion.usage.completion_tokens` + caching details

**Note**: This tool does not analyze multimodal features (images, audio, vision) - only text input and text output token usage.

### 🔍 Important: LLM Text Output Format Differences

**Critical Discovery**: Different LLMs format their text outputs differently, which affects token counts:

- **OpenAI/Grok**: Return clean text (e.g., `"hello"` = 1 token)
- **Gemini**: Includes newline characters (e.g., `"hello\n"` = 2 tokens)
- **Anthropic**: May include additional formatting tokens

**Example from actual test results (text-only):**

```text
Prompt: "Give me the word 'hello' without any punctuation or any other characters"

Results:
- OpenAI:    "hello"     (1 output token)
- Gemini:    "hello\n"   (2 output tokens) ← includes newline
- Anthropic: "hello"     (4 output tokens) ← additional processing tokens
- Grok:      "hello"     (1 output token)
```

**Why This Matters:**

1. Token count differences between providers are **legitimate behavioral differences**
2. Gemini's extra tokens come from actual newline characters in the response
3. The system preserves these differences for accurate analysis
4. CSV display may show newlines as formatting artifacts, but the data is correct

## OpenAI Input Token Caching and Cost Calculation

OpenAI's API provides a unique feature: **input token caching**. When a prompt prefix (≥ 1,024 tokens) has been processed very recently, those tokens are fetched from an internal cache and billed at a discounted rate (typically 50% of the normal input price for GPT-4o). This is reflected in the API response:

```jsonc
"usage": {
  "prompt_tokens": 2006,                // total input tokens (cached + uncached)
  "completion_tokens": 300,             // output tokens
  "prompt_tokens_details": {
      "cached_tokens": 1920,            // these came from the prompt cache
      // ...
  }
}
```

### How to Calculate OpenAI API Cost (with Caching)

Suppose:

- `prompt_tokens = 2006`
- `cached_tokens = 1920`
- `completion_tokens = 300`
- `input_cost_per_million = $2.50`
- `cached_input_cost_per_million = $1.25`
- `output_cost_per_million = $10.00`

Then:

- `uncached_input = 2006 - 1920 = 86`
- `cached_input = 1920`
- `output_tokens = 300`
- `total_cost = (86 * 2.50 + 1920 * 1.25 + 300 * 10.00) / 1_000_000 = $0.0031`

**Note:**

- Never subtract cached tokens from prompt tokens for cost after already splitting them out; each bucket is billed at its own rate.
- This logic is implemented in the codebase for every OpenAI call.

For more details, see [OpenAI Pricing](https://openai.com/pricing) and [community discussion](https://community.openai.com/t/how-to-get-the-cost-for-each-api-call/1227787).

## Output Format

Results are saved to timestamped CSV files in the `outputs/` folder with columns:

- `Run Number`: Trial identifier
- `Vendor`: LLM provider (OpenAI, Gemini, Anthropic, Grok)
- `Model`: Specific model used
- `User Prompt`: The input prompt
- `System Prompt`: System instructions (if any)
- `Output`: Actual LLM response (preserved exactly as returned)
- `Input Tokens`: Tokens used for input
- `Cached Input Tokens`: Input tokens served from cache (OpenAI only)
- `Output Tokens`: Tokens generated in response
- `Input Token Cost (USD)`: Cost for uncached input tokens
- `Cached Token Cost (USD)`: Cost for cached input tokens (OpenAI only)
- `Output Token Cost (USD)`: Cost for output tokens
- `Cost (USD)`: Total cost for the API call

## Experiment Summary

Each experiment generates multiple output files:

1. **Raw Data CSV**: `api_raw_YYYYMMDD_HHMMSS_TZ.csv` - Complete detailed results
2. **Experiment Summary**: `experiment_summary_YYYYMMDD_HHMMSS_TZ.txt` - Statistical overview
3. **Failed Calls Log**: `api_raw_YYYYMMDD_HHMMSS_TZ_failed.log` - Details of any failed API calls

### Sample Experiment Summary

```text
==================================================
EXPERIMENT SUMMARY
==================================================
Total API calls: 8
Successful calls: 8
Failed calls: 0

No failed calls by vendor.

Token usage by vendor:
          Input Tokens     Cached Input Tokens     Output Tokens       Cost (USD)
                  mean sum                mean sum          mean   sum       mean       sum
Vendor
Anthropic         24.0  48                 0.0   0           4.0     8   0.000132  0.000264
Gemini            16.0  32                 0.0   0           2.0     4   0.000008  0.000016
Grok              22.0  44                 0.0   0           1.0     2   0.000000  0.000000
OpenAI            23.0  46                 0.0   0           1.0     2   0.000068  0.000136

Sample outputs (first trial):
  OpenAI: Hello
  Gemini: hello
  Anthropic: hello
  Grok: hello
```

## Customization

### Changing Prompts

Edit `config.py`:

```python
DEFAULT_USER_PROMPT = "Your custom prompt here"
DEFAULT_SYSTEM_PROMPT = "Your system instructions"
```

### Changing Models

Edit `config.py` and update the model names in `MODELS_INFO`:

```python
MODELS_INFO = {
    "openai": {
        "model": "gpt-4.1",  # Change this to the desired OpenAI model
        # ... pricing info
    },
    "gemini": {
        "model": "gemini-2.5-flash",  # Change this to the desired Gemini model
        # ... pricing info
    }
    # ... etc
}
```

### Number of Trials

Edit `config.py`:

```python
DEFAULT_NUM_TRIALS = 5  # Run 5 trials instead of 3
```

## API Rate Limits

Be aware of rate limits for each provider:

- **OpenAI**: Varies by plan and model
- **Anthropic**: Based on usage tier
- **Gemini**: Free tier has limited requests per minute
- **Grok**: Varies by subscription level

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure environment variables are set correctly
2. **Rate Limiting**: Reduce `DEFAULT_NUM_TRIALS` or add delays
3. **Model Availability**: Some models may require specific API access levels
4. **CSV Display**: Newline characters may appear as formatting artifacts in viewers
5. **Failed API Calls**: Check the generated `*_failed.log` file in `outputs/` for detailed error information
6. **Cost Calculations**: Pricing in `config.py` may need manual updates as providers change their rates

### Output Files

All experiment results are saved to timestamped files in the `outputs/` folder:

- Raw data CSV files for analysis
- Human-readable experiment summaries
- Failed call logs for troubleshooting

### Debug Mode

Create custom debug scripts as needed to inspect raw API responses:

```bash
python -c "from openai_client import process_with_openai; print(process_with_openai('test', ''))"
```

## Contributing

When modifying the code:

1. Maintain the modular structure
2. Preserve official token counting methods
3. Handle errors gracefully
4. Update this README with significant changes

## License

This project is for educational and research purposes. Please respect each API provider's terms of service.

---

**Note**: This tool captures genuine differences in how LLMs format their text outputs. Token count variations between providers reflect real behavioral differences in text generation, not measurement errors. Multimodal features (images, audio, vision) are not analyzed by this tool.
