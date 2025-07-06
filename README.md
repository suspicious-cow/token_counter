# Token Counter - LLM Comparison Tool

A modular Python system for comparing token usage and outputs across multiple Large Language Model (LLM) providers: OpenAI, Google Gemini, Anthropic Claude, and xAI Grok.

## Features

- **Multi-Provider Support**: OpenAI GPT-4, Google Gemini, Anthropic Claude, and xAI Grok
- **Official Token Counts**: Uses each provider's official API token counts (not estimates)
- **Centralized Configuration**: Easy prompt and model customization in `config.py`
- **CSV Export**: Raw data output for analysis and visualization
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
├── config.py              # Centralized configuration
├── main.py                # Main execution script with CLI arguments
├── openai_client.py       # OpenAI API client
├── gemini_client.py       # Google Gemini API client
├── anthropic_client.py    # Anthropic Claude API client
├── grok_client.py         # xAI Grok API client
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Token Counting Implementation

### ✅ Official API Token Counts

All clients use official token counts from each provider's API response:

- **OpenAI**: `response.usage.prompt_tokens` / `response.usage.completion_tokens`
- **Anthropic**: `message.usage.input_tokens` / `message.usage.output_tokens`
- **Gemini**: `response.usage_metadata.prompt_token_count` / `response.usage_metadata.candidates_token_count`
- **Grok**: `completion.usage.prompt_tokens` / `completion.usage.completion_tokens`

### 🔍 Important: LLM Output Format Differences

**Critical Discovery**: Different LLMs format their outputs differently, which affects token counts:

- **OpenAI/Grok**: Return clean text (e.g., `"hello"` = 1 token)
- **Gemini**: Includes newline characters (e.g., `"hello\n"` = 2 tokens)
- **Anthropic**: May include additional formatting tokens

**Example from actual test results:**

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

Results are saved to `api_results.csv` with columns:

- `Run Number`: Trial identifier
- `Vendor`: LLM provider (OpenAI, Gemini, Anthropic, Grok)
- `Model`: Specific model used
- `User Prompt`: The input prompt
- `System Prompt`: System instructions (if any)
- `Output`: Actual LLM response (preserved exactly as returned)
- `Input Tokens`: Tokens used for input
- `Output Tokens`: Tokens generated in response

## Customization

### Changing Prompts

Edit `config.py`:

```python
DEFAULT_USER_PROMPT = "Your custom prompt here"
DEFAULT_SYSTEM_PROMPT = "Your system instructions"
```

### Changing Models

Edit `config.py`:

```python
MODELS = {
    "openai": "gpt-4o",
    "gemini": "gemini-2.0-flash",
    "anthropic": "claude-3-7-sonnet-20250219",
    "grok": "grok-3-beta"
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
5. **Vendor-Specific Failures**: Check the generated log file in `outputs/` for details on failed calls by vendor.

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

**Note**: This tool captures genuine differences in how LLMs format their outputs. Token count variations between providers reflect real behavioral differences, not measurement errors.
