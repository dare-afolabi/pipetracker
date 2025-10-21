import importlib.util
import sys
from pathlib import Path
from typing import Union, List, Any
from importlib import import_module
from pipetracker.plugins.base import LogSourcePlugin
import logging

logger = logging.getLogger(__name__)


def load_plugin(
    plugin_path: Union[str, Path], **kwargs: Any
) -> LogSourcePlugin:
    """
    Load a plugin from a given path (module:class or file path).

    Args:
        plugin_path: Path to the plugin in format 'module:ClassName' (for \
            Python modules),
                     'path:ClassName' (for file paths), or Path object.
        **kwargs: Optional arguments to pass to the plugin constructor.

    Returns:
        LogSourcePlugin: Instantiated plugin object.

    Raises:
        ValueError: If plugin_path is invalid or module/class cannot be found.
        TypeError: If the instantiated class does not extend LogSourcePlugin.
    """
    try:
        if isinstance(plugin_path, Path):
            # Handle Path object
            plugin_path = plugin_path.resolve()
            module_name = plugin_path.stem
            class_name = kwargs.get(
                "class_name", "Plugin"
            )  # Fallback class name
            spec = importlib.util.spec_from_file_location(
                module_name, plugin_path
            )
            if spec is None or spec.loader is None:
                raise ValueError(
                    f"Cannot create module spec for {plugin_path}"
                )
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
        else:
            # Handle string input as 'module:ClassName' or 'path:ClassName'
            module_name, class_name = str(plugin_path).rsplit(":", 1)
            # Check if module_name is a file path
            if Path(module_name).is_file():
                plugin_path = Path(module_name).resolve()
                module_name = plugin_path.stem
                spec = importlib.util.spec_from_file_location(
                    module_name, plugin_path
                )
                if spec is None or spec.loader is None:
                    raise ValueError(
                        f"Cannot create module spec for {plugin_path}"
                    )
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
            else:
                # Assume module_name is a Python module
                module = import_module(module_name)

        plugin_class = getattr(module, class_name)
        plugin_instance = plugin_class(**kwargs)
        if not isinstance(plugin_instance, LogSourcePlugin):
            raise TypeError(f"{class_name} must extend LogSourcePlugin")
        return plugin_instance
    except (ImportError, AttributeError, ValueError) as e:
        logger.error(f"Failed to load plugin from {plugin_path}: {e}")
        raise ValueError(f"Invalid plugin path: {plugin_path}")
    except TypeError as e:
        logger.error(f"Type error for plugin {plugin_path}: {e}")
        raise


def discover_plugins(plugin_dir: Union[str, Path] = "plugins") -> List[str]:
    """
    Discover available plugins in a specified directory.

    Args:
        plugin_dir: Directory containing plugin modules (default: "plugins").

    Returns:
        List[str]: List of plugin paths in 'path:ClassName' format for files.
    """
    plugin_paths = []
    plugin_dir = Path(plugin_dir).resolve()
    if not plugin_dir.exists() or not plugin_dir.is_dir():
        logger.warning(
            f"Plugin directory {plugin_dir} does not exist or is \
                not a directory"
        )
        return []

    for file_path in plugin_dir.glob("*.py"):
        module_name = file_path.stem
        try:
            spec = importlib.util.spec_from_file_location(
                module_name, file_path
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, LogSourcePlugin)
                    and attr != LogSourcePlugin
                ):
                    plugin_paths.append(f"{file_path}:{attr_name}")
        except Exception as e:
            logger.error(f"Failed to discover plugin in {file_path}: {e}")
            continue
    return plugin_paths


def instantiate_all_plugins(**kwargs: Any) -> List[LogSourcePlugin]:
    """
    Instantiate all discovered plugins.

    Args:
        **kwargs: Optional arguments to pass to each plugin constructor.

    Returns:
        List[LogSourcePlugin]: List of instantiated plugin objects.
    """
    plugins = []
    for plugin_path in discover_plugins():
        try:
            plugin = load_plugin(plugin_path, **kwargs)
            plugins.append(plugin)
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to instantiate plugin {plugin_path}: {e}")
            continue
    return plugins
