## Creating a new plugin

To extend the functionality of `doi_downloader`, you can create a new plugin for retrieving PDFs related to DOI from 
a specific website. A plugin is a Python module that implements the `Plugin` interface. Below is a step-by-step guide 
to creating a new plugin.

### Step 1: Create a new Python file

Create a new Python file in the `doi_downloader/plugins` directory or (for testing only) in the directory 
`doi_downloader/extra_plugins`. The name of the file should be descriptive of the plugin's functionality, 
for example, `my_plugin.py`. Plugins stored in the `extra_plugins` directory, will not be stored on Github.

### Step 2: Implement the Plugin interface

In your new Python file, you need to implement the `Plugin` interface. Most plugins only make a single HTTP request,
so rather than implementing `fetch_metadata` directly, implement two smaller methods instead: `make_url` (return the
URL to fetch for a DOI) and `process_webpage` (parse a successful response into an `ArticleDataObject`). The base
`Plugin.fetch_metadata` handles the request itself, all the common failure modes (HTTP errors, timeouts, connection
errors, unparseable responses), and always returns an `ArticleDataObject` -- even when the request failed, so the
attempted URL stays available for post-processing analysis instead of vanishing. Here is an example:

```python
from doi_downloader.plugins import Plugin

MY_API_URL = "https://example.com/{doi}"

class MyPlugin(Plugin):
    def make_url(self, doi):
        return MY_API_URL.format(doi=doi)

    def process_webpage(self, response, doi, data_object):
        paper = response.json()
        title = paper.get("title", "N/A")
        download_link = paper.get("downloadUrl", "N/A")
        data_object.set_title(title)
        if download_link:
            data_object.add_pdf_link(response.url, download_link)
```

`add_pdf_link(fetch_url, url)` ties every pdf link to the page it was found on (`fetch_url`, typically `response.url`),
since a plugin can make more than one request and later analysis may need to know which page a link came from.

Two more hooks are available if a plugin needs them:

- `request_headers(self, doi)`: return a dict to replace the default browser-like request headers (e.g. for an
  `Authorization` header), or `None` (the default) to use the default headers.
- `request_params(self, doi)`: return a dict of query string parameters to include in the request, or `None`
  (the default) for none.

If a plugin's shape doesn't fit this (e.g. it needs to make more than one request, like `googlescholar.py` fetching
both a search API and the publisher page it points to), override `fetch_metadata(self, doi)` directly instead of
`make_url`/`process_webpage`. It should still always return an `ArticleDataObject`, never `None`, even on failure.

### Step 3: Loading and testing the plugin

The `doi_downloader` loader module will automtically load all plugin files in the `plugins` or `extra_plugins` directory. You can test your plugin by loading your plugin withthis script:

```python
from doi_downloader import loader as ld

doi = "10.1000/xyz123"
metadata = ld.plugins["MyPlugin"].fetch_metadata(doi)
pdf_urls = ld.plugins["MyPlugin"].get_pdf_urls(doi)
```

### Step 4: Caching API results

Caching is handled centrally by the `Plugin` base class, so a new plugin does not need to implement it. `Plugin.__init__` already
sets up `self.cache = Cache("database.db", self.plugin_name)`, and the inherited `get_pdf_urls(doi, cache_mode=CacheMode.CACHE_FIRST, ttl=10)`
method reads from and writes to that cache around your `fetch_metadata` call. You only need to implement `fetch_metadata`; `get_pdf_urls`
is inherited as-is.

`cache_mode` (from `doi_downloader.plugins.CacheMode`) controls how the cache is used:

- `CacheMode.REFRESH`: skip the cache, call `fetch_metadata`, and store the result.
- `CacheMode.CACHE_ONLY`: read from the cache only; return an empty list if there is no cached data.
- `CacheMode.CACHE_FIRST` (default): try the cache first, falling back to `REFRESH` behavior if there is no cached data.

```python
from doi_downloader import loader as ld
from doi_downloader.plugins import CacheMode

doi = "10.1000/xyz123"
pdf_urls = ld.plugins["MyPlugin"].get_pdf_urls(doi, cache_mode=CacheMode.CACHE_FIRST)
```

The available plugins in the [doi_downloader/plugins](https://github.com/escience-tmsr/doi-downloader/tree/main/doi_downloader/plugins) directory can be inspected for more example plugins code. 
