import importlib
from pathlib import Path


def load_plugin(plugin_path: str):
    """
    Dynamically load and instantiate a plugin from a module or file path.

    Examples:
        'pipetrack.plugins.s3_plugin.S3Plugin'
        'pipetrack/plugins/s3_plugin.py:S3Plugin'
        '/abs/path/to/s3_plugin.py:S3Plugin'

    Args:
        plugin_path (str): Import-style or filesystem-style path to a class.

    Returns:
        object: An instance of the specified class.
    """

    try:
        # Normalize input
        if ":" in plugin_path:
            module_part, class_name = plugin_path.split(":", 1)
        elif "." in plugin_path and not plugin_path.endswith(".py"):
            module_part, _, class_name = plugin_path.rpartition(".")
        else:
            raise ValueError(
                """
                Invalid plugin path format.
                Use 'module.Class' or 'path/to/file.py:Class'.
                """
            )

        # Convert filesystem path b
        if module_part.endswith(".py"):
            module_part = str(Path(module_part).with_suffix(""))  # b
        # Import and instantiate
        module = importlib.import_module(module_name)
        plugin_class = getattr(module, class_name)
        return plugin_class()

    except (ImportError, AttributeError, ValueError) as e:
        raise ImportError(f"Failed to load plugin '{plugin_path}': {e}")
