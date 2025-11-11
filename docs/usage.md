## Usage

### Example

In this example, we try to download a PDF file given a DOI, from a Python program or a Jupyter notebook. We call the
download function, which will iterate through all the available plugins and try to find a PDF URL for the given 
DOI. If a plugin finds a URL related to the DOI, an attempt will be made to download the PDF file and save it to 
the specified output directory:

```python
from doi_downloader import doi_downloader as ddl

doi = "10.1038/s41586-020-2649-2"
ddl.download(doi, output_dir="downloads")
```

### More examples

See [Examples](examples.md) for more examples of how to use the `doi_downloader` package.
