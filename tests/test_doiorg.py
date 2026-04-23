from doi_downloader.plugins import doiorg
from unittest.mock import patch
import responses

TEST_DOI ="10.1007/s10207-021-00566-3"

@responses.activate
def test_get_url():
    doiorg_url = doiorg.DOIORG_URL.format(doi=TEST_DOI)

    with patch.object(doi_downloader.plugins.doiorg.DoiorgPlugin, "fetch_metadata", return_value=doiorg_url):
        instance = doiorg.DoiorgPlugin()
        url = instance.get_pdf_url(TEST_DOI, use_cache=False)
    assert url == doiorg_url
