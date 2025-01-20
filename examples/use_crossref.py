from doi_downloader import crossref as crf
from doi_downloader import csv
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up argument parser
parser = argparse.ArgumentParser(description="Process a CSV file.")
parser.add_argument('-f', '--file', type=str, required=True, help="Path to the CSV file")
args = parser.parse_args()

# Check if file argument is provided
if not args.file:
    raise ValueError("The '-f' argument is required. Please specify a CSV file using '-f filename.csv'.")

# Check if file exists
dois_file_path = args.file

# Main function
def main():
    # Example usage
    doi = "10.1038/s41586-019-1666-5"  # Replace with the DOI you want to query
    metadata = crf.fetch_metadata(doi)
    print(metadata)

main()
