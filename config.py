"""
Configuration file for the Token Counter project.
Contains API keys, default settings, and model configurations.
"""

import os
from datetime import datetime
try:
    from zoneinfo import ZoneInfo  # Python 3.9+

except ImportError:
    from pytz import timezone as ZoneInfo  # Fallback for older Python

# API Keys - Load from environment variables with fallback to manually entered keys if needed
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your-anthropic-api-key")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
GROK_API_KEY = os.getenv("GROK_API_KEY", "your-grok-api-key")

# Default prompts and settings
DEFAULT_USER_PROMPT = "Give me the word 'hello' without any puncuation or any other characters"
DEFAULT_SYSTEM_PROMPT = ""
DEFAULT_NUM_TRIALS = 3

# Model and pricing information for cost calculations (USD per 1M tokens)
# This is the single source of truth for both model names and pricing
# Unfortunately, most providers don't offer pricing through the API so updating cost is a manual process
MODELS_INFO = {
    "openai": {
        "model": "gpt-4.1",
        "input_cost_per_million": 2.00,    # USD per 1M *uncached* input tokens
        "cached_input_cost_per_million": 0.50, # USD per 1M *cached* input tokens (OpenAI cache discount, see docs)
        "output_cost_per_million": 8.00   # USD per 1M output tokens (no discount for completions)
        # Note: Only OpenAI exposes cached input tokens and discounts them. See comments below.
    },
    "gemini": {
        "model": "gemini-2.5-flash",
        "input_cost_per_million": 0.30,    # USD per 1M *uncached* input tokens
        "cached_input_cost_per_million": 0.075, # USD per 1M *cached* input tokens (75% discount from regular price)
        "output_cost_per_million": 2.50    # USD per 1M output tokens
        # Note: Gemini supports both implicit (automatic) and explicit context caching with 75% discount
    },
    "anthropic": {
        "model": "claude-3-7-sonnet-20250219",
        "input_cost_per_million": 3.00,    # USD per 1M input tokens
        "cached_input_cost_per_million": 0.30, # USD per 1M cached input tokens (90% discount for cache reads)
        "output_cost_per_million": 15.00   # USD per 1M output tokens
        # Note: Anthropic charges 25% premium for cache writes, 90% discount for cache reads
    },
    "grok": {
        "model": "grok-3-beta",
        "input_cost_per_million": 0.00,    # Set to actual if available
        "output_cost_per_million": 0.00    # Set to actual if available
    }
}

# Timezone configuration (default: Central Time)
TIMEZONE = os.getenv("TOKEN_COUNTER_TIMEZONE", "America/Chicago")  # Change to your preferred IANA timezone string

# Output settings
def get_timestamped_filename(base_name="api_results", extension="csv"):
    """Generate a timestamped filename for the current run in the outputs/ folder, using 24-hour time and configured timezone, with timezone abbreviation in the filename."""
    try:
        tz = ZoneInfo(TIMEZONE)
    except Exception:
        tz = None
    now = datetime.now(tz) if tz else datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    tz_abbr = now.strftime('%Z') if tz else "local"
    return os.path.join("outputs", f"{base_name}_{timestamp}_{tz_abbr}.{extension}")

CSV_OUTPUT_PATH = "api_results.csv"  # Default fallback, usually overridden with timestamp
CSV_COLUMNS = [
    'Run Number', 'Vendor', 'Model', 'User Prompt', 
    'System Prompt', 'Output', 'Input Tokens', 'Cached Input Tokens', 'Output Tokens',
    'Input Token Cost (USD)', 'Cached Token Cost (USD)', 'Output Token Cost (USD)', 'Cost (USD)'
]

# Note: For providers with caching (OpenAI, Gemini, Anthropic):
# - "Input Tokens" = regular/uncached input tokens only (I_reg)
# - "Cached Input Tokens" = tokens retrieved from cache (I_cache) 
# - Total input tokens = Input Tokens + Cached Input Tokens
# - Costs are calculated using the respective pricing rates per the provider's formula

# Anthropic specific settings
ANTHROPIC_MAX_TOKENS = 1024

# Gemini specific settings
GEMINI_THINKING_BUDGET = 0  # Set to 0 to disable internal reasoning, or higher values (up to 24576) to enable reasoning

# Grok API settings
GROK_BASE_URL = "https://api.x.ai/v1"

#
# OpenAI Caching Notes:
# - OpenAI’s API discounts *input* tokens that are fetched from their internal cache (see openai.com/docs/guides/rate-limits/caching).
# - The API response includes `prompt_tokens` (total input), and `prompt_tokens_details.cached_tokens` (subset that was cached).
# - Cost calculation:
#     uncached_input   = prompt_tokens - cached_tokens
#     cached_input    = cached_tokens
#     output          = completion_tokens
#     total_cost = (uncached_input * input_cost + cached_input * cached_input_cost + output * output_cost) / 1_000_000
# - Output tokens are never discounted or cached.
# - Only OpenAI exposes this breakdown; other vendors do not.
