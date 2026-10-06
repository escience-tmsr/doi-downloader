# doi-downloader

[![PyPI Version](https://img.shields.io/pypi/v/tmsr-doi-downloader)][PyPI-url]
[![docs](https://github.com/escience-tmsr/doi-downloader/actions/workflows/docs.yml/badge.svg)][docs-url]
[![github license badge](https://img.shields.io/github/license/escience-tmsr/doi-downloader)](https://github.com/escience-tmsr/doi-downloader)
[![CI](https://github.com/escience-tmsr/doi-downloader/actions/workflows/main.yml/badge.svg)](https://github.com/escience-tmsr/doi-downloader/actions/workflows/main.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/escience-tmsr/doi-downloader/main.svg)](https://results.pre-commit.ci/latest/github/escience-tmsr/doi-downloader/main)

DOI-downloader lets you download PDFs of scientific articles by providing the
DOI. It can search in several places and will automatically follow any redirects
needed to obtain the PDF.

## Usage

Download an article by providing the DOI as an argument:

```bash
doi-downloader 10.1038/s41586-020-2649-2
doi-downloader 10.1038/s41586-020-2649-2 -o downloads  # specify output location
```

A list of DOIs in a plain text file can be passed in using `--file`:

```bash
doi-downloader --file dois.txt  # one DOI per line
```

Run `doi-downloader --help` for all options, and see the [usage documentation] for details.

## Installation

If you have [`uv`] on your system, you can directly run doi-downloader with:

```bash
uvx --from tmsr-doi-downloader doi-downloader 10.1038/s41586-020-2649-2
```

### Install as a command line tool

For repeated usage, we recommend explicitly installing it as a command line tool
using e.g. [`uv`] or [`pipx`].

```bash
uv tool install tmsr-doi-downloader
# or
pipx install tmsr-doi-downloader
```

Once installed, you can run `doi-downloader` as a command from your command line.

### As a Python library

To use doi-downloader as a Python library, you can install it with `pip` (or
`uv pip`). Once installed, it is available to import

```python
from doi_downloader import doi_downloader as ddl

doi = "10.1038/s41586-020-2649-2"
ddl.download(doi, output_dir="downloads")
```

Check [examples](./examples) for examples of how to use.

## Developer instructions

To contribute to doi-downloader, clone the repository and use the provided
`make install` command.

```bash
git clone git@github.com:escience-tmsr/doi_downloader.git
cd doi_downloader
make virtualenv
source .venv/bin/activate
make install
```

Included tests can be run with:

```bash
make test
```

## Adding new source adapters

Create a new file in the `plugins` directory, and implement the `Plugin` class. The class should implement the following methods:

- `get_pdf_urls`: This method should return the PDF URL for the given DOI.
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

Check the documentation at [https://escience-tmsr.github.io/doi-downloader][docs-url].


<!-- References -->

[PyPI-url]:             https://pypi.org/project/tmsr-doi-downloader/
[docs-url]:             https://escience-tmsr.github.io/doi-downloader/
[usage documentation]:  https://escience-tmsr.github.io/doi-downloader/usage/
[`uv`]:                 https://docs.astral.sh/uv/
[`pipx`]:               https://pipx.pypa.io/stable/
