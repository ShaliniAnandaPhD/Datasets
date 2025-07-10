# scripts/evaluate_dataset.py

import json
import argparse
import logging

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def evaluate_jsonl_dataset(file_path: str):
    """
    Performs basic quality checks on a JSON Lines (.jsonl) dataset file.

    This script is a crucial part of a production pipeline, ensuring that
    downstream tasks receive clean, valid data.

    Checks performed:
    1.  Each line is a valid JSON object.
    2.  Each JSON object contains all expected keys.
    3.  The values for those keys are not empty or null.

    Args:
        file_path (str): The path to the .jsonl dataset file.
    """
    logging.info(f"Starting evaluation for dataset: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        logging.error(f"Evaluation failed: File not found at {file_path}")
        return

    if not lines:
        logging.warning("The dataset file is empty.")
        return

    total_lines = len(lines)
    invalid_json_count = 0
    missing_key_count = 0
    empty_value_count = 0
    
    # Determine expected keys from the first valid line
    expected_keys = None

    for i, line in enumerate(lines):
        line_num = i + 1
        try:
            data = json.loads(line)
            if expected_keys is None:
                expected_keys = set(data.keys())
                logging.info(f"Inferred expected keys from first record: {sorted(list(expected_keys))}")

            # Check for missing keys
            if set(data.keys()) != expected_keys:
                missing_key_count += 1
                logging.warning(f"Line {line_num}: Mismatched keys. Expected {expected_keys}, got {set(data.keys())}")
                continue
            
            # Check for empty values
            for key, value in data.items():
                if not value and value != 0: # Allow 0 as a valid value
                    empty_value_count += 1
                    logging.warning(f"Line {line_num}: Empty value for key '{key}'")

        except json.JSONDecodeError:
            invalid_json_count += 1
            logging.error(f"Line {line_num}: Invalid JSON format.")

    logging.info("--- Evaluation Summary ---")
    logging.info(f"Total records processed: {total_lines}")
    logging.info(f"Records with invalid JSON format: {invalid_json_count}")
    logging.info(f"Records with missing/extra keys: {missing_key_count}")
    logging.info(f"Records with empty values: {empty_value_count}")

    if invalid_json_count == 0 and missing_key_count == 0 and empty_value_count == 0:
        logging.info("Result: Dataset passed all quality checks!")
    else:
        logging.error("Result: Dataset has quality issues. Please review the warnings above.")


def main():
    """Main function to run the evaluation script."""
    parser = argparse.ArgumentParser(description="Evaluate a generated .jsonl dataset for quality.")
    parser.add_argument("--input_file", type=str, required=True, help="Path to the .jsonl dataset to evaluate.")
    args = parser.parse_args()
    
    evaluate_jsonl_dataset(args.input_file)

if __name__ == "__main__":
    main()
