from doi_downloader.plugins import doiorg
import doi_downloader.plugins.doiorg
from unittest.mock import patch
import responses

TEST_DOI="10.1007/s10207-021-00566-3"
TEST_FILE="10.1007_s10207-021-00566-3.pdf"
DOIORG_URL = "https://doi.org/{doi}"
JSON_RESPONSE={"authors":[{"name":"Cushing, R."},{"name":"de Laat, C."},{"name":"Grosso, P."},{"name":"Taal, A."},{"name":"Zhang, L."}],"createdDate":"2022-10-18T21:17:06","doi":"10.1007/s10207-021-00566-3","downloadUrl":"https://core.ac.uk/download/543085677.pdf","id":129955321,"identifiers":[{"identifier":"555948398","type":"CORE_ID"},{"identifier":"oai:dare.uva.nl:publications/a9eecfc0-ac04-4f45-901c-334f5eb158cb","type":"OAI_ID"},{"identifier":"539447873","type":"CORE_ID"},{"identifier":"oai:dare.uva.nl:openaire_cris_publications/a9eecfc0-ac04-4f45-901c-334f5eb158cb","type":"OAI_ID"},{"identifier":"543085677","type":"CORE_ID"},{"identifier":"10.1007/s10207-021-00566-3","type":"DOI"},{"identifier":"565293126","type":"CORE_ID"}],"title":"A risk-level assessment system based on the STRIDE/DREAD model for digital data marketplaces","language":{"code":"en","name":"English"},"oaiIds":["oai:dare.uva.nl:publications/a9eecfc0-ac04-4f45-901c-334f5eb158cb","oai:dare.uva.nl:openaire_cris_publications/a9eecfc0-ac04-4f45-901c-334f5eb158cb"],"publishedDate":"2022-06-01T01:00:00","publisher":"'Springer Science and Business Media LLC'","sourceFulltextUrls":["https://pure.uva.nl/ws/files/88132416/s10207_021_00566_3.pdf"],"updatedDate":"2023-10-26T14:57:01","yearPublished":2022,"links":[{"type":"download","url":"https://core.ac.uk/download/543085677.pdf"},{"type":"reader","url":"https://core.ac.uk/reader/543085677"},{"type":"thumbnail_m","url":"https://core.ac.uk/image/543085677/large"},{"type":"thumbnail_l","url":"https://core.ac.uk/image/543085677/large"},{"type":"display","url":"https://core.ac.uk/works/129955321"}]}

@responses.activate
def test_get_url():
    doiorg_url = DOIORG_URL.format(doi=TEST_DOI)

    with patch.object(doi_downloader.plugins.doiorg.AAADoiorgPlugin, "fetch_metadata", return_value=doiorg_url):
        instance = doiorg.AAADoiorgPlugin()
        url = instance.get_pdf_url(TEST_DOI, use_cache=False)
    assert url == doiorg_url

