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

Check [examples](./examples) for examples of how to use.

## Adding new source adapters

Create a new file in the `plugins` directory, and implement the `Plugin` class. The class should implement the following methods:

- `get_pdf_url`: This method should return the PDF URL for the given DOI.
- `fetch_metadata`: This method should return the metadata for the given DOI.
