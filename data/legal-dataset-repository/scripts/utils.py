import logging
import os

# --- Configuration ---
# Set up a basic logger to output informational messages and errors.
# This is more robust than using print() statements for debugging.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def split_text_into_chunks(text: str, max_chunk_size: int = 4000, overlap: int = 200) -> list[str]:
    """
    Splits a long text into smaller, overlapping chunks.

    This function is critical for handling large documents that exceed the token limit
    of a single API call to a generative model. By creating overlapping chunks,
    we help preserve the context between them, which can lead to more coherent
    and accurate generated data.

    Args:
        text (str): The full text document to be split.
        max_chunk_size (int): The maximum number of characters for each chunk.
                              This should be set based on the model's context window.
        overlap (int): The number of characters to include from the end of the previous
                       chunk at the beginning of the next one.

    Returns:
        list[str]: A list of text strings, each representing a chunk of the original text.
    """
    if not isinstance(text, str) or not text:
        logging.warning("Input text is empty or not a string. Returning empty list.")
        return []

    chunks = []
    start_index = 0
    # Loop through the text, creating chunks until the end is reached.
    while start_index < len(text):
        end_index = start_index + max_chunk_size
        chunks.append(text[start_index:end_index])
        # Move the start index forward for the next chunk, accounting for the overlap.
        start_index += max_chunk_size - overlap
    
    logging.info(f"Successfully split source text into {len(chunks)} chunk(s).")
    return chunks

def read_text_file(file_path: str) -> str | None:
    """
    Reads content from a specified text file with robust error handling.

    This function ensures that file-related errors (like the file not existing)
    are caught gracefully and logged, preventing the main script from crashing.

    Args:
        file_path (str): The absolute or relative path to the text file.

    Returns:
        str | None: The content of the file as a single string if successful,
                    otherwise None.
    """
    if not os.path.exists(file_path):
        logging.error(f"File not found at the specified path: {file_path}")
        return None
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            logging.info(f"Successfully read file: {file_path}")
            return f.read()
    except Exception as e:
        logging.error(f"An unexpected error occurred while reading the file {file_path}: {e}")
        return None

