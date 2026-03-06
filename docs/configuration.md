## Configuration

Some plugins require additional information to work properly. This information needs to be saved in a `.env` file 
in the root directory of `doi_downloader`. The file `test.env` contains an example of `.env`. It can be updated and 
copied to `.env`. For example, a parameter that needs to be set is the user's email address for the Unpaywall plugin. 
Developing new plugins with API key access might also require API keys to be set in the `.env` file. The environment 
variables are loaded automatically from the `Plugin` class interface in `doi_downloader/plugins/__init__.py`.

Current plugins needing configuration are:

- **Unpaywall**: requires the `UNPAYWALL_EMAIL` variable to be set to the user's email address.
- **Google Scholar**: requires `SERPAPI_KEY` to be set to a Google Scholar API key 
  ([more information](https://support.google.com/googleapi/answer/6158862?hl=en))
- **CORE**: required `CORE_API_KEY` to be set in order to be used
  ([more information](https://core.ac.uk/services/api))

### Accessing the .env variables from a plugin

To use a .env variable use `os`'s `environ` in the plugin code. For example, the environment variable 
`UNPAYWALL_EMAIL`, can be accessed like this:

```python
import os

unpaywall_email = os.environ['UNPAYWALL_EMAIL']
```

### Accessing the .env variables from a Jupyter notebook

In a Jupyter notebook, you first need to read the `.env` file with `dotenv`'s `load_dotenv()`. After this you can
extract the variable values with `os`'s `environ`. The environment variable `UNPAYWALL_EMAIL` can be accessed 
like this:

```python
from dotenv import load_dotenv
import os

load_dotenv()
unpaywall_email = os.environ['UNPAYWALL_EMAIL']
```
