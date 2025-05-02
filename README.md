# LLM Token Counter Notebook

This project provides a Jupyter Notebook (`token_counter_notebook.ipynb`) designed to compare the outputs and **native token counts** from multiple Large Language Models (LLMs) for a given user prompt and system prompt.

## Features

- **Multi-LLM Comparison:** Sends the same prompt to OpenAI (GPT-4o), Google Gemini (Gemini 2.0 Flash), Anthropic (Claude 3.7 Sonnet), and Grok (Grok 3 Beta).
- **Native Token Counts:** Retrieves and displays the **official input and output token counts** directly from each LLM's API response. No manual tokenization or estimation is used, ensuring accuracy based on the specific model's internal counting method.
- **System Prompt Support:** Allows setting a common system prompt (or leaving it blank) that is correctly formatted and sent to each supported LLM.
- **Clear Output:** Displays results in a pandas DataFrame for easy comparison and also saves the detailed output (including token counts) to a text file (`api_results.txt`).

## Setup

1. **Clone the repository or download the files.**
2. **Install Dependencies:** Create a virtual environment and install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
3. **API Keys:** Set your API keys for OpenAI, Gemini, Anthropic, and Grok either as environment variables (`OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `GROK_API_KEY`) or directly in the notebook (Cell 2).

## Usage

1. Open `token_counter_notebook.ipynb` in Jupyter Lab or a compatible environment.
2. **Set Prompts:** Modify the `prompt` (user prompt) and `system_prompt` variables in Cell 3.
3. **Run All Cells:** Execute the notebook cells sequentially.
4. **View Results:** The comparison DataFrame will be displayed in the output of Cell 8, and the detailed text output will be saved to `api_results.txt`.

## Token Counting Emphasis

This notebook prioritizes accuracy in token reporting. It accesses the `usage` or `usage_metadata` fields provided in the API responses from OpenAI, Gemini, Anthropic, and Grok to ensure the reported token counts reflect the actual values billed or tracked by the respective service providers.
