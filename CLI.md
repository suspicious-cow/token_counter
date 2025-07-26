# Token Counter CLI Documentation

Complete command-line interface reference for the LLM Token Counter tool.

## Quick Start

```bash
# Run with defaults (all providers, 3 trials)
python main.py

# Custom prompt with specific providers
python main.py --prompt "Your test prompt" --vendors openai,gemini --trials 5
```

## Command Syntax

```bash
python main.py [OPTIONS]
```

## Options Reference

### Core Parameters

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--prompt` | `-p` | string | "Give me the word 'halt'..." | User prompt to send to all models |
| `--system` | `-s` | string | "" (empty) | System prompt for models that support it |
| `--trials` | `-t` | integer | 3 | Number of trials to run per provider |
| `--output` | `-o` | string | auto-generated | Output CSV filename |
| `--vendors` | `-v` | string | "all" | Comma-separated list of providers |

### Valid Providers

| Provider | Model | Description |
|----------|-------|-------------|
| `openai` | gpt-4o | OpenAI GPT-4o with caching |
| `gemini` | gemini-2.5-pro | Google Gemini 2.5 Pro with tiered pricing |
| `anthropic` | claude-sonnet-4-20250514 | Anthropic Claude Sonnet 4 with configurable caching |
| `grok` | grok-2 | xAI Grok-2 with higher context pricing |

## Usage Examples

### Basic Usage

```bash
# Default run (all providers, 3 trials each)
python main.py

# Simple custom prompt
python main.py --prompt "Explain quantum computing in one sentence"

# Custom system prompt
python main.py --system "You are a helpful assistant" --prompt "Hello"
```

### Provider Selection

```bash
# Single provider
python main.py --vendors openai
python main.py --vendors gemini
python main.py --vendors anthropic
python main.py --vendors grok

# Multiple providers
python main.py --vendors openai,gemini
python main.py --vendors anthropic,grok
python main.py --vendors openai,gemini,anthropic

# All providers (explicit)
python main.py --vendors openai,gemini,anthropic,grok
```

### Trial Configuration

```bash
# Single trial for quick testing
python main.py --trials 1

# More trials for statistical significance
python main.py --trials 10

# Single trial with specific provider
python main.py --vendors gemini --trials 1
```

### Output Control

```bash
# Custom output filename
python main.py --output my_experiment.csv

# Timestamped output (default behavior)
python main.py  # Creates: outputs/api_raw_YYYYMMDD_HHMMSS_mmm_TZ.csv
```

### Complex Examples

```bash
# Cost comparison between OpenAI and Claude
python main.py --vendors openai,anthropic --trials 5 --prompt "Write a haiku about AI"

# Gemini tiered pricing test with long prompt
python main.py --vendors gemini --trials 1 --prompt "$(cat long_document.txt)"

# Quick single-provider test
python main.py --vendors grok --trials 1 --prompt "Test" --output grok_test.csv

# System prompt comparison
python main.py --system "Be concise" --prompt "Explain machine learning" --trials 3
```

## Output Files

### Generated Files

The tool generates several output files in the `outputs/` directory:

1. **Raw Data CSV**: `api_raw_YYYYMMDD_HHMMSS_mmm_TZ.csv`
   - Complete results with token counts and costs
   - One row per API call

2. **Summary Report**: `experiment_summary_YYYYMMDD_HHMMSS_mmm_TZ.txt`
   - Cost analysis and efficiency metrics
   - Failed call logs

3. **Failed Calls Log**: `api_raw_YYYYMMDD_HHMMSS_mmm_TZ_failed.log`
   - Detailed error information for debugging

### CSV Columns

| Column | Description |
|--------|-------------|
| Run Number | Trial number (1, 2, 3, etc.) |
| Vendor | Provider name (OpenAI, Gemini, etc.) |
| Model | Specific model used |
| User Prompt | The prompt sent to the model |
| System Prompt | System prompt (if any) |
| Output | Model's response |
| Input Tokens | Total input tokens |
| Cached Input Tokens | Tokens retrieved from cache |
| Output Tokens | Generated output tokens |
| Input Token Cost (USD) | Cost for regular input tokens |
| Cached Token Cost (USD) | Cost for cached tokens |
| Output Token Cost (USD) | Cost for output tokens |
| Cost (USD) | Total cost for this call |

## Advanced Usage

### Environment Variables

Set API keys via environment variables:

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GEMINI_API_KEY="your-gemini-key"
export GROK_API_KEY="your-grok-key"

# Then run normally
python main.py
```

### Configuration

Modify `config.py` for advanced settings:

```python
# Change default trials
DEFAULT_NUM_TRIALS = 5

# Modify Anthropic cache type
ANTHROPIC_CACHE_TYPE = "persistent"  # or "ephemeral"

# Adjust timezone for timestamps
TIMEZONE = "America/New_York"
```

### Batch Processing

```bash
# Test multiple prompts
python main.py --prompt "Prompt 1" --output test1.csv
python main.py --prompt "Prompt 2" --output test2.csv

# Provider-specific testing
for provider in openai gemini anthropic grok; do
    python main.py --vendors $provider --trials 1 --output ${provider}_test.csv
done
```

## Pricing Information

### Current Pricing (per 1M tokens)

| Provider | Input | Cached Input | Output | Notes |
|----------|-------|--------------|--------|-------|
| OpenAI | $2.50 | $0.50 (80% off) | $8.00 | Simple caching |
| Gemini | $1.25/$2.50 | Unknown | $10.00/$15.00 | Tiered at 200K tokens |
| Anthropic | $3.00 | $0.30/$3.75/$6.00 | $15.00 | Configurable cache types |
| Grok | $3.00/$6.00 | $0.75/$1.50 | $15.00/$30.00 | Tiered at 128K tokens |

### Tiered Pricing

**Gemini 2.5 Pro:**
- ≤200K tokens: Lower rates
- >200K tokens: Higher rates

**Grok-2:**
- ≤128K tokens: Standard rates  
- >128K tokens: Higher rates (2x)

**Anthropic Cache Types:**
- Ephemeral (~5min): $3.75 writes, $0.30 reads
- Persistent (~1hr): $6.00 writes, $0.30 reads

## Troubleshooting

### Common Issues

```bash
# API key not set
export OPENAI_API_KEY="your-key-here"

# Invalid provider name
python main.py --vendors openai,gemini  # Correct
python main.py --vendors gpt4,claude    # Wrong

# Output directory doesn't exist
mkdir -p outputs

# Permission issues
chmod +x main.py
```

### Error Messages

| Error | Solution |
|-------|----------|
| "Invalid vendor" | Check provider names: openai, gemini, anthropic, grok |
| "API key missing" | Set environment variables or update config.py |
| "Model not found" | Check if model names in config.py are current |
| "Rate limit exceeded" | Reduce trials or add delays between calls |

### Debug Mode

```bash
# Single trial for debugging
python main.py --trials 1 --vendors openai

# Check specific provider
python main.py --vendors gemini --prompt "test" --trials 1
```

## Performance Tips

### Efficient Testing

```bash
# Quick cost check
python main.py --trials 1 --prompt "short test"

# Focus on specific providers
python main.py --vendors openai,anthropic --trials 3

# Batch similar tests
python main.py --vendors gemini --trials 5 --prompt "$(cat test_prompts.txt)"
```

### Cost Optimization

- Use `--trials 1` for initial testing
- Test expensive providers (Anthropic, Grok) separately
- Use shorter prompts for cost comparison
- Monitor tiered pricing thresholds

## Integration Examples

### Shell Scripts

```bash
#!/bin/bash
# cost_comparison.sh

echo "Running cost comparison..."
python main.py --vendors openai,gemini --trials 3 --prompt "$1" --output "comparison_$(date +%Y%m%d).csv"
echo "Results saved to outputs/"
```

### Python Integration

```python
import subprocess
import json

def run_token_counter(prompt, vendors=None, trials=3):
    cmd = ["python", "main.py", "--prompt", prompt, "--trials", str(trials)]
    if vendors:
        cmd.extend(["--vendors", ",".join(vendors)])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0
```

## Version Information

Run `python main.py --help` to see current version and available options.

For configuration details and pricing updates, see the main README.md file.