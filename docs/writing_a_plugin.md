# Creating a new plugin

To extend the functionality of `doi_downloader`, you can create a new plugin. A plugin is a Python module that implements the `Plugin` interface. Below is a step-by-step guide to creating a new plugin.

## Step 1: Create a new Python file

Create a new Python file in the `plugins` or `extra_plugins` directory. `extra_plugins` folder if plugins that you do not want to commit to GitHub since the folder is ignored. The name of the file should be descriptive of the plugin's functionality, for example, `my_plugin.py`.

## Step 2: Implement the Plugin interface

In your new Python file, you need to implement the `Plugin` interface. This involves creating a class that inherits from `Plugin` and implementing the required methods. Here is an example:

```python
import requests
from doi_downloader.plugins import Plugin
from doi_downloader import article_dataobject as ado # import ArticleDataObject


# Read API keys and other sensitive data from environment variables
MY_API_URL = "https://example.com/{doi}"

class MyPlugin(Plugin):
    def __new__(self):
        instance = super(Plugin, self).__new__(self)
        return instance

    def test(self):
        return True

    def fetch_metadata(self, doi):
        url = MY_API_URL.format(doi=doi)
        try:
          if response.status_code == 200:
              paper = response.json()
              title = paper.get("title", "N/A")
              download_link = paper.get("downloadUrl", "N/A")
              data_object = ado.ArticleDataObject(None)
              data_object.set_title(title)
              data_object.set_doi(doi)
              if download_link:
                  data_object.add_pdf_link(download_link)
              return data_object

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None


    def get_pdf_url(self, doi, use_cache=True, ttl=0):
      metadata = self.fetch_metadata(doi)
      return metadata.get_pdf_url() if metadata else None
```

The plugin needs to implement two functions: `fetch_metadata` and `get_pdf_url`. The `fetch_metadata` function should return an `ArticleDataObject` containing the metadata of the article, while the `get_pdf_url` function should return the URL of the PDF file.
`fetch_metadata` should handle the API request and parse the response to extract the necessary information.

## Step 3: Loading and testing the plugin

The `doi_downloader` loader module will automtically load all plugin files in the `plugins` or `extra_plugins` directory. You can test your plugin by loading your plugin withthis script:

```python
from doi_downloader import loader as ld
plugins = ld.plugins
my_plugin = plugins["MyPlugin"]
doi = "10.1000/xyz123"  # Replace with a valid DOI
metadata = my_plugin.fetch_metadata(doi)
pdf_url = my_plugin.get_pdf_url(doi)
```
