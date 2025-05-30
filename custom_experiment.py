"""
Custom experiment runner - allows easy customization of prompts and settings.

This script allows you to run experiments with custom prompts and settings
without modifying the main configuration files.
"""

from main import run_experiments, save_results_to_csv, display_summary


def run_custom_experiment():
    """
    Run a custom experiment with user-defined settings.
    Modify the variables below to customize your experiment.
    """
      # =========================================================================
    # CUSTOMIZE YOUR EXPERIMENT HERE
    # =========================================================================
    
    # OPTION 1: Use default prompts from config.py (recommended for global changes)
    # To change prompts for ALL scripts, edit the DEFAULT_USER_PROMPT and 
    # DEFAULT_SYSTEM_PROMPT in config.py
    
    # OPTION 2: Override prompts just for this experiment
    # User prompt - the main instruction for the LLMs
    user_prompt = "Give me the word 'hello'"  # Set to None to use config default
    
    # System prompt - additional context or instructions (can be empty)
    system_prompt = ""  # Set to None to use config default
    
    # Number of trials to run (each trial tests all 4 LLMs)
    num_trials = 3
    
    # Custom output file name (optional - will use default if None)
    custom_output_file = None  # e.g., "my_custom_results.csv"
    
    # =========================================================================
    # END CUSTOMIZATION
    # =========================================================================
      print("Running custom token counter experiment...")
    
    # If prompts are set to None, they will use the defaults from config.py
    
    try:
        # Run the experiment
        df = run_experiments(
            prompt=user_prompt,
            system_prompt=system_prompt,
            num_trials=num_trials
        )
        
        # Save results
        save_results_to_csv(df, custom_output_file)
        
        # Display summary
        display_summary(df)
        
        print("\nCustom experiment completed successfully!")
        
    except Exception as e:
        print(f"Error running custom experiment: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(run_custom_experiment())
