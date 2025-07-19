"""
Enhanced main script with improved architecture and features.

This script uses the new client architecture with better error handling,
rate limiting, and comprehensive analytics.
"""

import pandas as pd
import argparse
import time
from pathlib import Path
from typing import List, Optional

from config import (
    DEFAULT_USER_PROMPT, DEFAULT_SYSTEM_PROMPT, DEFAULT_NUM_TRIALS,
    CSV_OUTPUT_PATH, CSV_COLUMNS, get_timestamped_filename
)
from config.validation import validate_api_keys, print_validation_report, get_valid_providers
from client_factory import ClientFactory
from utils.rate_limiter import RateLimiter
from utils.retry import retry_with_backoff
from analytics.analyzer import ExperimentAnalyzer


class EnhancedExperimentRunner:
    """Enhanced experiment runner with improved architecture"""
    
    def __init__(self, use_rate_limiting: bool = True, use_retry: bool = True):
        """
        Initialize the experiment runner.
        
        Args:
            use_rate_limiting: Whether to use rate limiting
            use_retry: Whether to use retry logic
        """
        self.rate_limiter = RateLimiter() if use_rate_limiting else None
        self.use_retry = use_retry
        self.results = []
    
    @retry_with_backoff(max_retries=2, base_delay=1.0)
    def _call_provider_with_retry(self, provider: str, prompt: str, system_prompt: str, trial_number: int):
        """Make API call with retry logic"""
        if self.rate_limiter:
            self.rate_limiter.wait_if_needed(provider)
        
        client = ClientFactory.get_client(provider)
        if not client:
            raise ValueError(f"Unknown provider: {provider}")
        
        response = client.process(prompt, system_prompt)
        
        return {
            'Run Number': trial_number,
            'Vendor': provider.capitalize(),
            'Model': response.model,
            'User Prompt': prompt,
            'System Prompt': system_prompt,
            'Output': response.output,
            'Input Tokens': response.usage.input_tokens,
            'Cached Input Tokens': response.usage.cached_input_tokens,
            'Output Tokens': response.usage.output_tokens,
            'Input Token Cost (USD)': round(response.cost - 
                (response.usage.cached_input_tokens * client.get_model_info()['cached_input_cost_per_million'] / 1_000_000) -
                (response.usage.output_tokens * client.get_model_info()['output_cost_per_million'] / 1_000_000), 6),
            'Cached Token Cost (USD)': round(
                response.usage.cached_input_tokens * client.get_model_info()['cached_input_cost_per_million'] / 1_000_000, 6),
            'Output Token Cost (USD)': round(
                response.usage.output_tokens * client.get_model_info()['output_cost_per_million'] / 1_000_000, 6),
            'Cost (USD)': response.cost
        }
    
    def run_single_trial(self, prompt: str, system_prompt: str, trial_number: int, vendors: List[str]) -> List[dict]:
        """Run a single trial across selected providers"""
        trial_results = []
        
        for vendor in vendors:
            try:
                if self.use_retry:
                    result = self._call_provider_with_retry(vendor, prompt, system_prompt, trial_number)
                else:
                    if self.rate_limiter:
                        self.rate_limiter.wait_if_needed(vendor)
                    
                    client = ClientFactory.get_client(vendor)
                    response = client.process(prompt, system_prompt)
                    
                    result = {
                        'Run Number': trial_number,
                        'Vendor': vendor.capitalize(),
                        'Model': response.model,
                        'User Prompt': prompt,
                        'System Prompt': system_prompt,
                        'Output': response.output,
                        'Input Tokens': response.usage.input_tokens,
                        'Cached Input Tokens': response.usage.cached_input_tokens,
                        'Output Tokens': response.usage.output_tokens,
                        'Input Token Cost (USD)': round(response.cost - 
                            (response.usage.cached_input_tokens * client.get_model_info()['cached_input_cost_per_million'] / 1_000_000) -
                            (response.usage.output_tokens * client.get_model_info()['output_cost_per_million'] / 1_000_000), 6),
                        'Cached Token Cost (USD)': round(
                            response.usage.cached_input_tokens * client.get_model_info()['cached_input_cost_per_million'] / 1_000_000, 6),
                        'Output Token Cost (USD)': round(
                            response.usage.output_tokens * client.get_model_info()['output_cost_per_million'] / 1_000_000, 6),
                        'Cost (USD)': response.cost
                    }
                
                trial_results.append(result)
                print(f"  ✅ {vendor.capitalize()}: {len(response.output)} chars, ${result['Cost (USD)']:.6f}")
                
            except Exception as e:
                error_result = {
                    'Run Number': trial_number,
                    'Vendor': vendor.capitalize(),
                    'Model': 'Unknown',
                    'User Prompt': prompt,
                    'System Prompt': system_prompt,
                    'Output': f"Error: {str(e)}",
                    'Input Tokens': None,
                    'Cached Input Tokens': 0,
                    'Output Tokens': None,
                    'Input Token Cost (USD)': None,
                    'Cached Token Cost (USD)': None,
                    'Output Token Cost (USD)': None,
                    'Cost (USD)': None
                }
                trial_results.append(error_result)
                print(f"  ❌ {vendor.capitalize()}: {str(e)}")
        
        return trial_results
    
    def run_experiments(self, prompt: str = None, system_prompt: str = None, 
                       num_trials: int = None, vendors: List[str] = None) -> pd.DataFrame:
        """Run the complete experiment with enhanced features"""
        
        # Use defaults if not provided
        if prompt is None:
            prompt = DEFAULT_USER_PROMPT
        if system_prompt is None:
            system_prompt = DEFAULT_SYSTEM_PROMPT
        if num_trials is None:
            num_trials = DEFAULT_NUM_TRIALS
        if vendors is None:
            vendors = ClientFactory.get_available_providers()
        
        # Validate providers
        valid_vendors = ClientFactory.validate_providers(vendors)
        if not valid_vendors:
            raise ValueError(f"No valid providers found in: {vendors}")
        
        # Check API keys
        api_validation = validate_api_keys()
        available_vendors = [v for v in valid_vendors if api_validation.get(v, False)]
        
        if not available_vendors:
            print("⚠️  No providers with valid API keys found!")
            print_validation_report()
            return pd.DataFrame()
        
        print(f"🚀 Starting enhanced token counter experiment:")
        print(f"   User prompt: '{prompt}'")
        print(f"   System prompt: '{system_prompt}'")
        print(f"   Number of trials: {num_trials}")
        print(f"   Testing providers: {', '.join(available_vendors)}")
        print(f"   Rate limiting: {'✅' if self.rate_limiter else '❌'}")
        print(f"   Retry logic: {'✅' if self.use_retry else '❌'}")
        print()
        
        start_time = time.time()
        all_results = []
        
        # Run trials
        for trial in range(1, num_trials + 1):
            print(f"🔄 Running trial {trial}/{num_trials}...")
            trial_results = self.run_single_trial(prompt, system_prompt, trial, available_vendors)
            all_results.extend(trial_results)
            
            if trial < num_trials:
                print()  # Add spacing between trials
        
        duration = time.time() - start_time
        
        # Create DataFrame
        df = pd.DataFrame(all_results, columns=CSV_COLUMNS)
        
        print(f"\n✅ Completed {num_trials} trials with {len(df)} total API calls in {duration:.1f}s")
        return df


def save_results_with_analysis(df: pd.DataFrame, output_path: str):
    """Save results and generate comprehensive analysis"""
    # Save raw CSV
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"📊 Raw data saved to {output_path}")
    
    # Generate analysis
    if not df.empty:
        analyzer = ExperimentAnalyzer(df)
        
        # Generate visualizations
        try:
            analyzer.generate_cost_comparison_chart()
        except Exception as e:
            print(f"⚠️  Could not generate charts: {e}")
        
        # Generate comprehensive report
        try:
            analyzer.generate_comprehensive_report()
        except Exception as e:
            print(f"⚠️  Could not generate comprehensive report: {e}")


def main():
    """Enhanced main function with comprehensive features"""
    parser = argparse.ArgumentParser(
        description="Enhanced Token Counter - Compare LLM providers with advanced analytics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main_enhanced.py
    python main_enhanced.py --prompt "Explain quantum computing" --trials 5
    python main_enhanced.py --vendors openai,gemini --no-retry
    python main_enhanced.py --validate-only
        """
    )
    
    parser.add_argument('--prompt', '-p', default=None, help='User prompt')
    parser.add_argument('--system', '-s', default=None, help='System prompt')
    parser.add_argument('--trials', '-t', type=int, default=DEFAULT_NUM_TRIALS, help='Number of trials')
    parser.add_argument('--output', '-o', default=None, help='Output CSV file')
    parser.add_argument('--vendors', '-v', default=None, help='Comma-separated list of vendors')
    parser.add_argument('--no-rate-limit', action='store_true', help='Disable rate limiting')
    parser.add_argument('--no-retry', action='store_true', help='Disable retry logic')
    parser.add_argument('--validate-only', action='store_true', help='Only validate API keys and exit')
    
    args = parser.parse_args()
    
    # Validate API keys if requested
    if args.validate_only:
        print_validation_report()
        return 0
    
    # Parse arguments
    user_prompt = args.prompt if args.prompt is not None else DEFAULT_USER_PROMPT
    system_prompt = args.system if args.system is not None else DEFAULT_SYSTEM_PROMPT
    output_file = args.output if args.output is not None else get_timestamped_filename(base_name="api_raw_enhanced")
    vendors = [v.strip().lower() for v in args.vendors.split(',')] if args.vendors else None
    
    # Create output directory
    Path("outputs").mkdir(exist_ok=True)
    
    try:
        # Initialize runner
        runner = EnhancedExperimentRunner(
            use_rate_limiting=not args.no_rate_limit,
            use_retry=not args.no_retry
        )
        
        # Run experiments
        df = runner.run_experiments(
            prompt=user_prompt,
            system_prompt=system_prompt,
            num_trials=args.trials,
            vendors=vendors
        )
        
        if df.empty:
            print("❌ No results to save")
            return 1
        
        # Save results with analysis
        save_results_with_analysis(df, output_file)
        
        # Generate summary files
        summary_file = output_file.replace('api_raw_enhanced', 'experiment_summary_enhanced').replace('.csv', '.txt')
        failed_log = output_file.replace('.csv', '_failed.log')
        
        # Save experiment summary
        from main import save_experiment_summary, display_summary
        save_experiment_summary(df, summary_file)
        display_summary(df, log_failed_path=failed_log)
        
        print(f"\n🎉 Enhanced experiment completed successfully!")
        print(f"📁 Files generated:")
        print(f"   • Raw data: {output_file}")
        print(f"   • Summary: {summary_file}")
        print(f"   • Analysis: outputs/comprehensive_analysis.txt")
        print(f"   • Charts: outputs/cost_comparison.png")
        
    except Exception as e:
        print(f"❌ Error running enhanced experiments: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())