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


def run_single_trial(prompt, system_prompt, trial_number):
    """
    Run a single trial across all LLM providers.
    
    Args:
        prompt (str): The user prompt
        system_prompt (str): The system prompt
        trial_number (int): The trial number
    
    Returns:
        list: List of result dictionaries
    """
    results = []
    
    # Test OpenAI
    try:
        output, in_tok, out_tok = process_with_openai(prompt, system_prompt)
        results.append({
            'Run Number': trial_number,
            'Vendor': 'OpenAI',
            'Model': get_openai_model(),
            'User Prompt': prompt,
            'System Prompt': system_prompt,
            'Output': output,
            'Input Tokens': in_tok,
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
            'Output Tokens': None
        })
    
    # Test Gemini
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
            'Output Tokens': None
        })
    
    # Test Anthropic
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
            'Output Tokens': None
        })
    
    # Test Grok
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
            'Output Tokens': None
        })
    
    return results


def run_experiments(prompt=None, system_prompt=None, num_trials=None):
    """
    Run the complete experiment across all LLM providers.
    
    Args:
        prompt (str): User prompt (defaults to config setting)
        system_prompt (str): System prompt (defaults to config setting)
        num_trials (int): Number of trials to run (defaults to config setting)
    
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
    
    print(f"Starting token counter experiment:")
    print(f"  User prompt: '{prompt}'")
    print(f"  System prompt: '{system_prompt}'")
    print(f"  Number of trials: {num_trials}")
    print(f"  Testing: OpenAI, Gemini, Anthropic, Grok")
    print()
    
    all_results = []
    
    # Run trials
    for trial in range(1, num_trials + 1):
        print(f"Running trial {trial}/{num_trials}...")
        trial_results = run_single_trial(prompt, system_prompt, trial)
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
    print(f"Results saved to {output_path}")


def display_summary(df):
    """
    Display a summary of the results.
    
    Args:
        df (pandas.DataFrame): Results dataframe
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
    
    # Token summary by vendor
    print("\nToken usage by vendor:")
    token_summary = df.groupby('Vendor').agg({
        'Input Tokens': ['mean', 'sum'],
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
        help='Output CSV file (default: auto-generated with timestamp)'
    )
    
    args = parser.parse_args()
    
    # Use defaults from config if not specified
    user_prompt = args.prompt if args.prompt is not None else DEFAULT_USER_PROMPT
    system_prompt = args.system if args.system is not None else DEFAULT_SYSTEM_PROMPT
    
    # Generate timestamped filename if no output specified
    output_file = args.output if args.output is not None else get_timestamped_filename()
    
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
            num_trials=args.trials
        )
          # Save results
        save_results_to_csv(df, output_file)
        
        # Display summary
        display_summary(df)
        
        print(f"\nExperiment completed successfully!")
        
    except Exception as e:
        print(f"Error running experiments: {str(e)}")
        return 1
    
    return 0
    
    return 0


if __name__ == "__main__":
    exit(main())
