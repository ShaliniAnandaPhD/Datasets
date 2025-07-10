# scripts/generate_summaries.py

import os
import json
import argparse
import asyncio
import logging
from tqdm import tqdm
from dotenv import load_dotenv
import google.generativeai as genai

# Import shared utilities
from .utils import split_text_into_chunks, read_text_file

# --- Configuration ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Domain-Specific Prompt Engineering for Summarization ---
PROMPT_TEMPLATES = {
    "legal": "You are a senior lawyer. Your task is to provide a concise, abstractive summary of the following legal document, highlighting the key obligations, rights, and definitions.",
    "finance": "You are a financial analyst. Your task is to summarize the following report, focusing on key performance indicators, financial health, and future outlook.",
    "healthcare": "You are a medical scribe. Your task is to create a brief, abstractive summary of the following clinical notes, focusing on patient diagnosis, treatment, and outcomes.",
    "default": "You are a helpful AI assistant. Your task is to provide a clear and concise abstractive summary of the following text."
}

async def generate_summary_from_text(text_chunk: str, domain: str):
    """
    Generates an abstractive summary from a chunk of text using the Gemini API.

    Args:
        text_chunk (str): A string containing the source text for summarization.
        domain (str): The domain of the text to select the appropriate prompt persona.

    Returns:
        A dictionary containing the source text and its summary, or None on failure.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logging.error("FATAL: GOOGLE_API_KEY not set.")
        return None

    genai.configure(api_key=api_key)
    
    # Define the desired JSON output structure for the summary.
    schema = {
        "type": "OBJECT",
        "properties": {
            "source_text": {"type": "STRING", "description": "The original text that was summarized."},
            "summary": {"type": "STRING", "description": "The generated abstractive summary."}
        },
        "required": ["source_text", "summary"]
    }

    persona = PROMPT_TEMPLATES.get(domain, PROMPT_TEMPLATES["default"])
    prompt = f"{persona}\n\nSummarize this text:\n---\n{text_chunk}\n---"
    
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generation_config": {"response_mime_type": "application/json", "response_schema": schema}
    }

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = await model.generate_content_async(payload['contents'], generation_config=payload['generation_config'])
        return json.loads(response.text)
    except Exception as e:
        logging.error(f"API call for summarization failed: {e}")
        return None

def main():
    """Main function to orchestrate the summarization dataset generation process."""
    parser = argparse.ArgumentParser(description="Generate a synthetic summarization dataset from a text file.")
    parser.add_argument("--input_file", type=str, required=True, help="Path to the source .txt file.")
    parser.add_argument("--output_file", type=str, required=True, help="Path for the output .jsonl file.")
    parser.add_argument("--domain", type=str, default="default", choices=list(PROMPT_TEMPLATES.keys()), help="Domain of the source text.")
    args = parser.parse_args()

    logging.info(f"Starting summarization for domain: '{args.domain}'")
    
    source_text = read_text_file(args.input_file)
    if not source_text:
        return

    # For summarization, we often process larger chunks or the whole document if possible.
    # Here, we'll still chunk it to be safe.
    text_chunks = split_text_into_chunks(source_text, max_chunk_size=8000, overlap=400)
    if not text_chunks:
        return

    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    total_summaries = 0
    
    with open(args.output_file, 'w', encoding='utf-8') as f:
        for chunk in tqdm(text_chunks, desc="Generating summaries"):
            summary_data = asyncio.run(generate_summary_from_text(chunk, args.domain))
            if summary_data:
                f.write(json.dumps(summary_data) + '\n')
                total_summaries += 1

    logging.info(f"--- Summarization Complete ---")
    logging.info(f"Generated {total_summaries} summaries.")
    logging.info(f"Output saved to: {args.output_file}")

if __name__ == "__main__":
    main()
