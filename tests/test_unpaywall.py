import doi_downloader.unpaywall as unpaywall
import pytest
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read API keys and other sensitive data from environment variables
UNPAYWALL_EMAIL = os.getenv("UNPAYWALL_EMAIL")

def test_set_email():
    unpaywall.set_email(UNPAYWALL_EMAIL)
    assert unpaywall.UNPAYWALL_EMAIL == UNPAYWALL_EMAIL

def test_get_url():
    TEST_DOI="10.1109/ACCESS.2019.2931762"
    url = unpaywall.get_url(TEST_DOI)
    assert url == "https://ieeexplore.ieee.org/ielx7/6287639/8600701/08779607.pdf"

def test_download_doi():
    TEST_DOI="10.1109/ACCESS.2019.2931762"
    result = unpaywall.download_from_doi(TEST_DOI)
    assert result
    assert os.path.exists("10.1109_ACCESS.2019.2931762.pdf")
    os.remove("10.1109_ACCESS.2019.2931762.pdf")
    assert not os.path.exists("10.1109_ACCESS.2019.2931762.pdf")

