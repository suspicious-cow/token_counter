#!/usr/bin/env python3
"""
Demo script showcasing the Token Counter features.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def demo_api_validation():
    """Demo API key validation"""
    console.print(Panel("[bold blue]🔑 API Key Validation Demo[/bold blue]", border_style="blue"))
    
    try:
        from config.validation import print_validation_report
        print_validation_report()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def demo_client_factory():
    """Demo client factory pattern"""
    console.print(Panel("[bold green]🏭 Client Factory Demo[/bold green]", border_style="green"))
    
    try:
        from client_factory import ClientFactory
        
        # Show available providers
        providers = ClientFactory.get_available_providers()
        console.print(f"Available providers: {', '.join(providers)}")
        
        # Validate providers
        test_providers = ['openai', 'gemini', 'invalid', 'anthropic']
        valid = ClientFactory.validate_providers(test_providers)
        console.print(f"Valid from {test_providers}: {valid}")
        
        # Try to get a client
        client = ClientFactory.get_client('openai')
        if client:
            console.print(f"✅ Successfully created OpenAI client: {type(client).__name__}")
        else:
            console.print("❌ Could not create OpenAI client")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def demo_rate_limiter():
    """Demo rate limiting"""
    console.print(Panel("[bold yellow]⏱️ Rate Limiter Demo[/bold yellow]", border_style="yellow"))
    
    try:
        from utils.rate_limiter import RateLimiter
        import time
        
        limiter = RateLimiter()
        
        console.print("Testing rate limiting (this will take a few seconds)...")
        
        start_time = time.time()
        for i in range(3):
            console.print(f"Call {i+1} to OpenAI...")
            limiter.wait_if_needed('openai')
        
        elapsed = time.time() - start_time
        console.print(f"✅ Completed 3 calls in {elapsed:.2f} seconds (with rate limiting)")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def demo_analytics():
    """Demo analytics capabilities"""
    console.print(Panel("[bold magenta]📊 Analytics Demo[/bold magenta]", border_style="magenta"))
    
    try:
        import pandas as pd
        from analytics.analyzer import ExperimentAnalyzer
        
        # Create sample data
        sample_data = [
            {'Vendor': 'OpenAI', 'Cost (USD)': 0.001, 'Input Tokens': 100, 'Output Tokens': 50, 'Output': 'Hello world'},
            {'Vendor': 'Gemini', 'Cost (USD)': 0.0005, 'Input Tokens': 100, 'Output Tokens': 50, 'Output': 'Hello world'},
            {'Vendor': 'Anthropic', 'Cost (USD)': 0.002, 'Input Tokens': 100, 'Output Tokens': 50, 'Output': 'Hello world'},
        ]
        
        df = pd.DataFrame(sample_data)
        analyzer = ExperimentAnalyzer(df)
        
        # Calculate efficiency
        efficiency = analyzer.generate_token_efficiency_report()
        
        console.print("Token Efficiency (tokens per dollar):")
        for provider, eff in efficiency.items():
            console.print(f"  {provider}: {eff:,.0f} tokens/$")
        
        # Success rates
        success_rates = analyzer.calculate_success_rates()
        console.print("\nSuccess Rates:")
        for provider, rate in success_rates.items():
            console.print(f"  {provider}: {rate:.1f}%")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def main():
    """Run all demos"""
    console.print(Panel(
        "[bold cyan]🚀 Token Counter - Feature Demo[/bold cyan]\n\n"
        "This demo showcases the enhanced features without making actual API calls.",
        title="Welcome",
        border_style="cyan"
    ))
    
    console.print()
    demo_api_validation()
    
    console.print()
    demo_client_factory()
    
    console.print()
    demo_rate_limiter()
    
    console.print()
    demo_analytics()
    
    console.print()
    console.print(Panel(
        "[bold green]✅ Demo completed![/bold green]\n\n"
        "To run actual experiments:\n"
        "• [cyan]python main.py --validate-only[/cyan] - Check API keys\n"
        "• [cyan]python cli/interactive.py[/cyan] - Interactive mode\n"
        "• [cyan]python main.py --prompt 'Hello' --enhanced[/cyan] - Enhanced features",
        title="Next Steps",
        border_style="green"
    ))


if __name__ == "__main__":
    main()