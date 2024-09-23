"""CLI interface for doi_downloader project.

Be creative! do whatever you want!

- Install click or typer and create a CLI app
- Use builtin argparse
- Start a web application
- Import things from your .base module
"""

import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Read API keys and other sensitive data from environment variables
UNPAYWALL_EMAIL = os.getenv("UNPAYWALL_EMAIL")
UNPAYWALL_API_URL = "https://api.unpaywall.org/v2/{doi}?email={email}"
dois_file_path = "dois.csv"

# Check if necessary variables are loaded
if not UNPAYWALL_EMAIL:
    raise EnvironmentError("Please make sure UNPAYWALL_EMAIL are set in the .env file.")


def get_open_access_pdf(doi):
    # Make the request to the Unpaywall API
    response = requests.get(UNPAYWALL_API_URL.format(doi=doi, email=UNPAYWALL_EMAIL))

    if response.status_code == 200:
        data = response.json()
        if "best_oa_location" in data and data["best_oa_location"]:
            pdf_url = data["best_oa_location"]["url_for_pdf"]
            print(f"Open access PDF for {doi}: {pdf_url}")
            return pdf_url
        else:
            print(f"No open access PDF found for {doi}.")
    else:
        print(f"Failed to retrieve Unpaywall data for DOI {doi}.")
    return None


# Function to download PDF
def download_pdf(pdf_url, filename):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Downloaded PDF: {filename}")
    else:
        print(f"Failed to download PDF from {pdf_url}")


def load_dois_from_file(file_path):
    with open(file_path, "r") as file:
        content = file.read().strip()
        values = content.split(",")
        lines = [line.strip() for line in values]
    return lines


# Main function
def main():  # pragma: no cover
    """
    The main function executes on commands:
    `python -m doi_downloader` and `$ doi_downloader `.

    This is your program's entry point.

    You can change this function to do whatever you want.
    Examples:
        * Run a test suite
        * Run a server
        * Do some other stuff
        * Run a command line application (Click, Typer, ArgParse)
        * List all available tasks
        * Run an application (Flask, FastAPI, Django, etc.)
    """
    # Load DOIs from file
    dois = load_dois_from_file(dois_file_path)
    # Attempt to download PDFs for each DOI
    for doi in dois:
        pdf_url = get_open_access_pdf(doi)
        if pdf_url:
            download_pdf(pdf_url, f"{doi.replace('/', '_')}.pdf")
