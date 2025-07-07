# doi-downloader

## Install

```bash
make virtualenv
source .venv/bin/activate
make install
```

## Test

```bash
make test

```

## Use

### Simple example

```python
from doi_downloader import doi_downloader as ddl
doi = "10.1038/s41586-020-2649-2"
ddl.download(doi, output_dir="downloads")
```

Check [examples](./examples) for examples of how to use.

## Adding new source adapters

Create a new file in the `plugins` directory, and implement the `Plugin` class. The class should implement the following methods:

- `get_pdf_url`: This method should return the PDF URL for the given DOI.
- `fetch_metadata`: This method should return the metadata for the given DOI.
