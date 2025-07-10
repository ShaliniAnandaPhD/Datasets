# scripts/config.py

# This file centralizes configuration for the data generation scripts.
# By keeping settings here, we can easily update them without changing the core logic
# of the generation scripts themselves.

# --- Classification Labels ---
# Define the categories for the classification task, organized by domain.
# This allows the classification script to be generic while handling domain-specific needs.
CLASSIFICATION_LABELS = {
    "legal": [
        "Governing Law",
        "Confidentiality",
        "Limitation of Liability",
        "Termination",
        "Indemnification",
        "Force Majeure",
        "Miscellaneous"
    ],
    "finance": [
        "Revenue Growth",
        "Profit Margin Analysis",
        "Risk Assessment",
        "Forward-Looking Statement",
        "Shareholder Equity",
        "Debt and Liabilities"
    ],
    "healthcare": [
        "Patient History",
        "Diagnosis",
        "Prescription",
        "Symptom Description",
        "Treatment Plan",
        "Test Results"
    ],
    # Add other domains and their respective labels here.
    "default": [
        "General Information",
        "Key Highlight",
        "Action Item"
    ]
}

# --- API & Model Configuration ---
# You could centralize model names or API parameters here as well.
# For example:
# GENERATIVE_MODEL_NAME = 'gemini-1.5-flash'
# MAX_TOKENS_OUTPUT = 1024

