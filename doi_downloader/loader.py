import os
import importlib.util
import inspect
from plugins import Plugin

PLUGIN_FOLDER = os.path.join(os.path.dirname(__file__), "plugins")

def load_plugins():
    plugins = {}

    for filename in os.listdir(PLUGIN_FOLDER):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"plugins.{filename[:-3]}"
            module_spec = importlib.util.spec_from_file_location(module_name, os.path.join(PLUGIN_FOLDER, filename))
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Plugin) and obj is not Plugin:
                    plugins[obj.__name__] = obj()

    return plugins

