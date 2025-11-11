## Examples

### Using a single plugin for retrieving the PDF URL related to a DOI

This example uses the Crossref plugin to fetch a PDF URLs for a DOI. Note that the plugin call only tries to retrieve an URL. 
It does not try to fetch a PDF. 

```python
from doi_downloader import loader as ld

doi = "10.1038/s41586-020-2649-2"
pdf_url = ld.plugins['CrossrefPlugin'].get_pdf_url(doi)
print(f'{doi}: {pdf_url}')
```

The names of the plugins in the code are: `CoreacukPlugin`, `CrossrefPlugin`, `GoogleScholarSerpAPIPlugin` and
`UnpaywallPlugin`. Not all plugins are successful in recovering a URL for the example DOI.

### Reading DOIs from a CSV file and retrieving the PDF URLs

This example reads DOIs from a CSV file and uses the Crossref plugin to fetch a PDF URL for each DOI.

```python
from doi_downloader import csv, loader as ld
import os

doi_list = csv.load_dois_from_file(os.path.abspath("doi_examples.csv"), "doi")
for doi in doi_list:
    pdf_url = ld.plugins['CrossrefPlugin'].get_pdf_url(doi, use_cache=True)
    print(f'{doi}: {pdf_url}')
```

###  Reading DOIs from a CSV file and retrieving the PDFs

This example reads DOIs from a CSV file, uses the Crossref plugin to fetch a PDF URL and tries to download the associated PDF.

```python
from doi_downloader import csv, loader as ld, pdf_download as pdf_dl

doi_list = csv.load_dois_from_file(os.path.abspath("doi_examples.csv"), "doi")
for doi in doi_list:
    pdf_url = ld.plugins['CrossrefPlugin'].get_pdf_url(doi, use_cache=True)
    if pdf_url:
        safe_filename = doi.replace("/", "_").replace(".", "_") + ".pdf"
        downloaded_file = pdf_dl.download_pdf(pdf_url, safe_filename, "downloads")
        if downloaded_file:
            print(f"Downloaded {doi} to {downloaded_file}")
    if not pdf_url or not downloaded_file:
        print(f"Failed to download {doi} ({pdf_url})")
```

### Using multiple plugins for retrieving the PDFs

This example uses all plugins through a helper function that attempts to download the PDFs.

```python
from doi_downloader import csv, doi_downloader as ddl
import os

doi_list = csv.load_dois_from_file(os.path.abspath("doi_examples.csv"), "doi")
for doi in doi_list:
    ddl.download(doi, output_dir="downloads", force_download=True)
```
