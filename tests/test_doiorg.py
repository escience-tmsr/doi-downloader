import responses
from unittest.mock import patch

from doi_downloader import article_dataobject as ado
from doi_downloader.plugins import doiorg
from doi_downloader.plugins import CacheMode

TEST_DOI ="10.1007/s10207-021-00566-3"


@responses.activate
def test_get_url():
    doiorg_url = doiorg.DOIORG_URL.format(doi=TEST_DOI)

    data_object = ado.ArticleDataObject(None)
    data_object.add_pdf_link(doiorg_url)
    with patch.object(doiorg.DoiorgPlugin, "fetch_metadata", return_value=data_object):
        instance = doiorg.DoiorgPlugin()
        urls = instance.get_pdf_urls(TEST_DOI, cache_mode=CacheMode.REFRESH)
    assert urls == [doiorg_url]
