# Usage

## Simple example

In this simple example we will download a PDF file from a DOI. The download function will iterate through all the plugins and try to find the PDF URL for the given DOI. If it finds a plugin that can handle the DOI, it will download the PDF file and save it to the specified output directory.

```python
from doi_downloader import doi_downloader as ddl
doi = "10.1038/s41586-020-2649-2"
ddl.download(doi, output_dir="downloads")
```

## More examples

See [Examples](examples.md) for more examples of how to use the `doi_downloader` package.
