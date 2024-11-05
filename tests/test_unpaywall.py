import doi_downloader.unpaywall as unpaywall
import pytest
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read API keys and other sensitive data from environment variables
UNPAYWALL_EMAIL = os.getenv("UNPAYWALL_EMAIL")


def test_unpaywall():
    TEST_DOI="10.1109/ACCESS.2019.2931762"
    unpaywall.set_email(UNPAYWALL_EMAIL)
    url = unpaywall.get_url(TEST_DOI)
    assert url == "https://ieeexplore.ieee.org/ielx7/6287639/8600701/08779607.pdf"
