# scripts/generate_qa_dataset.py

import os
import json
import argparse
import asyncio
import logging
from tqdm import tqdm
from dotenv import load_dotenv
import google.generativeai as genai

# Import helper functions from our utility module within the same package.
# The '.' before 'utils' indicates a relative import from the same package.
from .utils import split_text_into_chunks, read_text_file

# --- Configuration ---

# Load environment variables from a .env file in the project root.
# This is where we'll securely store the API key.
load_dotenv()

# Configure logging to provide clear, timestamped output.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Domain-Specific Prompt Engineering ---

# This dictionary holds prompt "personas" for different domains.
# By changing the persona, we can guide the model to generate more
# domain-appropriate content. This makes the script highly adaptable.
PROMPT_TEMPLATES = {
    "legal": "You are a meticulous paralegal specializing in contract analysis. Your task is to create training data by extracting key details.",
    "finance": "You are a senior financial analyst. Your task is to dissect financial reports to create training data for junior analysts.",
    "healthcare": "You are a health information specialist. Your task is to process de-identified clinical notes to create training data for medical AI.",
    "default": "You are a helpful AI assistant. Your task is to create structured training data from the provided text."
}

async def generate_qa_from_text(text_chunk: str, domain: str):
    """
    Generates structured question-answer pairs from a chunk of text using the Gemini API.

    This asynchronous function sends a single text chunk to the API and asks for a
    structured JSON output, which prevents parsing errors and ensures data consistency.

    Args:
        text_chunk (str): A string containing the source text for generation.
        domain (str): The domain of the text (e.g., 'legal', 'finance'), which
                      determines the prompt persona.

    Returns:
        A list of dictionaries, where each dictionary is a Q&A pair. Returns an
        empty list if the API call fails or returns an invalid structure.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logging.error("FATAL: GOOGLE_API_KEY environment variable not set. Please create a .env file or set it manually.")
        return []

    genai.configure(api_key=api_key)
    
    # Define the JSON schema for the model's output. This is a powerful feature
    # that forces the model to return clean, predictable JSON, which is ideal for
    # production pipelines.
    schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "question": {"type": "STRING", "description": "A detailed question derived from the text."},
                "answer": {"type": "STRING", "description": "A precise answer to the question."},
                "context_used": {"type": "STRING", "description": "The exact text snippet used for the answer."}
            },
            "required": ["question", "answer", "context_used"]
        }
    }

    # Select the appropriate persona from our templates based on the domain.
    persona = PROMPT_TEMPLATES.get(domain, PROMPT_TEMPLATES["default"])
    
    # Construct the final prompt sent to the model.
    prompt = f"""
    {persona}
    Based on the following text, generate a series of high-quality question-and-answer pairs.
    Each pair must be directly and fully answerable from the provided text.
    The answer should be thorough and precise. Also include the specific context snippet used for the answer.

    Text:
    ---
    {text_chunk}
    ---
    """
    
    # Prepare the payload for the API call.
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generation_config": {
            "response_mime_type": "application/json",
            "response_schema": schema
        }
    }

    try:
        # Initialize the model. 'gemini-1.5-flash' is a good balance of speed and capability.
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Make the asynchronous API call.
        response = await model.generate_content_async(payload['contents'], generation_config=payload['generation_config'])
        
        # The response.text will be a JSON string that matches our schema.
        return json.loads(response.text)
        
    except Exception as e:
        logging.error(f"An error occurred during the API call: {e}")
        return []

def main():
    """
    The main function that orchestrates the entire dataset generation process.
    It handles command-line arguments, file I/O, and calls the generation function.
    """
    # Set up command-line argument parsing for a professional user experience.
    parser = argparse.ArgumentParser(description="Generate a synthetic Question/Answer dataset from a text file.")
    parser.add_argument("--input_file", type=str, required=True, help="Path to the source .txt file.")
    parser.add_argument("--output_file", type=str, required=True, help="Path for the output .jsonl file.")
    parser.add_argument("--domain", type=str, default="default", choices=list(PROMPT_TEMPLATES.keys()), help="Domain of the source text to tailor the prompt.")
    args = parser.parse_args()

    logging.info(f"Starting dataset generation process for domain: '{args.domain}'")
    
    # Step 1: Read the source text from the specified input file.
    source_text = read_text_file(args.input_file)
    if not source_text:
        logging.critical(f"Failed to read source text from {args.input_file}. Aborting process.")
        return

    # Step 2: Split the source text into manageable chunks for API processing.
    text_chunks = split_text_into_chunks(source_text)
    if not text_chunks:
        logging.warning("Source text was empty or could not be split into chunks. No data to process.")
        return

    # Step 3: Ensure the output directory exists before trying to write to it.
    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    total_pairs_generated = 0
    
    # Step 4: Process each chunk and write the results to the output file.
    # The 'with' statement ensures the file is properly closed even if errors occur.
    with open(args.output_file, 'w', encoding='utf-8') as f:
        # tqdm provides a progress bar for a better user experience with large files.
        for chunk in tqdm(text_chunks, desc="Processing text chunks"):
            # Run our asynchronous generation function for the current chunk.
            qa_pairs = asyncio.run(generate_qa_from_text(chunk, args.domain))
            if qa_pairs:
                for pair in qa_pairs:
                    # Write each generated Q&A pair as a new line in the JSONL file.
                    f.write(json.dumps(pair) + '\n')
                total_pairs_generated += len(qa_pairs)

    logging.info(f"--- Generation Complete ---")
    logging.info(f"Successfully generated {total_pairs_generated} Q&A pairs.")
    logging.info(f"Output dataset saved to: {args.output_file}")

if __name__ == "__main__":
    # This standard Python construct ensures that main() is called only when the script
    # is executed directly, not when it's imported as a module elsewhere.
    main()
