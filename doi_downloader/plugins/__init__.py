from dotenv import load_dotenv
load_dotenv()
class Plugin:
    """Base class for plugins. All plugins must inherit from this class."""
    def test(self):
        raise NotImplementedError("Plugin subclasses must implement the `test` method")
    def fetch_metadata(self, doi):
        raise NotImplementedError("Plugin subclasses must implement the `fetch_metadata` method")
    def get_pdf_urls(self, doi, read_from_cache=True, save_to_cache=False, ttl=0):
        raise NotImplementedError("Plugin subclasses must implement the `get_pdf_url` method")

