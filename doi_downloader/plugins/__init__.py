class Plugin:
    """Base class for plugins. All plugins must inherit from this class."""
    def test(self):
        raise NotImplementedError("Plugin subclasses must implement the `test` method")
    def fetch_metadata(self, doi):
        raise NotImplementedError("Plugin subclasses must implement the `fetch_metadata` method")
    def get_pdf_url(self, doi, use_cache=True, ttl=0):
        raise NotImplementedError("Plugin subclasses must implement the `get_pdf_url` method")

