"""
Retry utilities with exponential backoff.
"""

import time
import random
from functools import wraps
from typing import Callable, Any


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):  # +1 for initial attempt
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Don't retry on the last attempt
                    if attempt == max_retries:
                        break
                    
                    # Calculate delay with exponential backoff and jitter
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = random.uniform(0, delay * 0.1)  # Add up to 10% jitter
                    total_delay = delay + jitter
                    
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    print(f"Retrying in {total_delay:.2f} seconds...")
                    time.sleep(total_delay)
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    return decorator


class RetryableError(Exception):
    """Exception that should trigger a retry"""
    pass


class NonRetryableError(Exception):
    """Exception that should not trigger a retry"""
    pass