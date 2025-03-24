from doi_downloader.plugins import crossref
import responses
#
#
# # Read API keys and other sensitive data from environment variables
TEST_DOI="10.1007/s10207-021-00566-3"
TEST_FILE="10.1007_s10207-021-00566-3.pdf"
CROSSREF_API_URL = "https://api.crossref.org/works/{doi}"
JSON_RESPONSE = {"status":"ok","message-type":"work","message-version":"1.0.0","message":{"publisher":"Springer Science and Business Media LLC","issue":"3","DOI":"10.1007/s10207-021-00566-3","type":"journal-article","created":{"date-parts":[[2021,9,14]],"date-time":"2021-09-14T12:11:27Z","timestamp":1631621487000},"title":["A risk-level assessment system based on the STRIDE/DREAD model for digital data marketplaces"],"author":[{"ORCID":"https://orcid.org/0000-0002-8039-1800","given":"Lu","family":"Zhang","sequence":"first","affiliation":[]},{"given":"Arie","family":"Taal","sequence":"additional","affiliation":[]},{"given":"Reginald","family":"Cushing","sequence":"additional","affiliation":[]},{"given":"Cees","family":"de Laat","sequence":"additional","affiliation":[]},{"given":"Paola","family":"Grosso","sequence":"additional","affiliation":[]}],"published-online":{"date-parts":[[2021,9,14]]},"link":[{"URL":"https://link.springer.com/content/pdf/10.1007/s10207-021-00566-3.pdf","content-type":"application/pdf","content-version":"vor","intended-application":"text-mining"},{"URL":"https://link.springer.com/article/10.1007/s10207-021-00566-3/fulltext.html","content-type":"text/html","content-version":"vor","intended-application":"text-mining"},{"URL":"https://link.springer.com/content/pdf/10.1007/s10207-021-00566-3.pdf","content-type":"application/pdf","content-version":"vor","intended-application":"similarity-checking"}],"issued":{"date-parts":[[2021,9,14]]},"URL":"https://doi.org/10.1007/s10207-021-00566-3"}}

@responses.activate
def test_get_url():
    crf = crossref.CrossrefPlugin()
    crf_url = CROSSREF_API_URL.format(doi=TEST_DOI)
    responses.add(responses.GET, crf_url,
                  json=JSON_RESPONSE,
                  status=200)


    url = crf.get_pdf_url(TEST_DOI, use_cache=False)
    assert url =='https://link.springer.com/content/pdf/10.1007/s10207-021-00566-3.pdf'
#
