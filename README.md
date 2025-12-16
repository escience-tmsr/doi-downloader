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

## Benchmarking plugin performance

This repository has code to measure, benchmark and analyse the coverage or performance of all API plugins used with doi-downloader. Performance means the ability of the plugins to find and download the PDF articles associated with a given list of DOIs (ratio of successfully downloaded PDFs to failed downloads). To run the benchmark you have to:

1. Install the required libraries of this repo by following the instructions under the "Install" section above.
2. Ensure you have procured the relevant API keys of the plugins you use.
3. Add the API keys as environment variables to your operating system. [Here](https://www3.ntu.edu.sg/home/ehchua/programming/howto/Environment_Variables.html) is a useful reference for how to do this on different operating systems. 
4. Ensure you have a CSV file with two (or more) columns. One column should have a header called "doi" and hold the DOI for a paper. The second column should have a header called "domain" which holds the journal name or domain of the journal website (not URL, just the domain name) where the paper metadata can be viewed. You can then run the benchmark code using this command:

``` python -m benchmark.batch_download path/to/csv/file.csv ```

After execution, generated data for analysis can be found under ``` benchmark/logs/... ``` and ``` benchmark/reports/... ```

To get a summary of the top performing plugins and journals run (ensure you have run the above command first):

``` python -m benchmark.get_top_performers ```

After execution, the results are written to ``` benchmark/reports/top_performers.txt ```

## Read the docs

Check the documentaion at [https://escience-tmsr.github.io/doi-downloader/](https://escience-tmsr.github.io/doi-downloader/).
