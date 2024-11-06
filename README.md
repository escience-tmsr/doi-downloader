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

```python
from doi_downloader import unpaywall
unpaywall.set_email("youremail@domain.com")
unpaywall.download_from_doi("somedoi")

```
