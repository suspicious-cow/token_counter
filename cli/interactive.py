"""
Interactive CLI for building and running experiments.
"""

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from typing import List

from client_factory import ClientFactory
from config.validation import validate_api_keys, print_validation_report


console = Console()


def display_welcome():
    """Display welcome message"""
    welcome_text = """
[bold blue]🚀 Token Counter - Interactive Mode[/bold blue]

This interactive mode will guide you through setting up and running
a token counting experiment across multiple LLM providers.
    """
    console.print(Panel(welcome_text, title="Welcome", border_style="blue"))


def select_vendors() -> List[str]:
    """Interactive vendor selection"""
    console.print("\n[bold]Available Providers:[/bold]")
    
    # Check API key validation
    api_validation = validate_api_keys()
    available_providers = ClientFactory.get_available_providers()
    
    table = Table()
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Model")
    
    from config import MODELS_INFO
    
    valid_providers = []
    for provider in available_providers:
        is_valid = api_validation.get(provider, False)
        status = "✅ Ready" if is_valid else "❌ No API Key"
        model = MODELS_INFO[provider]['model']
        
        table.add_row(provider.capitalize(), status, model)
        if is_valid:
            valid_providers.append(provider)
    
    console.print(table)
    
    if not valid_providers:
        console.print("\n[red]❌ No providers with valid API keys found![/red]")
        console.print("Please set your environment variables and try again.")
        return []
    
    # Let user select providers
    console.print(f"\n[green]Valid providers: {', '.join(valid_providers)}[/green]")
    
    if Confirm.ask("Use all valid providers?", default=True):
        return valid_providers
    
    selected = []
    for provider in valid_providers:
        if Confirm.ask(f"Include {provider.capitalize()}?", default=True):
            selected.append(provider)
    
    return selected


def get_experiment_config():
    """Get experiment configuration from user"""
    console.print("\n[bold]Experiment Configuration:[/bold]")
    
    # Get prompts
    prompt = Prompt.ask(
        "Enter your user prompt",
        default="Give me the word 'halt' without any formatting or additional text."
    )
    
    system_prompt = Prompt.ask(
        "Enter system prompt (optional)",
        default=""
    )
    
    # Get number of trials
    trials = int(Prompt.ask(
        "Number of trials per provider",
        default="3"
    ))
    
    # Get vendors
    vendors = select_vendors()
    
    if not vendors:
        return None
    
    return {
        'prompt': prompt,
        'system_prompt': system_prompt,
        'trials': trials,
        'vendors': vendors
    }


def display_experiment_summary(config):
    """Display experiment summary before running"""
    console.print("\n[bold]Experiment Summary:[/bold]")
    
    summary_table = Table()
    summary_table.add_column("Setting", style="cyan")
    summary_table.add_column("Value", style="white")
    
    summary_table.add_row("User Prompt", config['prompt'][:50] + "..." if len(config['prompt']) > 50 else config['prompt'])
    summary_table.add_row("System Prompt", config['system_prompt'] if config['system_prompt'] else "(none)")
    summary_table.add_row("Trials", str(config['trials']))
    summary_table.add_row("Providers", ", ".join([v.capitalize() for v in config['vendors']]))
    summary_table.add_row("Total API Calls", str(config['trials'] * len(config['vendors'])))
    
    console.print(summary_table)


def run_interactive_mode():
    """Main interactive mode function"""
    display_welcome()
    
    # Check if user wants to validate API keys first
    if Confirm.ask("\nValidate API keys first?", default=True):
        print_validation_report()
        console.print()
    
    # Get experiment configuration
    config = get_experiment_config()
    if not config:
        console.print("[red]❌ Cannot proceed without valid providers[/red]")
        return None
    
    # Display summary and confirm
    display_experiment_summary(config)
    
    if not Confirm.ask("\nProceed with experiment?", default=True):
        console.print("[yellow]Experiment cancelled[/yellow]")
        return None
    
    return config


def interactive_main():
    """Entry point for interactive mode"""
    try:
        config = run_interactive_mode()
        if not config:
            return 1
        
        # Import and run the enhanced experiment
        from main_enhanced import EnhancedExperimentRunner
        from pathlib import Path
        from config import get_timestamped_filename
        
        # Create output directory
        Path("outputs").mkdir(exist_ok=True)
        
        console.print("\n[bold green]🚀 Starting experiment...[/bold green]")
        
        # Run experiment
        runner = EnhancedExperimentRunner(use_rate_limiting=True, use_retry=True)
        df = runner.run_experiments(
            prompt=config['prompt'],
            system_prompt=config['system_prompt'],
            num_trials=config['trials'],
            vendors=config['vendors']
        )
        
        if df.empty:
            console.print("[red]❌ No results generated[/red]")
            return 1
        
        # Save results
        output_file = get_timestamped_filename(base_name="api_raw_interactive")
        from main_enhanced import save_results_with_analysis
        save_results_with_analysis(df, output_file)
        
        console.print(f"\n[bold green]✅ Experiment completed![/bold green]")
        console.print(f"Results saved to: {output_file}")
        
        return 0
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Experiment interrupted by user[/yellow]")
        return 1
    except Exception as e:
        console.print(f"\n[red]❌ Error: {str(e)}[/red]")
        return 1


if __name__ == "__main__":
    exit(interactive_main())