# Examples

## Using a single plugin

In this example we will use the Unpaywall plugin to fetch PDF URLs for a list of DOIs.

```python
from doi_downloader import loader as ld
plugins = ld.plugins
upw = plugins['UnpaywallPlugin']
doi = "10.1038/s41586-020-2649-2"
pdf_url = upw.get_pdf_url(doi)
```

## Reading dois from a CSV file

In this example we will read DOIs from a CSV file and use the Unpaywall plugin to fetch PDF URLs for each DOI.

```python
    from doi_downloader import loader as ld
    from doi_downloader import csv
    unique_dois = csv.load_dois_from_file(dois_file_path, "doi", unique=True)

    plugins = ld.plugins
    upw = plugins['UnpaywallPlugin']

    for doi in unique_dois:
        pdf_url = upw.get_pdf_url(doi, use_cache=True)
        print(f'{doi}: {pdf_url}')
```

## Attempt to download the PDF

In this example we will attempt to download the PDF for a list of DOIs using the Unpaywall plugin.

```python
    from doi_downloader import loader as ld
    from doi_downloader import csv
    from doi_downloader import pdf_download as pdf_dl
    unique_dois = csv.load_dois_from_file(dois_file_path, "doi", unique=True)

    plugins = ld.plugins
    upw = plugins['UnpaywallPlugin']

    for doi in unique_dois:
        pdf_url = upw.get_pdf_url(doi, use_cache=True)
        if pdf_url:
            # Sanitize DOI for filename
            safe_filename = doi.replace("/", "_").replace(".", "_") + ".pdf"
            downloaded_file = pdf_dl.download_pdf(url, safe_filename, output_dir)
            if downloaded_file:
                print(f"Downloaded {doi} to {downloaded_file}")
            else:
                print(f"Failed to download {doi}")


```

## Using multiple plugins

In this example we will use all plugins through a helper function that will attempt to download the PDFs.

```python
from doi_downloader import doi_downloader as ddl
from doi_downloader import csv

dois_file_path = "dois.csv"
unique_dois = csv.load_dois_from_file(dois_file_path, "doi", unique=True)
for doi in unique_dois:
    ddl.download(doi, output_dir="downloads", force_download=True)

```
