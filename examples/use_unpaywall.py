from doi_downloader import unpaywall as upw
from doi_downloader import csv
import os
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read API keys and other sensitive data from environment variables
UNPAYWALL_EMAIL = os.getenv("UNPAYWALL_EMAIL")

# Set up argument parser
parser = argparse.ArgumentParser(description="Process a CSV file.")
parser.add_argument('-f', '--file', type=str, required=True, help="Path to the CSV file")
args = parser.parse_args()

# Check if file argument is provided
if not args.file:
    raise ValueError("The '-f' argument is required. Please specify a CSV file using '-f filename.csv'.")

# Check if file exists
dois_file_path = args.file

# Check if necessary variables are loaded
if not UNPAYWALL_EMAIL:
    raise EnvironmentError("Please make sure UNPAYWALL_EMAIL are set in the .env file.")


# Main function
def main():
    # Set up email
    upw.set_email(UNPAYWALL_EMAIL)

    dois = csv.load_dois_from_file(dois_file_path, "doi")
    print(f'Number of DOIs: {len(dois)}')
    unique_dois = csv.load_dois_from_file(dois_file_path, "doi", unique=True)
    print(f'Number of unique DOIs: {len(unique_dois)}')
    # Print difference
    print(f'Number of duplicates: {len(dois) - len(unique_dois)}')

    for doi in unique_dois:
        pdf_url = upw.get_pdf_url(doi, use_cache=True)
        print(f'{doi}: {pdf_url}')
        

    # Get URLs for dois
    # urls = upw.get_urls(dois)
    # false_values = sum(1 for value in urls.values() if value is False)
    # print(false_values)
    # no_urls = upw.get_list_with_no_urls()
    # for (doi, _, _) in no_urls:
    #     print(doi)
    # print(len(no_urls))
    # for url in urls:
    #     print(f'{url["doi"]}: {url["url"]}')

    # Download files

    # dois = load_dois_from_file(dois_file_path)
    # files = upw.download_from_dois(dois)
    # print(files)


main()
