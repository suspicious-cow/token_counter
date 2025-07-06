"""
Gemini client module for token counting.

Features:
- Supports Gemini 2.5 Flash with controllable reasoning via thinking_budget
- thinking_budget=0 disables internal reasoning (like GPT-4.1)
- thinking_budget>0 enables reasoning with token limit (up to 24,576)
"""

from google import genai
from google.genai import types
from config import GEMINI_API_KEY, MODELS_INFO, GEMINI_THINKING_BUDGET


def process_with_gemini(prompt, system_prompt, model=None):
    """
    Process a prompt using Google's Gemini API.
    
    Args:
        prompt (str): The user prompt
        system_prompt (str): The system prompt (can be empty)
        model (str): The model to use (defaults to config setting)
    
    Returns:
        tuple: (output, input_tokens, output_tokens)
    """
    if model is None:
        model = MODELS_INFO["gemini"]["model"]
    
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Create thinking configuration to control internal reasoning
        # thinking_budget=0 disables reasoning (like non-reasoning models)
        # thinking_budget>0 enables reasoning with specified token limit
        thinking_config = types.ThinkingConfig(thinking_budget=GEMINI_THINKING_BUDGET)
        
        if system_prompt:
            # Add system instruction if provided
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                thinking_config=thinking_config
            )
        else:
            # Set thinking budget even without system instruction
            config = types.GenerateContentConfig(
                thinking_config=thinking_config
            )
            
        response = client.models.generate_content(
            model=model,
            config=config,
            contents=prompt
        )
        
        # Use response.text to preserve the actual LLM output (including newlines for accurate token counting)
        output = getattr(response, 'text', str(response))
        usage = getattr(response, 'usage_metadata', None)
        input_tokens = usage.prompt_token_count if usage and hasattr(usage, 'prompt_token_count') else None
        output_tokens = usage.candidates_token_count if usage and hasattr(usage, 'candidates_token_count') else None
        
        return output, input_tokens, output_tokens
    except Exception as e:
        return f"Gemini error: {str(e)}", None, None


def get_model_name():
    """Get the default model name for Gemini."""
    return MODELS_INFO["gemini"]["model"]
