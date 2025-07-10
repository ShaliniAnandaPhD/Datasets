# scripts/generate_classifications.py

import os
import json
import argparse
import asyncio
import logging
from tqdm import tqdm
from dotenv import load_dotenv
import google.generativeai as genai

# Import shared utilities and the new config file
from .utils import split_text_into_chunks, read_text_file
from .config import CLASSIFICATION_LABELS

# --- Configuration ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def generate_classification_from_text(text_chunk: str, domain: str):
    """
    Classifies a text chunk into a predefined category for a given domain.

    Args:
        text_chunk (str): The source text to classify.
        domain (str): The domain used to fetch the appropriate classification labels.

    Returns:
        A dictionary with the text and its classification, or None on failure.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logging.error("FATAL: GOOGLE_API_KEY not set.")
        return None

    genai.configure(api_key=api_key)
    
    # Fetch the classification labels for the specified domain from our config.
    labels = CLASSIFICATION_LABELS.get(domain, CLASSIFICATION_LABELS["default"])
    
    # Define the JSON schema, dynamically inserting the valid labels.
    schema = {
        "type": "OBJECT",
        "properties": {
            "text_snippet": {"type": "STRING"},
            "classification": {"type": "STRING", "enum": labels}
        },
        "required": ["text_snippet", "classification"]
    }

    prompt = f"""
    You are a text classification expert. Your task is to classify the following text snippet into one of the provided categories.
    Choose the single best category from the list.

    Categories: {', '.join(labels)}

    Text to Classify:
    ---
    {text_chunk}
    ---
    """
    
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generation_config": {"response_mime_type": "application/json", "response_schema": schema}
    }

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = await model.generate_content_async(payload['contents'], generation_config=payload['generation_config'])
        return json.loads(response.text)
    except Exception as e:
        logging.error(f"API call for classification failed: {e}")
        return None

def main():
    """Main function to orchestrate the classification dataset generation."""
    parser = argparse.ArgumentParser(description="Generate a synthetic classification dataset.")
    parser.add_argument("--input_file", type=str, required=True, help="Path to the source .txt file.")
    parser.add_argument("--output_file", type=str, required=True, help="Path for the output .jsonl file.")
    parser.add_argument("--domain", type=str, required=True, choices=list(CLASSIFICATION_LABELS.keys()), help="Domain to use for classification labels.")
    args = parser.parse_args()

    logging.info(f"Starting classification for domain: '{args.domain}'")
    
    source_text = read_text_file(args.input_file)
    if not source_text:
        return

    # For classification, we want to classify smaller, more focused chunks.
    text_chunks = split_text_into_chunks(source_text, max_chunk_size=500, overlap=50)
    if not text_chunks:
        return

    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    total_classifications = 0
    
    with open(args.output_file, 'w', encoding='utf-8') as f:
        for chunk in tqdm(text_chunks, desc="Classifying text snippets"):
            classification_data = asyncio.run(generate_classification_from_text(chunk, args.domain))
            if classification_data:
                f.write(json.dumps(classification_data) + '\n')
                total_classifications += 1

    logging.info(f"--- Classification Complete ---")
    logging.info(f"Generated {total_classifications} classifications.")
    logging.info(f"Output saved to: {args.output_file}")

if __name__ == "__main__":
    main()
