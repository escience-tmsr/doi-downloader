from doi_downloader.plugins import unpaywall as unpaywall
import responses
import os

TEST_DOI="10.1007/s10207-021-00566-3"
TEST_FILE="10.1007_s10207-021-00566-3.pdf"
UNPAYWALL_API_URL = "https://api.unpaywall.org/v2/{doi}?email={email}"


@responses.activate
def test_get_url(tmp_path):
    upw = unpaywall.UnpaywallPlugin()

    # Mock the response from the Unpaywall API
    unpaywall_url = UNPAYWALL_API_URL.format(doi=TEST_DOI, email=unpaywall.UNPAYWALL_EMAIL)
    responses.add(responses.GET, unpaywall_url,
                  json={"best_oa_location": {"url_for_pdf": "https://link.springer.com/content/pdf/10.1007/s10207-021-00566-3.pdf"}},
                  status=200)


    url = upw.get_pdf_url(TEST_DOI, use_cache=False)
    assert url =='https://link.springer.com/content/pdf/10.1007/s10207-021-00566-3.pdf'
