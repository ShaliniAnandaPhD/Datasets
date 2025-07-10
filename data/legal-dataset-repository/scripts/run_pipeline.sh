#!/bin/bash

# ==============================================================================
# Synthetic Dataset Generation Pipeline
#
# This script automates the process of generating and evaluating multiple
# datasets. It ensures a consistent and repeatable workflow.
#
# Usage:
#   ./scripts/run_pipeline.sh <domain> <input_file_path>
#
# Example:
#   ./scripts/run_pipeline.sh legal data/raw_source_texts/legal/nda.txt
# ==============================================================================

# --- Configuration ---
# Exit immediately if a command exits with a non-zero status.
set -e

# The domain for the dataset (e.g., 'legal', 'finance')
DOMAIN=$1
# The path to the raw source text file
INPUT_FILE=$2

# Check if arguments are provided
if [ -z "$DOMAIN" ] || [ -z "$INPUT_FILE" ]; then
  echo "Usage: $0 <domain> <input_file_path>"
  exit 1
fi

# Get the base name of the input file (e.g., 'nda')
BASENAME=$(basename "$INPUT_FILE" .txt)
OUTPUT_DIR="data/generated_datasets/$DOMAIN"

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo "=================================================="
echo "Starting Pipeline for Domain: $DOMAIN"
echo "Source File: $INPUT_FILE"
echo "=================================================="

# --- Step 1: Generate Question-Answer Dataset ---
echo -e "\n[Step 1/4] Generating Question-Answer Dataset..."
QA_OUTPUT_FILE="$OUTPUT_DIR/${BASENAME}_qa.jsonl"
python scripts/generate_qa_dataset.py --input_file "$INPUT_FILE" --output_file "$QA_OUTPUT_FILE" --domain "$DOMAIN"

# --- Step 2: Evaluate the Q&A Dataset ---
echo -e "\n[Step 2/4] Evaluating Question-Answer Dataset..."
python scripts/evaluate_dataset.py --input_file "$QA_OUTPUT_FILE"

# --- Step 3: Generate Summaries Dataset ---
echo -e "\n[Step 3/4] Generating Summaries Dataset..."
SUMMARIES_OUTPUT_FILE="$OUTPUT_DIR/${BASENAME}_summaries.jsonl"
python scripts/generate_summaries.py --input_file "$INPUT_FILE" --output_file "$SUMMARIES_OUTPUT_FILE" --domain "$DOMAIN"

# --- Step 4: Evaluate the Summaries Dataset ---
echo -e "\n[Step 4/4] Evaluating Summaries Dataset..."
python scripts/evaluate_dataset.py --input_file "$SUMMARIES_OUTPUT_FILE"

echo -e "\n=================================================="
echo "Pipeline finished successfully!"
echo "Generated datasets are located in: $OUTPUT_DIR"
echo "=================================================="

