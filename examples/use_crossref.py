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
    dois = csv.load_dois_from_file(dois_file_path, "doi")
    print(f'Number of DOIs: {len(dois)}')
    unique_dois = csv.load_dois_from_file(dois_file_path, "doi", unique=True)
    print(f'Number of unique DOIs: {len(unique_dois)}')
    # Print difference
    print(f'Number of duplicates: {len(dois) - len(unique_dois)}')

    # Get URLs for dois
    urls = crf.get_urls(dois, False)
    print(urls)
    false_values = sum(1 for value in urls.values() if value is False)
    print(false_values)
    # no_urls = crf.get_list_with_no_urls()
    # for (doi, _, _) in no_urls:
    #     print(doi)
    # print(len(no_urls))

main()
