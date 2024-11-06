import doi_downloader.unpaywall as unpaywall
import pytest
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read API keys and other sensitive data from environment variables
UNPAYWALL_EMAIL = os.getenv("UNPAYWALL_EMAIL")
TEST_DOI="10.1007/s10207-021-00566-3"
TEST_FILE="10.1007_s10207-021-00566-3.pdf"

def test_set_email():
    unpaywall.set_email(UNPAYWALL_EMAIL)
    assert unpaywall.UNPAYWALL_EMAIL == UNPAYWALL_EMAIL

def test_get_url():
    url = unpaywall.get_url(TEST_DOI)
    assert url =='https://link.springer.com/content/pdf/10.1007/s10207-021-00566-3.pdf'

def test_download_doi():
    result = unpaywall.download_from_doi(TEST_DOI)
    assert result
    assert os.path.exists(TEST_FILE)
    os.remove(TEST_FILE)
    assert not os.path.exists(TEST_FILE)

