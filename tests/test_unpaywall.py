import doi_downloader.unpaywall as unpaywall
import responses


# Read API keys and other sensitive data from environment variables
TEST_DOI="10.1007/s10207-021-00566-3"
TEST_FILE="10.1007_s10207-021-00566-3.pdf"

def test_set_email():
    unpaywall.set_email("test@test.com")
    assert unpaywall.UNPAYWALL_EMAIL == "test@test.com"

@responses.activate
def test_get_url():
    # Mock the response from the Unpaywall API
    unpaywall_url = unpaywall.UNPAYWALL_API_URL.format(doi=TEST_DOI, email=unpaywall.UNPAYWALL_EMAIL)
    responses.add(responses.GET, unpaywall_url,
                  json={"best_oa_location": {"url_for_pdf": "https://link.springer.com/content/pdf/10.1007/s10207-021-00566-3.pdf"}},
                  status=200)


    url = unpaywall.get_url(TEST_DOI, use_cache=False)
    assert url =='https://link.springer.com/content/pdf/10.1007/s10207-021-00566-3.pdf'

