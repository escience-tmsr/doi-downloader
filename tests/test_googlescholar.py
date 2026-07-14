# claude code
import pytest
import responses
from doi_downloader import lib
from doi_downloader.plugins import googlescholar

TEST_DOI = "10.1007/s10207-021-00566-3"

PUBLISHER_LINK = f"https://link.springer.com/article/{TEST_DOI}"
PDF_LINK = f"https://link.springer.com/content/pdf/{TEST_DOI}.pdf"
ROBOTS_TXT_URL = "https://link.springer.com/robots.txt"

UNMATCHED_PUBLISHER_LINK = "https://link.springer.com/article/other-paper"
UNMATCHED_PDF_LINK = "https://link.springer.com/content/pdf/other-paper.pdf"


# checked
@pytest.fixture(autouse=True)
def test_wrapper_always_run(monkeypatch):
    """Avoid needing a real SERPAPI_KEY, real sleeps, and robots.txt caching
    bleeding between tests (get_robots_txt is memoized with functools.cache)."""
    monkeypatch.setattr(googlescholar, "SERPAPI_KEY", "test-serpapi-key")
    monkeypatch.setattr(lib.time, "sleep", lambda seconds: None)
    lib.get_robots_txt.cache_clear()

    yield
    
    lib.get_robots_txt.cache_clear()


# checked
def make_matched_serpapi_response():
    return {"organic_results": [{
        "title": "Example title",
        "link": PUBLISHER_LINK,
        "resources": [{"link": PDF_LINK}],
    }]}


# checked
def make_unmatched_serpapi_response():
    return {"organic_results": [{
        "title": "Example title",
        "link": UNMATCHED_PUBLISHER_LINK,
        "resources": [{"link": UNMATCHED_PDF_LINK}],
    }]}


# checked
# @responses.activate is not necessary for helper functions
def mock_robots_txt_allowed():
    responses.add(responses.GET, ROBOTS_TXT_URL, status=404)


# checked
@responses.activate
def test_get_pdf_urls_uses_cache(monkeypatch):
    plugin = googlescholar.GoogleScholarSerpAPIPlugin()
    cached_object = googlescholar.ado.ArticleDataObject(None)
    cached_object.set_title("Cached title")
    cached_object.set_doi(TEST_DOI)
    cached_object.add_pdf_link(PDF_LINK)
    monkeypatch.setattr(plugin.cache, "get_cache", lambda doi, ttl=0: cached_object.to_json())

    urls = plugin.get_pdf_urls(TEST_DOI, read_from_cache=True)

    assert urls == [PDF_LINK]


# checked
@responses.activate
def test_get_pdf_urls_verified_by_url():
    plugin = googlescholar.GoogleScholarSerpAPIPlugin()
    responses.add(responses.GET, googlescholar.SERPAPI_SEARCH_URL,
                  json=make_matched_serpapi_response(),
                  status=200)
    mock_robots_txt_allowed()
    responses.add(responses.GET, PUBLISHER_LINK,
                  body="<html><body>No PDF markers here</body></html>", status=200)

    urls = plugin.get_pdf_urls(TEST_DOI, read_from_cache=False, save_to_cache=False)

    assert urls == [PDF_LINK]


# checked
@responses.activate
def test_get_pdf_urls_no_organic_results():
    plugin = googlescholar.GoogleScholarSerpAPIPlugin()
    responses.add(responses.GET, googlescholar.SERPAPI_SEARCH_URL,
                  json={"organic_results": []}, status=200)

    urls = plugin.get_pdf_urls(TEST_DOI, read_from_cache=False, save_to_cache=False)

    assert urls == []


# checked
@responses.activate
def test_fetch_metadata_verified_by_metadata_tier():
    plugin = googlescholar.GoogleScholarSerpAPIPlugin()
    responses.add(responses.GET, googlescholar.SERPAPI_SEARCH_URL,
                  json=make_unmatched_serpapi_response(),
                  status=200)
    mock_robots_txt_allowed()
    # the publisher page itself mentions the DOI, even though the SerpAPI
    # links did not, so verification should succeed on the metadata tier
    responses.add(responses.GET, UNMATCHED_PUBLISHER_LINK,
                  body=f"<html><body>Published version of DOI {TEST_DOI}</body></html>",
                  status=200)

    metadata = plugin.fetch_metadata(TEST_DOI)

    assert metadata.get_pdf_links() == [UNMATCHED_PDF_LINK]
    assert metadata.data["links_verified"] is True


# checked
@responses.activate
def test_fetch_metadata_unverified_when_doi_not_found_anywhere():
    plugin = googlescholar.GoogleScholarSerpAPIPlugin()
    responses.add(responses.GET, googlescholar.SERPAPI_SEARCH_URL,
                  json=make_unmatched_serpapi_response(),
                  status=200)
    mock_robots_txt_allowed()
    responses.add(responses.GET, UNMATCHED_PUBLISHER_LINK,
                  body="<html><body>Unrelated article content</body></html>", status=200)

    metadata = plugin.fetch_metadata(TEST_DOI)

    assert metadata.get_pdf_links() == [UNMATCHED_PDF_LINK]
    assert metadata.data["links_verified"] is False


# checked
def test_fetch_metadata_missing_api_key(monkeypatch):
    monkeypatch.setattr(googlescholar, "SERPAPI_KEY", None)
    plugin = googlescholar.GoogleScholarSerpAPIPlugin()

    with pytest.raises(EnvironmentError):
        plugin.fetch_metadata(TEST_DOI)


# checked
def test_verify_links_by_url_matches_pdf_link():
    plugin = googlescholar.GoogleScholarSerpAPIPlugin()
    assert plugin.verify_links_by_url(TEST_DOI, UNMATCHED_PUBLISHER_LINK, [PDF_LINK]) is True


# checked
def test_verify_links_by_url_matches_publisher_link():
    plugin = googlescholar.GoogleScholarSerpAPIPlugin()
    assert plugin.verify_links_by_url(TEST_DOI, PUBLISHER_LINK, []) is True


# checked
def test_verify_links_by_url_no_match():
    plugin = googlescholar.GoogleScholarSerpAPIPlugin()
    assert plugin.verify_links_by_url(
        TEST_DOI, UNMATCHED_PUBLISHER_LINK, [UNMATCHED_PDF_LINK]) is False


# checked
@responses.activate
def test_verify_link_by_html_match():
    plugin = googlescholar.GoogleScholarSerpAPIPlugin()
    responses.add(responses.GET, PUBLISHER_LINK,
                  body=f"<html>DOI: {TEST_DOI}</html>", status=200)

    assert plugin.verify_link_by_html(TEST_DOI, PUBLISHER_LINK) is True


# checked
@responses.activate
def test_verify_link_by_html_no_match():
    plugin = googlescholar.GoogleScholarSerpAPIPlugin()
    responses.add(responses.GET, PUBLISHER_LINK,
                  body="<html>Unrelated content</html>", status=200)

    assert plugin.verify_link_by_html(TEST_DOI, PUBLISHER_LINK) is False
