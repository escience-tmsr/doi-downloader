## Welcome to doi_downloader

`doi_downloader` provides an efficient way to download PDFs of research papers given a list of DOIs. `doi_downloader` 
supports multiple paper repositories and can be extended with plugins servicing other sources. Plugins are adaptors 
to online API services that can provide PDF URLs given a DOI. `doi_downloader` makes a great choice for researchers 
and developers who are looking for PDFs of research papers related to DOIs.

Current plugins include:

- **Crossref**: A widely used service for retrieving metadata and content associated with DOIs.
- **Unpaywall**: A service that provides access to open access versions of scholarly articles.
- **CORE**: A service that aggregates open access research outputs from repositories and journals worldwide
  (requires API key)
- **SerpApi**: A service that provides access to search engine results, including scholarly articles 
  (requires API key).
