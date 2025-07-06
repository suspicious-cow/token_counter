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
    CSV_OUTPUT_PATH, CSV_COLUMNS, get_timestamped_filename
)
from openai_client import process_with_openai, get_model_name as get_openai_model
from gemini_client import process_with_gemini, get_model_name as get_gemini_model
from anthropic_client import process_with_anthropic, get_model_name as get_anthropic_model
from grok_client import process_with_grok, get_model_name as get_grok_model


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
            results.append({
                'Run Number': trial_number,
                'Vendor': 'OpenAI',
                'Model': get_openai_model(),
                'User Prompt': prompt,
                'System Prompt': system_prompt,
                'Output': output,
                'Input Tokens': in_tok,
                'Cached Input Tokens': int(cached_in_tok) if cached_in_tok is not None else 0,
                'Output Tokens': out_tok
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
                'Output Tokens': None
            })
    if 'gemini' in vendors:
        try:
            output, in_tok, out_tok = process_with_gemini(prompt, system_prompt)
            results.append({
                'Run Number': trial_number,
                'Vendor': 'Gemini',
                'Model': get_gemini_model(),
                'User Prompt': prompt,
                'System Prompt': system_prompt,
                'Output': output,
                'Input Tokens': in_tok,
                'Cached Input Tokens': 0,
                'Output Tokens': out_tok
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
                'Output Tokens': None
            })
    if 'anthropic' in vendors:
        try:
            output, in_tok, out_tok = process_with_anthropic(prompt, system_prompt)
            results.append({
                'Run Number': trial_number,
                'Vendor': 'Anthropic',
                'Model': get_anthropic_model(),
                'User Prompt': prompt,
                'System Prompt': system_prompt,
                'Output': output,
                'Input Tokens': in_tok,
                'Cached Input Tokens': 0,
                'Output Tokens': out_tok
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
                'Output Tokens': None
            })
    if 'grok' in vendors:
        try:
            output, in_tok, out_tok = process_with_grok(prompt, system_prompt)
            results.append({
                'Run Number': trial_number,
                'Vendor': 'Grok',
                'Model': get_grok_model(),
                'User Prompt': prompt,
                'System Prompt': system_prompt,
                'Output': output,
                'Input Tokens': in_tok,
                'Cached Input Tokens': 0,
                'Output Tokens': out_tok
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
                'Output Tokens': None
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
    
    # Run trials
    for trial in range(1, num_trials + 1):
        print(f"Running trial {trial}/{num_trials}...")
        trial_results = run_single_trial(prompt, system_prompt, trial, vendors=vendors)
        all_results.extend(trial_results)
    
    # Create DataFrame
    df = pd.DataFrame(all_results, columns=CSV_COLUMNS)
    
    print(f"\nCompleted {num_trials} trials with {len(df)} total API calls.")
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
    successful_calls = len(df[~df['Output'].str.contains('error', case=False, na=False)])
    failed_calls = total_calls - successful_calls
    
    print(f"Total API calls: {total_calls}")
    print(f"Successful calls: {successful_calls}")
    print(f"Failed calls: {failed_calls}")
    
    # Failed calls by vendor
    failed = df[df['Output'].str.contains('error', case=False, na=False)]
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
    
    # Token summary by vendor
    print("\nToken usage by vendor:")
    token_summary = df.groupby('Vendor').agg({
        'Input Tokens': ['mean', 'sum'],
        'Cached Input Tokens': ['mean', 'sum'],
        'Output Tokens': ['mean', 'sum']
    }).round(2)
    print(token_summary)
    
    # Sample outputs
    print("\nSample outputs (first trial):")
    first_trial = df[df['Run Number'] == 1]
    for _, row in first_trial.iterrows():
        output_preview = row['Output'][:100] + "..." if len(str(row['Output'])) > 100 else row['Output']
        print(f"  {row['Vendor']}: {output_preview}")


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
    
    args = parser.parse_args()
    
    # Use defaults from config if not specified
    user_prompt = args.prompt if args.prompt is not None else DEFAULT_USER_PROMPT
    system_prompt = args.system if args.system is not None else DEFAULT_SYSTEM_PROMPT
    
    # Generate timestamped filename in outputs/ if no output specified
    output_file = args.output if args.output is not None else get_timestamped_filename(base_name="api_raw")
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
