# Welcome to doi_downloader

The scope of `doi_downloader` is to provide a simple and efficient way to download PDFs from DOIs. It supports multiple sources and can be easily extended with new plugins.
Plugins are adaptors to online API services that can provide PDF URLs given a DOI. The library is designed to be easy to use and extend, making it a great choice for researchers and developers who need to download PDFs from DOIs.
urrent plugins include:

- **Crossref**: A widely used service for retrieving metadata and content associated with DOIs.
- **Unpaywall**: A service that provides access to open access versions of scholarly articles.
- **CORE**: A service that aggregates open access research outputs from repositories and journals worldwide.
