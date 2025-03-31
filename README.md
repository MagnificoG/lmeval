# Python LLM Evaluation Pipeline

This project provides a Python framework for evaluating Large Language Models (LLMs) using tasks defined in an Excel spreadsheet. It leverages `asyncio` for concurrent API calls to multiple OpenAI-compatible LLM providers, parses complex input formats, evaluates responses against various ground truth types, and stores detailed results persistently in JSON format with checkpointing for resumption.

## Key Features

*   **Flexible Input:** Reads evaluation tasks directly from an Excel file (`.xlsx`).
*   **Robust Data Parsing:** Handles complex string representations for multiple-choice options (dictionaries) and ground truth answers (lists, booleans, strings, numbers).
*   **Concurrent Multi-Provider Evaluation:** Uses `asyncio` to efficiently query multiple OpenAI-compatible LLM APIs (like DeepSeek, Qwen) in parallel for each task.
*   **Versatile Evaluation Logic:** Compares LLM responses against ground truth, supporting:
    *   Single-choice answers (string comparison)
    *   Multiple-choice answers with multiple correct options (list comparison, order-insensitive)
    *   Boolean answers (True/False)
    *   Numeric answers (with tolerance)
*   **Persistent JSON Results:** Saves detailed evaluation results (including task data, LLM response, ground truth, and correctness) to a structured JSON file.
*   **Progress Tracking & Resumption:**
    *   Displays a progress bar (`tqdm`) during evaluation.
    *   Implements checkpointing, saving progress periodically to the JSON file.
    *   Automatically resumes evaluation from the last completed task/provider combination if the script is interrupted and restarted.
*   **Configurable Concurrency:** Allows setting a limit on the number of concurrent API requests to manage rate limits.
*   **Provider Management:** Uses a class (`LLMProvider`) to easily configure and manage different LLM services and models.

## Requirements

*   Python 3.8+
*   Libraries:
    *   `pandas`
    *   `openai` (>= 1.0 for async client)
    *   `tqdm`
    *   `openpyxl` (for reading `.xlsx` files with pandas)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/MagnificoG/lmeval.git
    cd ./lmeval
    ```
2.  **Install dependencies and run:**
    - The traditional way
    Create a `requirements.txt` file with the following content:
    ```txt
    pandas>=1.3
    openai>=1.0
    tqdm>=4.60
    openpyxl>=3.0
    ```
    Then run:
    ```bash
    pip install -r requirements.txt
    ```
    - With `uv` (recommended)
    Alternatively, you can use `uv` to manage dependencies which is more convenient. If you have `uv` installed, run:
    ```bash
    uv run main.py
    ```

## Configuration

1.  **API Keys:**
    *   The script expects API keys to be available as environment variables. Set them in your shell before running:
        ```bash
        export QWEN_API_KEY="your_qwen_key_here"
        export DEEPSEEK_API_KEY="your_deepseek_key_here"
        # Add other keys as needed
        ```
    *   Alternatively, you can hardcode the keys directly when creating `LLMProvider` instances in the `if __name__ == "__main__":` block (not recommended for security).

2.  **LLM Providers:**
    *   Configure the LLM providers you want to evaluate in the `if __name__ == "__main__":` block of the main script (`evaluation_script.py` or similar name).
    *   Modify or add `LLMProvider` instances, specifying `provider_name`, `model_name`, `api_key` (retrieved from env vars ideally), and `base_url` if needed (for non-OpenAI endpoints).
        ```python
        # Example from main block:
        providers_to_run = []
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        qwen_api_key = os.getenv("QWEN_API_KEY")

        if deepseek_api_key:
             providers_to_run.append(LLMProvider(provider_name="DeepSeek",
                                                model_name="deepseek-chat",
                                                api_key=deepseek_api_key,
                                                base_url="https://api.deepseek.com"))
        # Add more providers...

        if not providers_to_run:
            logging.error("No LLM providers configured...")
            exit()
        ```

3.  **Input Excel File:**
    *   Prepare your evaluation tasks in an `.xlsx` file. By default, the script looks for `llm_eval_tasks_async.xlsx` (or similar, check the `DataLoader` instantiation in the main block).
    *   Ensure the file follows the format described in the **Input Format** section below. Place the file in the same directory as the script or provide the correct path.

4.  **Script Parameters (Optional):**
    *   You can modify parameters like the output JSON filename, checkpoint interval, and concurrency limit directly in the `EvaluationRunner` instantiation within the `if __name__ == "__main__":` block.
        ```python
        results_output_file = "my_evaluation_results.json"
        save_interval = 10 # Save every 10 completed task/provider pairs
        max_concurrent_requests = 5 # Limit concurrent API calls

        runner = EvaluationRunner(...,
                                  output_json_path=results_output_file,
                                  checkpoint_interval=save_interval,
                                  concurrency_limit=max_concurrent_requests)
        ```

## Usage

1.  Ensure your environment variables are set (API keys).
2.  Make sure your input Excel file is correctly formatted and located.
3.  Configure the desired providers in the script.
4.  Run the main Python script from your terminal:
    ```bash
    python evaluation_script.py # Replace with your script's filename
    ```

The script will:
*   Load data from the Excel file.
*   Load any previous results from the specified JSON output file (or the default generated one).
*   Identify tasks and providers that still need evaluation.
*   Run API calls concurrently using `asyncio` (respecting the concurrency limit).
*   Display a progress bar (`tqdm`).
*   Evaluate responses as they complete.
*   Save progress periodically (checkpointing) and finally to the JSON output file.
*   Print a summary of the accuracy per provider to the console.

## Input Format (Excel `.xlsx`)

The script expects the **first row** of the Excel sheet to contain headers that **exactly match** the keys used internally (which correspond to the keys in the example JSON structure shown in the original prompt).

**Required Columns:**

*   `id`: **Unique identifier** for each task (string or number). **Crucial for resumption.** Must be unique and non-empty.
*   `instruction`: Text instructions for the LLM for this specific task (e.g., "Choose the best option.", "Answer True or False.").
*   `text`: Context or background text for the task (can be empty).
*   `question`: The specific question being asked.
*   `options`: A **string** representation of a Python dictionary mapping option keys (e.g., 'A', 'B') to their text.
    *   Example string: `"{'A': 'Paris', 'B': 'London', 'C': 'Berlin'}"`
    *   Example string: `"{'True': 'The statement is correct', 'False': 'The statement is incorrect'}"`
*   `answer`: The ground truth answer(s). This should be a **string** representation that can be parsed into the correct Python type:
    *   **Multiple Correct Options:** String representation of a Python list. Example: `"['A', 'C']"`
    *   **Single Correct Option:** String representing the key. Example: `"A"`
    *   **Boolean:** String "True" or "False". Example: `"True"`
    *   **Numeric:** String representation of the number. Example: `"4"` or `"3.14"`
    *   **No Answer/Not Applicable:** Leave the cell empty or explicitly write `None`.

## Output Format (JSON)

The script outputs a single JSON file containing a list of result objects. Each object represents the evaluation of one task by one specific provider/model configuration.

**Structure of a single result object:**

```json
{
    "task_id": "task_01",
    "provider_identifier": "DeepSeek__deepseek-chat",
    "provider_name": "DeepSeek",
    "model_name": "deepseek-chat",
    "llm_response": ["A", "C"],
    "ground_truth": ["A", "C"],
    "is_correct": true,
    "task_instruction": "Choose all correct options keys.",
    "task_question": "Which letters are vowels?"
}
```

The file will contain a JSON list `[...]` of these objects, accumulating results across runs if resumption is used.

## Architecture Overview

The code is structured into several classes to promote modularity:

*   `DataLoader`: Handles loading data from the Excel file.
*   `DataTransformer`: Parses and transforms raw Excel rows into structured Python dictionaries.
*   `AsyncLLMClient`: Manages asynchronous interaction with a specific OpenAI-compatible API endpoint.
*   `LLMProvider`: Encapsulates configuration (name, model, credentials) and holds an `AsyncLLMClient` instance for a specific provider.
*   `Evaluator`: Contains the logic for comparing LLM responses to ground truth answers based on type.
*   `EvaluationRunner`: Orchestrates the entire process – loading, transforming, dispatching async API calls, evaluating, handling resumption, and saving results.