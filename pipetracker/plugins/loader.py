from pathlib import Path
from typing import Union, List, Any
from pipetracker.plugins.base import LogSourcePlugin
from pipetracker.core import plugin_loader as core_loader
import logging

logger = logging.getLogger(__name__)


def load_plugin(
    plugin_path: Union[str, Path], **kwargs: Any
) -> LogSourcePlugin:
    """
    Wrapper around core plugin loader that ensures type safety.

    Args:
        plugin_path: Path to the plugin class, as a string\
             ('module:ClassName') or Path object.
        **kwargs: Optional arguments to pass to the plugin constructor.

    Returns:
        LogSourcePlugin: Instantiated plugin object.

    Raises:
        TypeError: If the instantiated plugin does not extend LogSourcePlugin.
        ValueError: If the plugin path is invalid or cannot be loaded.
    """
    try:
        plugin_instance = core_loader.load_plugin(plugin_path, **kwargs)
        if not isinstance(plugin_instance, LogSourcePlugin):
            raise TypeError(
                f"{plugin_instance.__class__.__name__} must\
                     extend LogSourcePlugin"
            )
        return plugin_instance
    except (ValueError, TypeError) as e:
        logger.error(f"Failed to load plugin from {plugin_path}: {e}")
        raise


def discover_plugins() -> List[str]:
    """
    Discover available plugins.

    Returns:
        List[str]: List of plugin paths in 'module:ClassName'\
             format or Path objects.
    """
    return core_loader.discover_plugins()


def instantiate_all_plugins(**kwargs: Any) -> List[LogSourcePlugin]:
    """
    Instantiate all discovered plugins.

    Args:
        **kwargs: Optional arguments to pass to each plugin constructor.

    Returns:
        List[LogSourcePlugin]: List of instantiated plugin objects.
    """
    return core_loader.instantiate_all_plugins(**kwargs)
