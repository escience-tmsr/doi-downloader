## Usage

This text contains five examples of how `doi_downloader` can be used.

### 1. Download a PDF file given a DOI

In this example, we try to download a PDF file given a DOI, from a Python program or a Jupyter notebook. We call the
download function, which will iterate through all the available plugins and try to find a PDF URL for the given 
DOI. If a plugin finds a URL related to the DOI, an attempt will be made to download the PDF file and save it to 
the specified output directory:

```python
from doi_downloader import doi_downloader as ddl

doi = "10.1038/s41586-020-2649-2"
ddl.download(doi, output_dir="downloads")
```

The download function will return the location of the downloaded PDF file, if the download was successful. In other 
cases, the download will return `False`.

### 2. Using a single plugin for retrieving the PDF URL related to a DOI

This example uses the Crossref plugin to fetch a PDF URL for a DOI. Note that the plugin call only tries to retrieve an URL. 
It does not try to fetch a PDF. 

```python
from doi_downloader import loader as ld

doi = "10.1038/s41586-020-2649-2"
pdf_url = ld.plugins['CrossrefPlugin'].get_pdf_url(doi)
print(f'{doi}: {pdf_url}')
```

The names of the plugins in the code are: `CoreacukPlugin`, `CrossrefPlugin`, `GoogleScholarSerpAPIPlugin` and
`UnpaywallPlugin`. Not all plugins are successful in recovering a URL for the example DOI. If a plugin cannot
find a URL for the DOI, it will return `None`.

### 3. Reading DOIs from a CSV file and retrieving the PDF URLs

This example reads DOIs from a CSV file and uses the Crossref plugin to fetch a PDF URL for each DOI.

```python
from doi_downloader import csv, loader as ld
import os

doi_list = csv.load_dois_from_file(os.path.abspath("doi_examples.csv"), "doi")
for doi in doi_list:
    pdf_url = ld.plugins['CrossrefPlugin'].get_pdf_url(doi, use_cache=True)
    print(f'{doi}: {pdf_url}')
```

The example file contains two DOIs. The plugin finds a URL for one of them but not for the other.

### 4. Reading DOIs from a CSV file and retrieving the PDFs

This example reads DOIs from a CSV file, uses the Crossref plugin to fetch a URL and tries to download the 
associated PDF.

```python
from doi_downloader import csv, loader as ld, pdf_download as pdf_dl
import os

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

The example file contains two DOIs. The plugin finds a URL for one of them and manages to download a PDF from the URL. 
For the other DOI, no URL was found.

### 5. Using multiple plugins for retrieving the PDFs

This example uses all plugins through a helper function `ddl.download` that attempts to download the PDFs.

```python
from doi_downloader import csv, doi_downloader as ddl
import os

doi_list = csv.load_dois_from_file(os.path.abspath("doi_examples.csv"), "doi")
for doi in doi_list:
    if ddl.download(doi, output_dir="downloads", force_download=True):
        print(f"Download successful for doi {doi}")
```

The plugins will be called in alphabetical order of the names until one of them finds a URL from which a PDF can
be downloaded. Other plugins will not be called. If plugin finds a url, it will print a message. When a download
is successful, an extra message is shown.
