# Configuration

Certain plugins might require configuration to work properly. These parameters can be saved in a `.env` file in the root of your project. `test.env` shows a test env file.
This can be compied to a `.env` file. Example of a parameter that needs to be set is an email address for the Unpaywall plugin. Develpong new plugins with API key access would also require
an API key to be set in the `.env` file. The environment variables are loaded automatically from the `Plugin` class interface. Current plugins needing configuration are:

- **Unpaywall**: requires `UNPAYWALL_EMAIL` variable to be set to an email address.
- **Google Scholar**: requires `SERPAPI_KEY` to be set to a Google Scholar API key.

## Accessing the env variables from the plugin

To use an env variable simply use os.getenv() in the plugin code. For example, if you have an env variable called `UNPAYWALL_EMAIL`, you can access it like this:

```python
import os
unpaywall_email = os.getenv('UNPAYWALL_EMAIL')
```
