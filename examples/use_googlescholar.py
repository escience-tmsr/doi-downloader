from doi_downloader import loader as ld
from doi_downloader import csv
import argparse

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
    dois = csv.load_dois_from_file(dois_file_path, "doi")
    print(f'Number of DOIs: {len(dois)}')
    unique_dois = csv.load_dois_from_file(dois_file_path, "doi", unique=True)
    print(f'Number of unique DOIs: {len(unique_dois)}')
    # Print difference
    print(f'Number of duplicates: {len(dois) - len(unique_dois)}')

    plugins = ld.plugins
    serpapi = plugins['GoogleScholarSerpAPIPlugin']

    for doi in unique_dois:
        pdf_url = serpapi.get_pdf_url(doi, use_cache=True)
        print(f'{doi}: {pdf_url}')
        


main()
