import importlib
import pkgutil
from typing import Type, List
from pipetrack.plugins.base import LogSourcePlugin


def load_plugin(plugin_path: str) -> LogSourcePlugin:
    """
    Dynamically load and instantiate a plugin given as module.Class.

    Args:
        plugin_path (str): path in the format "module.submodule.ClassName".

    Returns:
        LogSourcePlugin: Instantiated plugin object.
    """
    mod_name, class_name = plugin_path.rsplit(".", 1)
    mod = importlib.import_module(mod_name)
    cls = getattr(mod, class_name)
    if not issubclass(cls, LogSourcePlugin):
        raise TypeError(f"{class_name} must inherit from LogSourcePlugin")
    return cls()


def discover_plugins(package: str) -> List[Type[LogSourcePlugin]]:
    """
    Discover all LogSourcePlugin subclasses in a package.

    Args:
        package (str): Package name to scan (e.g., "pipetrack.plugins").

    Returns:
        List[Type[LogSourcePlugin]]: List of plugin classes found.
    """
    plugins: List[Type[LogSourcePlugin]] = []
    pkg = importlib.import_module(package)
    for _, name, is_pkg in pkgutil.iter_modules(
        pkg.__path__, pkg.__name__ + "."
    ):
        if is_pkg:
            continue
        mod = importlib.import_module(name)
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, LogSourcePlugin)
                and attr is not LogSourcePlugin
            ):
                plugins.append(attr)
    return plugins


def instantiate_all_plugins(package: str) -> List[LogSourcePlugin]:
    """
    Discover and instantiate all plugins in a package.

    Args:
        package (str): Package name to scan.

    Returns:
        List[LogSourcePlugin]: List of instantiated plugin objects.
    """
    return [cls() for cls in discover_plugins(package)]
