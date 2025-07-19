"""
Rate limiting utilities for API calls.
"""

import time
from collections import defaultdict
from typing import Dict


class RateLimiter:
    """Rate limiter to prevent hitting API rate limits"""
    
    def __init__(self, custom_intervals: Dict[str, float] = None):
        """
        Initialize rate limiter.
        
        Args:
            custom_intervals: Custom minimum intervals per provider
        """
        self.last_call = defaultdict(float)
        
        # Default minimum intervals between calls (seconds)
        self.min_intervals = {
            'openai': 0.1,      # 10 calls/second
            'gemini': 0.5,      # 2 calls/second (conservative for free tier)
            'anthropic': 0.2,   # 5 calls/second
            'grok': 0.1         # 10 calls/second
        }
        
        # Update with custom intervals if provided
        if custom_intervals:
            self.min_intervals.update(custom_intervals)
    
    def wait_if_needed(self, provider: str):
        """
        Wait if necessary to respect rate limits.
        
        Args:
            provider: Provider name (openai, gemini, anthropic, grok)
        """
        provider = provider.lower()
        now = time.time()
        last = self.last_call[provider]
        min_interval = self.min_intervals.get(provider, 0.1)
        
        time_since_last = now - last
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            print(f"Rate limiting: waiting {sleep_time:.2f}s for {provider}")
            time.sleep(sleep_time)
        
        self.last_call[provider] = time.time()
    
    def set_interval(self, provider: str, interval: float):
        """
        Set custom interval for a provider.
        
        Args:
            provider: Provider name
            interval: Minimum interval in seconds
        """
        self.min_intervals[provider.lower()] = interval
    
    def reset(self, provider: str = None):
        """
        Reset rate limiting state.
        
        Args:
            provider: Specific provider to reset, or None for all
        """
        if provider:
            self.last_call.pop(provider.lower(), None)
        else:
            self.last_call.clear()