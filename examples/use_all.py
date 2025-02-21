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
    
    # Load plugins
    plugins = ld.plugins 

    for doi in unique_dois:
        for name, plugin in plugins.items():
            url = plugin.get_pdf_url(doi)
            if url:
                print(f"Plugin: {name},  doi:{doi},  url: {plugin.get_pdf_url(doi)}")
                continue

main()
