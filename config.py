"""
Configuration file for the Token Counter project.
Contains API keys, default settings, and model configurations.
"""

import os
from datetime import datetime

# API Keys - Load from environment variables with fallback defaults
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your-anthropic-api-key")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
GROK_API_KEY = os.getenv("GROK_API_KEY", "your-grok-api-key")

# Default prompts and settings
DEFAULT_USER_PROMPT = "Give me the word 'hello' without any puncuation or any other characters"
DEFAULT_SYSTEM_PROMPT = ""
DEFAULT_NUM_TRIALS = 3

# Model configurations
MODELS = {
    "openai": "gpt-4o",
    "gemini": "gemini-2.0-flash", 
    "anthropic": "claude-3-7-sonnet-20250219",
    "grok": "grok-3-beta"
}

# Output settings
def get_timestamped_filename(base_name="api_results", extension="csv"):
    """Generate a timestamped filename for the current run."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"

CSV_OUTPUT_PATH = "api_results.csv"  # Default fallback, usually overridden with timestamp
CSV_COLUMNS = [
    'Run Number', 'Vendor', 'Model', 'User Prompt', 
    'System Prompt', 'Output', 'Input Tokens', 'Output Tokens'
]

# Anthropic specific settings
ANTHROPIC_MAX_TOKENS = 1024

# Grok API settings
GROK_BASE_URL = "https://api.x.ai/v1"
