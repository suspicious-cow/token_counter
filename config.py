"""
Configuration file for the Token Counter project.
Contains API keys, default settings, and model configurations.
"""

import os
from datetime import datetime
from pathlib import Path

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:
    from pytz import timezone as ZoneInfo  # Fallback for older Python

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    
    # Look for .env file in the project root
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment variables from {env_path}")
    else:
        print("No .env file found, using system environment variables")
        
except ImportError:
    print("python-dotenv not installed. Install with: pip install python-dotenv")
    print("Using system environment variables only")

# API Keys - Load from .env file first, then system environment, then fallback
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your-anthropic-api-key")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
GROK_API_KEY = os.getenv("GROK_API_KEY", "your-grok-api-key")

# Default prompts and settings
DEFAULT_USER_PROMPT = "Give me the word 'halt' without any formatting or additional text."
DEFAULT_SYSTEM_PROMPT = ""
DEFAULT_NUM_TRIALS = 1

# Model and pricing information for cost calculations (USD per 1M tokens)
# This is the single source of truth for both model names and pricing
# Pricing is manually maintained - update when providers change rates
# Last updated: January 2025
MODELS_INFO = {
    "openai": {
        "model": "gpt-4.1",  # Latest GPT-4o model (November 2024)
        "input_cost_per_million": 2.00,    # USD per 1M input tokens (verified from actual billing)
        "cached_input_cost_per_million": .50, # USD per 1M cached input tokens (50% discount)
        "output_cost_per_million": 8.00   # USD per 1M output tokens (gpt-4o pricing)
        # Note: OpenAI automatic prompt caching - 75% discount on cached input tokens (≥1024 tokens)
        # Caching is automatic for repeated prompt prefixes, no explicit cache management needed
    },
    "gemini": {
        "model": "gemini-2.5-pro",  # Gemini 2.5 Pro with tiered pricing
        "tiered_pricing": True,  # Flag to indicate this uses tiered pricing
        "pricing_tiers": {
            "threshold": 200000,  # 200K tokens threshold
            "low_tier": {  # <=200K tokens
                "input_cost_per_million": 1.25,
                "output_cost_per_million": 10.00
            },
            "high_tier": {  # >200K tokens
                "input_cost_per_million": 2.50,
                "output_cost_per_million": 15.00
            }
        },
        # Fallback for backward compatibility (using low tier rates)
        "input_cost_per_million": 1.25,
        "cached_input_cost_per_million": 0.31,  # Assuming 75% discount like other providers
        "output_cost_per_million": 10.00
        # Note: Gemini 2.5 Pro has tiered pricing - rates increase after 200K tokens
        # UI remains free of charge, API pricing shown above
    },
    "anthropic": {
        "model": "claude-sonnet-4-20250514",  # Claude Sonnet 4 (May 2025)
        "input_cost_per_million": 3.00,    # USD per 1M input tokens
        "output_cost_per_million": 15.00,   # USD per 1M output tokens
        "cache_pricing": {
            "ephemeral": {  # ~5 minute TTL
                "cache_write_multiplier": 1.25,  # $3.75 per 1M tokens (25% markup: $3.00 * 1.25)
                "cache_read_multiplier": 0.10,   # $0.30 per 1M tokens (90% discount: $3.00 * 0.10)
                "storage_cost_per_million_per_hour": 0.0  # No storage cost for ephemeral
            },
            "persistent": {  # ~1 hour TTL  
                "cache_write_multiplier": 2.00,  # $6.00 per 1M tokens (1h cache writes)
                "cache_read_multiplier": 0.10,   # $0.30 per 1M tokens (cache hits & refreshes)
                "storage_cost_per_million_per_hour": 0.0  # Storage cost included in write price
            }
        },
        # Fallback for backward compatibility (ephemeral rates)
        "cached_input_cost_per_million": 0.30
        # Note: Cache type controlled by ANTHROPIC_CACHE_TYPE config setting
        # Pricing: Base $3.00, 5m writes $3.75, 1h writes $6.00, cache reads $0.30, output $15.00
    },
    "grok": {
        "model": "grok-4",  # Latest Grok-4 model
        "tiered_pricing": True,  # Flag to indicate this uses tiered pricing
        "pricing_tiers": {
            "threshold": 128000,  # 128K tokens threshold
            "standard_tier": {  # ≤128K tokens
                "input_cost_per_million": 3.00,
                "cached_input_cost_per_million": 0.75,
                "output_cost_per_million": 15.00
            },
            "higher_context_tier": {  # >128K tokens
                "input_cost_per_million": 6.00,  # Estimated higher rate
                "cached_input_cost_per_million": 1.50,  # Estimated higher rate
                "output_cost_per_million": 30.00  # Estimated higher rate
            }
        },
        # Fallback for backward compatibility (using standard tier rates)
        "input_cost_per_million": 3.00,
        "cached_input_cost_per_million": 0.75,
        "output_cost_per_million": 15.00
        # Note: Grok has tiered pricing - rates increase after 128K tokens
        # Higher context pricing applies when total context exceeds 128K tokens
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
    timestamp = now.strftime("%Y%m%d_%H%M%S") + f"{now.microsecond // 1000:03d}"
    tz_abbr = now.strftime('%Z') if tz else "local"
    return os.path.join("outputs", f"{base_name}_{timestamp}_{tz_abbr}.{extension}")

CSV_OUTPUT_PATH = "api_results.csv"  # Default fallback, usually overridden with timestamp
CSV_COLUMNS = [
    'Run Number', 'Vendor', 'Model', 'User Prompt', 
    'System Prompt', 'Output', 'Input Tokens', 'Cached Input Tokens', 'Output Tokens',
    'Input Token Cost (USD)', 'Cached Token Cost (USD)', 'Output Token Cost (USD)', 'Cost (USD)'
]

# Note: For providers with caching (OpenAI, Gemini, Anthropic, Grok):
# - "Input Tokens" = TOTAL input tokens from API (I_total)
# - "Cached Input Tokens" = tokens retrieved from cache (I_cache) 
# - Uncached input tokens = Input Tokens - Cached Input Tokens (calculated for cost only)
# - Costs are calculated using the respective pricing rates per the provider's formula

# Anthropic specific settings
ANTHROPIC_MAX_TOKENS = 1024
ANTHROPIC_CACHE_TYPE = "ephemeral"  # Options: "ephemeral" (~5min TTL) or "persistent" (~1hr TTL)

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
