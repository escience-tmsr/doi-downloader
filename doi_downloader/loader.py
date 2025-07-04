import os
import importlib.util
import inspect
from doi_downloader.plugins import Plugin

PLUGIN_FOLDER = os.path.join(os.path.dirname(__file__), "plugins")
EXTRA_PLUGIN_FOLDER = os.path.join(os.path.dirname(__file__), "extra_plugins")

plugins = {}

def _load_plugins(folder):
    global plugins

    if not os.path.isdir(folder):
        return plugins

    for filename in os.listdir(folder):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"plugins.{filename[:-3]}"
            module_spec = importlib.util.spec_from_file_location(module_name, os.path.join(folder, filename))
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Plugin) and obj is not Plugin:
                    plugins[obj.__name__] = obj()

    return plugins

_load_plugins(PLUGIN_FOLDER)
_load_plugins(EXTRA_PLUGIN_FOLDER)
