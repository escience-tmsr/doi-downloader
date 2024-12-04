# Examples

## use_unpaywall.py

This script show the basic usage of the Unpaywall class. It will get the PDF URL for a given DOI. It will load a list of DOIs from a CSV file using the column name "doi".

```bash
python examples/use_unpaywall.py -f examples/data/doi_list.csv

```

## check_unpaywall_cache.py

This script will check the Unpaywall cache for a given DOI and return the JSON result if it exists. It will parse the JSON to find the PDF URL. Finally it will calculate the percentage of DOIs with no URLs in the cache.

```bash
python examples/check_unpaywall_cache.py
```
