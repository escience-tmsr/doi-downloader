from doi_downloader import unpaywall as upw
import os
import argparse
import csv
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
if not os.path.isfile(dois_file_path):
    raise FileNotFoundError(f"The file '{dois_file_path}' does not exist. Please provide a valid file path.")

# Check if necessary variables are loaded
if not UNPAYWALL_EMAIL:
    raise EnvironmentError("Please make sure UNPAYWALL_EMAIL are set in the .env file.")


def load_dois_from_file(file_path, column_name="doi"):
    with open(file_path, 'r') as f:
        array = [row['doi'] for row in csv.DictReader(f)]
    return array


# Main function
def main():
    # Set up email
    upw.set_email(UNPAYWALL_EMAIL)

    # dois = load_dois_from_file(dois_file_path, "doi")
    # print(dois)
    # urls = upw.get_urls(dois)
    # print(urls)
    TEST_DOI="10.1111/j.1468-0335.2008.00689.x"
    print(upw.get_url(TEST_DOI))



    # # Load DOIs from file
    # dois = load_dois_from_file(dois_file_path)
    # print(dois)
    # files = upw.download_from_dois(dois)
    # print(files)


main()
