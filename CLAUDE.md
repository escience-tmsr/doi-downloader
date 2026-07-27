# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Goal

`doi_downloader` is software for downloading PDFs of research papers given their DOI. The software employs various Python plugins which use different strategies or databases for finding an online location of a PDF related to a given DOI. When found, the software passes the address of the PDF to a separate function for downloading the PDF.

## Policies

`doi_downloader` aims at performing its task in a legal and ethical way;

- Do not retrieve data from pirate web sites. Keep a blacklist of such sites and avoid visiting them
- Do not access contents from a website when its configuration file robots.txt prohibits bot access
- Do not access contents from a website when its terms of use prohibits bot access (hard to implement)
- Be gentle to target web sites and use a waiting period before revisiting a web site

## Commands

```bash
make virtualenv          # create .venv and install project + test deps
source .venv/bin/activate
make install              # pip install -e .[test] (rerun after changing requirements*.txt)

make fmt                  # format doi_downloader/ with ruff
make lint                 # ruff check doi_downloader/
make test                 # lint, then pytest with coverage (fails fast: --maxfail=1)
make docs                 # build mkdocs site into site/
make docs-serve           # serve built docs at localhost:8000
```

Run a single test or file directly with pytest, bypassing the Makefile's lint-then-test chain:

```bash
pytest tests/test_crossref.py -v
pytest tests/test_crossref.py::test_get_pdf_urls_uses_cache -v
```

CI (`.github/workflows/main.yml`) runs `make lint` then `make test` on Linux/macOS/Windows for Python 3.12, and requires the linter job to pass first. CONTRIBUTING.md states the project targets 100% coverage on new code.

There is no `pyproject.toml`; dependencies are pinned in `requirements.txt` (runtime) and installed via `setup.py`'s `install_requires`. `make switch-to-poetry` exists but switches the whole project to Poetry and is not the current setup — don't assume Poetry is in use.

For testing the syntax of CITATION.cff (requires installation of `cffconvert` with `pipx`):

```bash
cffconvert --validate
```

For testing the quality of the repository (requires installation of `https://github.com/EVERSE-ResearchSoftware/QualityPipelines`):

```bash
resqui -u https://github.com/escience-tmsr/doi-downloader -t $GITHUB_ACTION_TOKEN
```

Note that `resqui` requires a Github action token being provided via the command-line arguments, not via the environment

## Environment configuration

Plugins that need credentials read them from a `.env` file in the repo root (loaded via `python-dotenv`, see `doi_downloader/plugins/__init__.py`). Copy `test.env` to `.env` and fill in real values. Variables in use:

- `UNPAYWALL_EMAIL` — required by the Unpaywall plugin (an email address, not a real API key)
- `SERPAPI_KEY` — required by the Google Scholar plugin
- `CORE_API_KEY` — required by the CORE plugin

Tests load `.env` via `pytest.ini`'s `env_files` (pytest-dotenv), and `tests/conftest.py` runs every test inside a temp cwd, so tests never touch the real `database.db` or `downloads/` in the repo root.

## Architecture

`doi_downloader.doi_downloader.download(doi, ...)` is the main entry point. It iterates all loaded plugins in alphabetical order by class name, and for each one:
1. calls `plugin.get_pdf_urls(doi)` to resolve candidate PDF URLs,
2. passes the first URL to `pdf_download.download_pdf()`, which checks `robots.txt` (`lib.robot_access_allowed`), fetches the file, verifies it's a real PDF (`is_valid_pdf` on the `%PDF` magic bytes), and checks the DOI string appears in the extracted text (`verify_pdf`),
3. stops at the first plugin that produces a verified download.

Every attempt (success or failure) should be recorded via `BenchmarkLogger` (`doi_downloader/benchmark.py`) to a JSONL log under `benchmark/logs/`; `BenchmarkAnalyzer` turns those logs into per-plugin/per-journal success-rate reports. This is separate from the `benchmark/` top-level directory, which holds the batch-evaluation CLI (`python -m benchmark.batch_download <csv>` and `python -m benchmark.get_top_performers`) used to score plugins against a labeled DOI list — see README.md's "Benchmarking plugin performance" section.

### Plugin system

- All source adapters live in `doi_downloader/plugins/` (e.g. `coreacuk.py`, `crossref.py`, `doiorg.py`, `googlescholar.py`, `unpaywall.py`) and subclass `Plugin` (`doi_downloader/plugins/__init__.py`), implementing `test`, `fetch_metadata`, and `get_pdf_urls`.
- `doi_downloader/loader.py` discovers plugins at import time by dynamically loading every `.py` file (except `__init__.py`) in `doi_downloader/plugins/` **and** `doi_downloader/extra_plugins/` (the latter is gitignored — used for local/experimental plugins that shouldn't be committed), then instantiating every `Plugin` subclass found. The resulting `{ClassName: instance}` dict is `loader.plugins`.
- Each plugin typically owns its own cache table via `cache_duckdb.Cache("database.db", "<plugin_name>")` — one DuckDB file, one table per plugin, keyed by DOI. There's also an older `cache.py` (sqlite3-based) that some code paths may still reference; new plugins should use `cache_duckdb`.
- `article_dataobject.ArticleDataObject` is the shared metadata model plugins return/cache: it validates against a JSON schema and has factory constructors (`from_crossref_json`, `from_unpaywall_json`, `from_json`) plus `to_json()` for cache storage.
- See `docs/writing_a_plugin.md` for the full walkthrough of adding a new plugin, including the caching pattern.

### Other component

- `benchmark/` (top-level) is the batch evaluation harness (distinct from `doi_downloader/benchmark.py`'s per-call logging described above).

## Release process

Releases are cut with `make release`, which prompts for a semver version, writes `doi_downloader/VERSION`, regenerates `HISTORY.md` via `gitchangelog`, commits, and pushes a matching git tag. `.github/workflows/release.yml` then builds and publishes to PyPI on tag push (`PYPI_API_TOKEN` secret required). Commit messages should follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) (per CONTRIBUTING.md).
