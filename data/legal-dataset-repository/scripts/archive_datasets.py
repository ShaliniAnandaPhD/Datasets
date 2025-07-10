# scripts/archive_datasets.py

import os
import zipfile
import argparse
import logging
from datetime import datetime

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def archive_datasets(source_dir: str, output_dir: str):
    """
    Creates a timestamped zip archive of a directory.

    This is useful for creating versioned backups of the generated_datasets
    folder before running a new generation pipeline.

    Args:
        source_dir (str): The directory to be archived (e.g., 'data/generated_datasets').
        output_dir (str): The directory where the zip archive will be saved.
    """
    if not os.path.isdir(source_dir):
        logging.error(f"Source directory not found: {source_dir}. Aborting archive.")
        return

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate a timestamp for the archive name (e.g., 2025-07-10_14-30-00)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_name = f"dataset_archive_{timestamp}.zip"
    archive_path = os.path.join(output_dir, archive_name)

    logging.info(f"Archiving directory '{source_dir}' to '{archive_path}'...")

    try:
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the source directory
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Create a relative path for the files inside the zip
                    archive_file_path = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, archive_file_path)
        
        logging.info("Archive created successfully!")
    except Exception as e:
        logging.error(f"Failed to create archive: {e}")

def main():
    """Main function to run the archiving script."""
    parser = argparse.ArgumentParser(description="Archive the generated datasets.")
    parser.add_argument("--source_dir", type=str, default="data/generated_datasets", help="Directory containing the datasets to archive.")
    parser.add_argument("--output_dir", type=str, default="data/archives", help="Directory to save the timestamped archive.")
    args = parser.parse_args()

    archive_datasets(args.source_dir, args.output_dir)

if __name__ == "__main__":
    main()
