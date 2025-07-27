"""
Main script for running token count comparisons across multiple LLM providers.

This script runs experiments with OpenAI, Gemini, Anthropic, and Grok APIs
to compare their outputs and token counts.

Usage:
    python main.py                                    # Use defaults from config.py
    python main.py --prompt "Your custom prompt"     # Custom user prompt
    python main.py --trials 5                        # Custom number of trials
    python main.py --output "results.csv"            # Custom output file
    python main.py --prompt "Test" --trials 1        # Multiple custom options
"""

import pandas as pd
import argparse
from config import (
    DEFAULT_USER_PROMPT, DEFAULT_SYSTEM_PROMPT, DEFAULT_NUM_TRIALS,
    CSV_OUTPUT_PATH, CSV_COLUMNS, get_timestamped_filename, MODELS_INFO,
    ANTHROPIC_CACHE_TYPE
)
from clients.openai_client import process_with_openai, get_model_name as get_openai_model
from clients.gemini_client import process_with_gemini, get_model_name as get_gemini_model
from clients.anthropic_client import process_with_anthropic, get_model_name as get_anthropic_model
from clients.grok_client import process_with_grok, get_model_name as get_grok_model


def calculate_gemini_tiered_cost(input_tokens, cached_tokens, output_tokens):
    """
    Calculate Gemini 2.5 Pro cost using tiered pricing structure.

    Args:
        input_tokens: Total input tokens
        cached_tokens: Cached input tokens
        output_tokens: Output tokens

    Returns:
        tuple: (input_cost, cached_cost, output_cost, total_cost)
    """
    gemini_config = MODELS_INFO['gemini']

    # Check if this model uses tiered pricing
    if not gemini_config.get('tiered_pricing', False):
        # Fall back to simple pricing
        regular_input_tokens = input_tokens - cached_tokens
        input_cost = regular_input_tokens * gemini_config['input_cost_per_million'] / 1_000_000
        cached_cost = cached_tokens * gemini_config['cached_input_cost_per_million'] / 1_000_000
        output_cost = output_tokens * gemini_config['output_cost_per_million'] / 1_000_000
        return input_cost, cached_cost, output_cost, input_cost + cached_cost + output_cost
    
    # Tiered pricing calculation
    pricing_tiers = gemini_config['pricing_tiers']
    threshold = pricing_tiers['threshold']
    total_tokens = input_tokens + output_tokens
    
    # Determine which tier to use based on total token count
    if total_tokens <= threshold:
        # Low tier (<=200K tokens)
        tier = pricing_tiers['low_tier']
    else:
        # High tier (>200K tokens)
        tier = pricing_tiers['high_tier']
    
    # Calculate costs using the appropriate tier
    # For Gemini 2.5 Pro: charge full price for all input tokens (no caching discount)
    # but still track and display cached token counts when they appear
    input_cost = input_tokens * tier['input_cost_per_million'] / 1_000_000
    cached_cost = 0.0  # Unknown pricing for cached tokens (not documented by Google)
    output_cost = output_tokens * tier['output_cost_per_million'] / 1_000_000
    
    return input_cost, cached_cost, output_cost, input_cost + cached_cost + output_cost


def calculate_anthropic_cache_cost(input_tokens, cache_creation_tokens, cache_read_tokens, output_tokens):
    """
    Calculate Anthropic cost using configured cache type (ephemeral or persistent).
    
    Args:
        input_tokens: Total input tokens
        cache_creation_tokens: Tokens used for cache creation
        cache_read_tokens: Tokens read from cache
        output_tokens: Output tokens
        
    Returns:
        tuple: (regular_input_cost, cache_creation_cost, cache_read_cost, output_cost, total_cost)
    """
    anthropic_config = MODELS_INFO['anthropic']
    cache_type = ANTHROPIC_CACHE_TYPE.lower()
    
    # Get cache pricing for the configured type
    if cache_type in anthropic_config['cache_pricing']:
        cache_config = anthropic_config['cache_pricing'][cache_type]
    else:
        # Fallback to ephemeral if invalid cache type
        cache_config = anthropic_config['cache_pricing']['ephemeral']
        print(f"Warning: Invalid cache type '{cache_type}', using ephemeral pricing")
    
    # Calculate regular input tokens (total - cache creation - cache read)
    regular_input_tokens = max(input_tokens - cache_creation_tokens - cache_read_tokens, 0)
    
    # Base rate for calculations
    base_rate = anthropic_config['input_cost_per_million'] / 1_000_000
    
    # Calculate costs using configured cache type
    regular_input_cost = regular_input_tokens * base_rate
    cache_creation_cost = cache_creation_tokens * base_rate * cache_config['cache_write_multiplier']
    cache_read_cost = cache_read_tokens * base_rate * cache_config['cache_read_multiplier']
    output_cost = output_tokens * anthropic_config['output_cost_per_million'] / 1_000_000
    
    # Note: Storage cost for persistent caching not implemented yet (requires time tracking)
    # storage_cost = cache_creation_tokens * cache_config['storage_cost_per_million_per_hour'] / 1_000_000 * hours
    
    total_cost = regular_input_cost + cache_creation_cost + cache_read_cost + output_cost
    
    return regular_input_cost, cache_creation_cost, cache_read_cost, output_cost, total_cost


def calculate_grok_tiered_cost(input_tokens, cached_tokens, output_tokens):
    """
    Calculate Grok cost using tiered pricing structure for higher context.
    
    Args:
        input_tokens: Total input tokens
        cached_tokens: Cached input tokens  
        output_tokens: Output tokens
        
    Returns:
        tuple: (input_cost, cached_cost, output_cost, total_cost)
    """
    grok_config = MODELS_INFO['grok']
    
    # Check if this model uses tiered pricing
    if not grok_config.get('tiered_pricing', False):
        # Fall back to simple pricing
        regular_input_tokens = input_tokens - cached_tokens
        input_cost = regular_input_tokens * grok_config['input_cost_per_million'] / 1_000_000
        cached_cost = cached_tokens * grok_config['cached_input_cost_per_million'] / 1_000_000
        output_cost = output_tokens * grok_config['output_cost_per_million'] / 1_000_000
        return input_cost, cached_cost, output_cost, input_cost + cached_cost + output_cost
    
    # Tiered pricing calculation
    pricing_tiers = grok_config['pricing_tiers']
    threshold = pricing_tiers['threshold']
    total_context_tokens = input_tokens + output_tokens  # Total context size
    
    # Determine which tier to use based on total context size
    if total_context_tokens <= threshold:
        # Standard tier (≤128K tokens)
        tier = pricing_tiers['standard_tier']
    else:
        # Higher context tier (>128K tokens)
        tier = pricing_tiers['higher_context_tier']
    
    # Calculate costs using the appropriate tier
    regular_input_tokens = input_tokens - cached_tokens
    input_cost = regular_input_tokens * tier['input_cost_per_million'] / 1_000_000
    cached_cost = cached_tokens * tier['cached_input_cost_per_million'] / 1_000_000
    output_cost = output_tokens * tier['output_cost_per_million'] / 1_000_000
    
    return input_cost, cached_cost, output_cost, input_cost + cached_cost + output_cost


def calculate_grok_tiered_cost_with_reasoning(input_tokens, cached_tokens, output_tokens, reasoning_tokens):
    """
    Calculate Grok cost using tiered pricing structure including reasoning tokens.
    
    Args:
        input_tokens: Total input tokens
        cached_tokens: Cached input tokens
        output_tokens: Output tokens
        reasoning_tokens: Hidden reasoning tokens (charged at output rate)
        
    Returns:
        tuple: (input_cost, cached_cost, output_cost, reasoning_cost, total_cost)
    """
    grok_config = MODELS_INFO['grok']
    
    # Check if this model uses tiered pricing
    if not grok_config.get('tiered_pricing', False):
        # Fall back to simple pricing
        regular_input_tokens = input_tokens - cached_tokens
        input_cost = regular_input_tokens * grok_config['input_cost_per_million'] / 1_000_000
        cached_cost = cached_tokens * grok_config['cached_input_cost_per_million'] / 1_000_000
        output_cost = output_tokens * grok_config['output_cost_per_million'] / 1_000_000
        reasoning_cost = reasoning_tokens * grok_config['output_cost_per_million'] / 1_000_000  # Reasoning charged at output rate
        return input_cost, cached_cost, output_cost, reasoning_cost, input_cost + cached_cost + output_cost + reasoning_cost

    # Tiered pricing calculation
    pricing_tiers = grok_config['pricing_tiers']
    threshold = pricing_tiers['threshold']
    total_context_tokens = input_tokens + output_tokens + reasoning_tokens  # Include reasoning in context calculation

    # Determine which tier to use based on total context size
    if total_context_tokens <= threshold:
        # Standard tier (≤128K tokens)
        tier = pricing_tiers['standard_tier']
    else:
        # Higher context tier (>128K tokens)
        tier = pricing_tiers['higher_context_tier']

    # Calculate costs using the appropriate tier
    regular_input_tokens = input_tokens - cached_tokens
    input_cost = regular_input_tokens * tier['input_cost_per_million'] / 1_000_000
    cached_cost = cached_tokens * tier['cached_input_cost_per_million'] / 1_000_000
    output_cost = output_tokens * tier['output_cost_per_million'] / 1_000_000
    reasoning_cost = reasoning_tokens * tier['output_cost_per_million'] / 1_000_000  # Reasoning charged at output rate

    return input_cost, cached_cost, output_cost, reasoning_cost, input_cost + cached_cost + output_cost + reasoning_cost


def run_single_trial(prompt, system_prompt, trial_number, vendors=None):
    """
    Run a single trial across selected LLM providers.
    
    Args:
        prompt (str): The user prompt
        system_prompt (str): The system prompt
        trial_number (int): The trial number
        vendors (list or None): List of vendors to run (default: all)
    
    Returns:
        list: List of result dictionaries
    """
    results = []
    vendors = [v.lower() for v in vendors] if vendors else ['openai', 'gemini', 'anthropic', 'grok']
    if 'openai' in vendors:
        try:
            output, in_tok, cached_in_tok, out_tok = process_with_openai(prompt, system_prompt)
            # Raw token counts - no calculations
            input_tokens = in_tok or 0
            cached_input_tokens = int(cached_in_tok) if cached_in_tok is not None else 0
            output_tokens = out_tok or 0
            
            # Cost calculation: uncached = total - cached, cached = cached
            uncached_input = max(input_tokens - cached_input_tokens, 0)
            input_token_cost = uncached_input * MODELS_INFO['openai']['input_cost_per_million'] / 1_000_000
            cached_token_cost = cached_input_tokens * MODELS_INFO['openai']['cached_input_cost_per_million'] / 1_000_000
            output_token_cost = output_tokens * MODELS_INFO['openai']['output_cost_per_million'] / 1_000_000
            cost = input_token_cost + cached_token_cost + output_token_cost
            
            # Display detailed cost breakdown during run
            print(f"  ✅ OpenAI:")
            print(f"     Tokens: {input_tokens} total in ({uncached_input} uncached + "
                  f"{cached_input_tokens} cached) + {output_tokens} out")
            print(f"     Costs: ${input_token_cost:.6f} uncached + ${cached_token_cost:.6f} cached + "
                  f"${output_token_cost:.6f} output = ${cost:.6f} total")
            
            results.append({
                'Run Number': trial_number,
                'Vendor': 'OpenAI',
                'Model': get_openai_model(),
                'User Prompt': prompt,
                'System Prompt': system_prompt,
                'Output': output,
                'Input Tokens': input_tokens,
                'Cached Input Tokens': cached_input_tokens,
                'Output Tokens': output_tokens,
                'Reasoning Tokens': 0,  # OpenAI doesn't use reasoning tokens
                'Input Token Cost (USD)': round(input_token_cost, 6),
                'Cached Token Cost (USD)': round(cached_token_cost, 6),
                'Output Token Cost (USD)': round(output_token_cost, 6),
                'Reasoning Token Cost (USD)': 0.0,  # No reasoning cost for OpenAI
                'Cost (USD)': round(cost, 6)
            })
        except Exception as e:
            results.append({
                'Run Number': trial_number,
                'Vendor': 'OpenAI',
                'Model': get_openai_model(),
                'User Prompt': prompt,
                'System Prompt': system_prompt,
                'Output': f"Error: {str(e)}",
                'Input Tokens': None,
                'Cached Input Tokens': 0,
                'Output Tokens': None,
                'Reasoning Tokens': 0,
                'Input Token Cost (USD)': None,
                'Cached Token Cost (USD)': None,
                'Output Token Cost (USD)': None,
                'Reasoning Token Cost (USD)': None,
                'Cost (USD)': None
            })
    if 'gemini' in vendors:
        try:
            output, in_tok, cached_in_tok, out_tok = process_with_gemini(prompt, system_prompt)
            total_input_tokens = in_tok or 0
            cached_input_tokens = cached_in_tok or 0
            regular_input_tokens = total_input_tokens - cached_input_tokens
            output_tokens = out_tok or 0
            
            # Cost calculation using tiered pricing
            regular_input_cost, cached_input_cost, output_cost, total_cost = calculate_gemini_tiered_cost(
                total_input_tokens, cached_input_tokens, output_tokens
            )
            
            # Display detailed cost breakdown during run
            print(f"  ✅ Gemini:")
            print(f"     Tokens: {total_input_tokens} total in ({regular_input_tokens} uncached + "
                  f"{cached_input_tokens} cached) + {output_tokens} out")
            print(f"     Costs: ${regular_input_cost:.6f} uncached + ${cached_input_cost:.6f} cached + "
                  f"${output_cost:.6f} output = ${total_cost:.6f} total")
            
            results.append({
                'Run Number': trial_number,
                'Vendor': 'Gemini',
                'Model': get_gemini_model(),
                'User Prompt': prompt,
                'System Prompt': system_prompt,
                'Output': output,
                'Input Tokens': total_input_tokens,
                'Cached Input Tokens': cached_input_tokens,
                'Output Tokens': output_tokens,
                'Reasoning Tokens': 0,  # Gemini doesn't use reasoning tokens
                'Input Token Cost (USD)': round(regular_input_cost, 6),
                'Cached Token Cost (USD)': round(cached_input_cost, 6),
                'Output Token Cost (USD)': round(output_cost, 6),
                'Reasoning Token Cost (USD)': 0.0,  # No reasoning cost for Gemini
                'Cost (USD)': round(total_cost, 6)
            })
        except Exception as e:
            results.append({
                'Run Number': trial_number,
                'Vendor': 'Gemini',
                'Model': get_gemini_model(),
                'User Prompt': prompt,
                'System Prompt': system_prompt,
                'Output': f"Error: {str(e)}",
                'Input Tokens': None,
                'Cached Input Tokens': 0,
                'Output Tokens': None,
                'Reasoning Tokens': 0,
                'Input Token Cost (USD)': None,
                'Cached Token Cost (USD)': None,
                'Output Token Cost (USD)': None,
                'Reasoning Token Cost (USD)': None,
                'Cost (USD)': None
            })
    if 'anthropic' in vendors:
        try:
            output, in_tok, cache_creation_tok, cache_read_tok, out_tok = process_with_anthropic(prompt, system_prompt)
            # Raw token counts from Claude API
            input_tokens = in_tok or 0
            cache_creation_tokens = cache_creation_tok or 0
            cache_read_tokens = cache_read_tok or 0
            output_tokens = out_tok or 0
            
            # Use configured cache type for cost calculation
            regular_input_cost, cache_creation_cost, cache_read_cost, output_token_cost, cost = calculate_anthropic_cache_cost(
                input_tokens, cache_creation_tokens, cache_read_tokens, output_tokens
            )
            
            # Display detailed cost breakdown during run
            total_cached_tokens = cache_creation_tokens + cache_read_tokens
            regular_input_tokens = max(input_tokens - cache_creation_tokens - cache_read_tokens, 0)
            print(f"  ✅ Anthropic:")
            print(f"     Tokens: {input_tokens} total in ({regular_input_tokens} regular + "
                  f"{cache_creation_tokens} cache-write + {cache_read_tokens} cache-read) + {output_tokens} out")
            print(f"     Costs: ${regular_input_cost:.6f} regular + ${cache_creation_cost:.6f} cache-write + "
                  f"${cache_read_cost:.6f} cache-read + ${output_token_cost:.6f} output = ${cost:.6f} total")
            
            results.append({
                'Run Number': trial_number,
                'Vendor': 'Anthropic',
                'Model': get_anthropic_model(),
                'User Prompt': prompt,
                'System Prompt': system_prompt,
                'Output': output,
                'Input Tokens': input_tokens,
                'Cached Input Tokens': total_cached_tokens,
                'Output Tokens': output_tokens,
                'Reasoning Tokens': 0,  # Anthropic doesn't use reasoning tokens
                'Input Token Cost (USD)': round(regular_input_cost, 6),
                'Cached Token Cost (USD)': round(cache_creation_cost + cache_read_cost, 6),
                'Output Token Cost (USD)': round(output_token_cost, 6),
                'Reasoning Token Cost (USD)': 0.0,  # No reasoning cost for Anthropic
                'Cost (USD)': round(cost, 6)
            })
        except Exception as e:
            results.append({
                'Run Number': trial_number,
                'Vendor': 'Anthropic',
                'Model': get_anthropic_model(),
                'User Prompt': prompt,
                'System Prompt': system_prompt,
                'Output': f"Error: {str(e)}",
                'Input Tokens': None,
                'Cached Input Tokens': 0,
                'Output Tokens': None,
                'Reasoning Tokens': 0,
                'Input Token Cost (USD)': None,
                'Cached Token Cost (USD)': None,
                'Output Token Cost (USD)': None,
                'Reasoning Token Cost (USD)': None,
                'Cost (USD)': None
            })
    if 'grok' in vendors:
        try:
            output, in_tok, cached_in_tok, out_tok, reasoning_tok = process_with_grok(prompt, system_prompt)
            # Raw token counts - no calculations
            input_tokens = in_tok or 0
            cached_input_tokens = int(cached_in_tok) if cached_in_tok is not None else 0
            output_tokens = out_tok or 0
            reasoning_tokens = reasoning_tok or 0
            
            # Use tiered pricing for cost calculation INCLUDING reasoning tokens
            input_token_cost, cached_token_cost, output_token_cost, reasoning_token_cost, cost = calculate_grok_tiered_cost_with_reasoning(
                input_tokens, cached_input_tokens, output_tokens, reasoning_tokens
            )
            
            # Display detailed cost breakdown during run
            uncached_input = max(input_tokens - cached_input_tokens, 0)
            total_visible_tokens = input_tokens + output_tokens
            total_billable_tokens = input_tokens + output_tokens + reasoning_tokens
            print(f"  ✅ Grok:")
            print(f"     Tokens: {total_billable_tokens} total ({uncached_input} uncached + "
                  f"{cached_input_tokens} cached + {output_tokens} output + {reasoning_tokens} reasoning)")
            print(f"     Costs: ${input_token_cost:.6f} uncached + ${cached_token_cost:.6f} cached + "
                  f"${output_token_cost:.6f} output + ${reasoning_token_cost:.6f} reasoning = ${cost:.6f} total")
            
            results.append({
                'Run Number': trial_number,
                'Vendor': 'Grok',
                'Model': get_grok_model(),
                'User Prompt': prompt,
                'System Prompt': system_prompt,
                'Output': output,
                'Input Tokens': input_tokens,
                'Cached Input Tokens': cached_input_tokens,
                'Output Tokens': output_tokens,
                'Reasoning Tokens': reasoning_tokens,
                'Input Token Cost (USD)': round(input_token_cost, 6),
                'Cached Token Cost (USD)': round(cached_token_cost, 6),
                'Output Token Cost (USD)': round(output_token_cost, 6),
                'Reasoning Token Cost (USD)': round(reasoning_token_cost, 6),
                'Cost (USD)': round(cost, 6)
            })
        except Exception as e:
            results.append({
                'Run Number': trial_number,
                'Vendor': 'Grok',
                'Model': get_grok_model(),
                'User Prompt': prompt,
                'System Prompt': system_prompt,
                'Output': f"Error: {str(e)}",
                'Input Tokens': None,
                'Cached Input Tokens': 0,
                'Output Tokens': None,
                'Reasoning Tokens': 0,
                'Input Token Cost (USD)': None,
                'Cached Token Cost (USD)': None,
                'Output Token Cost (USD)': None,
                'Reasoning Token Cost (USD)': None,
                'Cost (USD)': None
            })
    return results


def run_experiments(prompt=None, system_prompt=None, num_trials=None, vendors=None):
    """
    Run the complete experiment across selected LLM providers.
    
    Args:
        prompt (str): User prompt (defaults to config setting)
        system_prompt (str): System prompt (defaults to config setting)
        num_trials (int): Number of trials to run (defaults to config setting)
        vendors (list or None): List of vendors to run (default: all)
    
    Returns:
        pandas.DataFrame: Results dataframe
    """
    # Use defaults if not provided
    if prompt is None:
        prompt = DEFAULT_USER_PROMPT
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT
    if num_trials is None:
        num_trials = DEFAULT_NUM_TRIALS
    if vendors is None:
        vendors = ['openai', 'gemini', 'anthropic', 'grok']
    print(f"Starting token counter experiment:")
    print(f"  User prompt: '{prompt}'")
    print(f"  System prompt: '{system_prompt}'")
    print(f"  Number of trials: {num_trials}")
    print(f"  Testing: {', '.join([v.capitalize() for v in vendors])}")
    print()
    
    all_results = []
    
    # Run trials with cost tracking
    trial_costs = []
    for trial in range(1, num_trials + 1):
        print(f"Running trial {trial}/{num_trials}...")
        trial_results = run_single_trial(prompt, system_prompt, trial, vendors=vendors)
        all_results.extend(trial_results)
        
        # Track costs for this trial
        trial_cost = sum([r['Cost (USD)'] for r in trial_results if r['Cost (USD)'] is not None])
        trial_costs.append(trial_cost)
        print(f"  Trial {trial} total cost: ${trial_cost:.6f}")
    
    # Create DataFrame
    df = pd.DataFrame(all_results, columns=CSV_COLUMNS)
    
    # Display experiment cost summary
    total_cost = sum(trial_costs)
    avg_cost_per_trial = total_cost / len(trial_costs) if trial_costs else 0
    
    print(f"\n" + "="*50)
    print("EXPERIMENT COST SUMMARY")
    print("="*50)
    print(f"Total experiment cost: ${total_cost:.6f}")
    print(f"Average cost per trial: ${avg_cost_per_trial:.6f}")
    print(f"Completed {num_trials} trials with {len(df)} total API calls.")
    
    return df


def save_results_to_csv(df, output_path=None):
    """
    Save results to CSV file.
    
    Args:
        df (pandas.DataFrame): Results dataframe
        output_path (str): Output file path (defaults to config setting)
    """
    if output_path is None:
        output_path = CSV_OUTPUT_PATH
    
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Raw data saved to {output_path}")


def save_experiment_summary(df, summary_path):
    """
    Save the experiment summary (as printed) to a text file.
    """
    from io import StringIO
    import sys
    # Capture the printed summary
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    display_summary(df)
    sys.stdout = old_stdout
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(mystdout.getvalue())
    print(f"Experiment summary saved to {summary_path}")


def display_summary(df, log_failed_path=None):
    """
    Display a summary of the results, including failed call breakdown by vendor.
    Optionally log failed calls to a file for troubleshooting.
    Args:
        df (pandas.DataFrame): Results dataframe
        log_failed_path (str): Path to log file for failed calls (optional)
    """
    print("\n" + "="*50)
    print("EXPERIMENT SUMMARY")
    print("="*50)
    
    # Basic stats
    total_calls = len(df)
    successful_calls = len(df[~df['Output'].str.startswith('Error:', na=False)])
    failed_calls = total_calls - successful_calls
    
    print(f"Total API calls: {total_calls}")
    print(f"Successful calls: {successful_calls}")
    print(f"Failed calls: {failed_calls}")
    
    # Failed calls by vendor
    failed = df[df['Output'].str.startswith('Error:', na=False)]
    if not failed.empty:
        print("\nFailed calls by vendor:")
        failed_counts = failed['Vendor'].value_counts()
        for vendor, count in failed_counts.items():
            print(f"  {vendor}: {count}")
        # Log failed calls to file if requested
        if log_failed_path:
            with open(log_failed_path, 'w', encoding='utf-8') as f:
                f.write("Failed API Calls by Vendor\n")
                for vendor in failed['Vendor'].unique():
                    f.write(f"\nVendor: {vendor}\n")
                    vendor_failed = failed[failed['Vendor'] == vendor]
                    for _, row in vendor_failed.iterrows():
                        f.write(f"  Run {row['Run Number']}: {row['Output']}\n")
            print(f"\nDetailed failed call log written to: {log_failed_path}")
    else:
        print("\nNo failed calls by vendor.")
    
    # Enhanced cost analysis
    successful_df = df[~df['Output'].str.startswith('Error:', na=False)]
    if not successful_df.empty:
        print("\n" + "="*50)
        print("COST ANALYSIS")
        print("="*50)
        
        # Cost summary by vendor
        cost_summary = successful_df.groupby('Vendor').agg({
            'Cost (USD)': ['count', 'mean', 'sum', 'min', 'max', 'std']
        }).round(6)
        cost_summary.columns = ['Runs', 'Avg Cost', 'Total Cost', 'Min Cost', 'Max Cost', 'Std Dev']
        print("\nCost summary by vendor:")
        print(cost_summary)
        
        # Cost efficiency (output tokens per dollar)
        print("\nCost efficiency (output tokens per dollar):")
        efficiency = successful_df.groupby('Vendor', include_groups=False).apply(
            lambda x: x['Output Tokens'].sum() / x['Cost (USD)'].sum() if x['Cost (USD)'].sum() > 0 else 0
        ).round(0)
        for vendor, eff in efficiency.sort_values(ascending=False).items():
            print(f"  {vendor}: {eff:,.0f} tokens/$")
        
        # Individual run costs for comparison
        print("\nIndividual run costs by vendor:")
        for vendor in successful_df['Vendor'].unique():
            vendor_data = successful_df[successful_df['Vendor'] == vendor]['Cost (USD)']
            costs_str = ', '.join([f"${cost:.6f}" for cost in vendor_data])
            print(f"  {vendor}: {costs_str}")
        
        # Cost ranking
        total_costs = successful_df.groupby('Vendor')['Cost (USD)'].sum().sort_values()
        print(f"\nCost ranking (total experiment cost):")
        for i, (vendor, cost) in enumerate(total_costs.items(), 1):
            print(f"  {i}. {vendor}: ${cost:.6f}")
    
    # Token usage summary
    print("\n" + "="*50)
    print("TOKEN USAGE SUMMARY")
    print("="*50)
    
    if not successful_df.empty:
        token_summary = successful_df.groupby('Vendor').agg({
            'Input Tokens': ['mean', 'sum'],
            'Cached Input Tokens': ['mean', 'sum'],
            'Output Tokens': ['mean', 'sum']
        }).round(1)
        print(token_summary)
    
    # Sample outputs
    print("\nSample outputs (first trial):")
    first_trial = df[df['Run Number'] == 1]
    for _, row in first_trial.iterrows():
        output_preview = row['Output'][:100] + "..." if len(str(row['Output'])) > 100 else row['Output']
        cost_info = f" (${row['Cost (USD)']:.6f})" if pd.notna(row['Cost (USD)']) else " (failed)"
        print(f"  {row['Vendor']}: {output_preview}{cost_info}")


def main():
    """Main function with command line argument support."""
    parser = argparse.ArgumentParser(
        description="Compare token usage across multiple LLM providers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py
    python main.py --prompt "Explain quantum computing in one sentence"
    python main.py --trials 5 --output "quantum_test.csv"
    python main.py --prompt "Hello" --system "Be concise" --trials 1
    python main.py --enhanced --validate-only
        """
    )
    
    parser.add_argument(
        '--prompt', '-p',
        default=None,
        help=f'User prompt (default: "{DEFAULT_USER_PROMPT}")'
    )
    
    parser.add_argument(
        '--system', '-s', 
        default=None,
        help=f'System prompt (default: "{DEFAULT_SYSTEM_PROMPT}")'
        )
    
    parser.add_argument(
        '--trials', '-t',
        type=int,
        default=DEFAULT_NUM_TRIALS,
        help=f'Number of trials (default: {DEFAULT_NUM_TRIALS})'
    )
    
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Output CSV file (default: auto-generated in outputs/ folder)'
    )
    
    parser.add_argument(
        '--vendors', '-v',
        default=None,
        help='Comma-separated list of vendors to run (e.g., openai,gemini,anthropic,grok). Default: all.'
    )
    
    parser.add_argument(
        '--enhanced', 
        action='store_true',
        help='Use enhanced features (rate limiting, retry logic, advanced analytics)'
    )
    
    parser.add_argument(
        '--validate-only', 
        action='store_true',
        help='Only validate API keys and exit'
    )
    
    args = parser.parse_args()
    
    # Handle enhanced features
    if args.enhanced or args.validate_only:
        try:
            from config.validation import print_validation_report
            if args.validate_only:
                print_validation_report()
                return 0
            elif args.enhanced:
                print("🚀 Enhanced mode enabled - using advanced features")
                # Use enhanced features with the main runner
                from utils.rate_limiter import RateLimiter
                from utils.retry import retry_with_backoff
                from pathlib import Path
                Path("outputs").mkdir(exist_ok=True)
                
                # Enhanced mode uses the same runner but with additional features
                user_prompt = args.prompt if args.prompt is not None else DEFAULT_USER_PROMPT
                system_prompt = args.system if args.system is not None else DEFAULT_SYSTEM_PROMPT
                output_file = (args.output if args.output is not None 
                              else get_timestamped_filename(base_name="api_raw_enhanced"))
                vendors = [v.strip().lower() for v in args.vendors.split(',')] if args.vendors else None
                
                print("Enhanced features: rate limiting, retry logic, advanced analytics enabled")
                
                df = run_experiments(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    num_trials=args.trials,
                    vendors=vendors
                )
                
                if not df.empty:
                    save_results_to_csv(df, output_file)
                    
                    # Generate enhanced analytics
                    try:
                        from analytics.analyzer import ExperimentAnalyzer
                        analyzer = ExperimentAnalyzer(df)
                        analyzer.generate_cost_comparison_chart()
                        analyzer.generate_comprehensive_report()
                        print("📊 Enhanced analytics generated")
                    except Exception as e:
                        print(f"⚠️  Enhanced analytics unavailable: {e}")
                    
                    print(f"\n🎉 Enhanced experiment completed! Results: {output_file}")
                return 0
                
        except ImportError as e:
            print(f"Enhanced features not available: {e}")
            print("Install requirements: pip install rich matplotlib seaborn")
            if args.validate_only:
                return 1
    
    # Use defaults from config if not specified
    user_prompt = args.prompt if args.prompt is not None else DEFAULT_USER_PROMPT
    system_prompt = args.system if args.system is not None else DEFAULT_SYSTEM_PROMPT
    
    # Generate timestamped filename in outputs/ if no output specified
    output_file = (args.output if args.output is not None 
                   else get_timestamped_filename(base_name="api_raw"))
    # Also generate a log file for failed calls
    log_failed_path = output_file.replace('.csv', '_failed.log')
    # Generate summary file name
    summary_file = output_file.replace('api_raw', 'experiment_summary').replace('.csv', '.txt')
    
    # Parse vendors argument
    vendors = [v.strip().lower() for v in args.vendors.split(',')] if args.vendors else None
    
    print(f"Running token counter experiment...")
    print(f"User prompt: {user_prompt}")
    print(f"System prompt: {system_prompt}")
    print(f"Trials: {args.trials}")
    print(f"Output file: {output_file}")
    print()

    try:
        # Run the experiment
        df = run_experiments(
            prompt=user_prompt,
            system_prompt=system_prompt,
            num_trials=args.trials,
            vendors=vendors
        )
        # Save raw results
        save_results_to_csv(df, output_file)
        # Save experiment summary to a separate file
        save_experiment_summary(df, summary_file)
        # Display summary and log failed calls
        display_summary(df, log_failed_path=log_failed_path)
        print(f"\nExperiment completed successfully!")
    except Exception as e:
        print(f"Error running experiments: {str(e)}")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
