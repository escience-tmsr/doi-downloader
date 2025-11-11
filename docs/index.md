## Welcome to doi_downloader

`doi_downloader` provides an efficient way to download PDFs given a list of DOIs. `doi_downloader` supports multiple 
sources and can be extended with new plugins. Plugins are adaptors to online API services that can provide PDF URLs 
given a DOI. `doi_downloader` makes a great choice for researchers and developers who need to download PDFs from DOIs.

Current plugins include:

- **Crossref**: A widely used service for retrieving metadata and content associated with DOIs.
- **Unpaywall**: A service that provides access to open access versions of scholarly articles.
- **CORE**: A service that aggregates open access research outputs from repositories and journals worldwide
  (requires API key)
- **SerpApi**: A service that provides access to search engine results, including scholarly articles 
  (requires API key).
