Datasets for the Neuron FrameworkOverviewWelcome to the official datasets repository! 


This project is dedicated to creating and maintaining a comprehensive collection of datasets for testing, proof-of-concept (PoC), and development activities related to the Neuron Framework.Our primary goal is to provide a diverse mix of raw, processed, and synthetically generated data across three key domains: Financial, Healthcare, and Legal.Purpose and Data FlowThis repository acts as a centralized data hub. Raw data is ingested and then processed by our utility scripts to create clean, structured datasets. These final datasets are then consumed by the Neuron Framework for robust testing and validation.          
                     

                                +-----------------------------+
                               |      NEURON FRAMEWORK       |
                               |     (Testing & PoCs)        |
                               +--------------+--------------+
                                              ^
                                              |
                                              | Consumes
                                              |
+----------------------+     +-----------------------------+
|   RAW DATA SOURCES   |     |      PROCESSED DATASETS     |
| (Contracts, Reports, |     | (Located in /data/...)      |
|  Clinical Notes...)  |     +--------------+--------------+
+-----------+----------+                      ^
            |                                 |
            | Ingested & Processed by         | Creates
            |                                 |
            v                                 |
+-----------+----------+     +----------------+--------------+
|        DOMAINS       |     |          UTILITY SCRIPTS      |
| FIN | HEALTH | LEGAL |     | (Located in /scripts/...)     |
+----------------------+     +-------------------------------+

Available Datasets

This section provides an overview of the datasets available for each domain.Financial DatasetsLocation: data/finance/Description: A collection of financial documents, including raw quarterly reports, synthetic transaction logs, and datasets for tasks like sentiment analysis of financial news.Healthcare DatasetsLocation: data/healthcare/Description: Contains de-identified clinical notes, synthetic patient records, and data for training models on tasks like medical entity recognition and summarization.Legal DatasetsLocation: data/legal/Description: This collection includes raw contract templates, synthetic legal case summaries, and datasets generated to support tasks like legal document analysis and clause classification.

Utility Scripts

To help manage the datasets, this repository includes several utility scripts.archive_datasets.pyLocation: scripts/archive_datasets.pyPurpose: This script provides a command-line tool to create timestamped .zip archives of the dataset directories. This is essential for versioning, backups, and ensuring the reproducibility of tests.Usage:# Archive a specific domain's data

python scripts/archive_datasets.py --source_dir data/legal

How to Contribute

Contributions, issues, and feature requests are welcome. If you have a dataset you would like to add or a suggestion for improving the repository, please feel free to open an issue or submit a pull request.

License

The contents of this repository are licensed under the MIT License.


