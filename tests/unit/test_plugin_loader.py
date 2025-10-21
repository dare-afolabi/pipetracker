from pathlib import Path
from pipetracker.core.plugin_loader import load_plugin


def test_plugin_loader_discovers_local_plugins(tmp_path):
    """Test the plugin loader's ability to discover and instantiate local \
        plugins from various path formats."""
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir(parents=True, exist_ok=True)
    dummy_plugin_file = plugin_dir / "dummy_plugin.py"
    dummy_plugin_file.write_text(
        "from pipetracker.plugins.base import LogSourcePlugin\n"
        "class DummyPlugin(LogSourcePlugin):\n"
        "    def fetch_logs(self, source, max_files=100, max_size_mb=10.0):\n"
        "        return ['example_plugin']\n"
        "    def discover(self):\n"
        "        return ['example_plugin']\n",
        encoding="utf-8",
    )
    plugin_paths = [
        f"{dummy_plugin_file}:DummyPlugin",
        f"{dummy_plugin_file.resolve()}:DummyPlugin",
        Path(dummy_plugin_file.resolve()),
    ]
    for path in plugin_paths:
        plugin_path = path if isinstance(path, str) else f"{path}:DummyPlugin"
        plugin_instance = load_plugin(plugin_path)
        assert plugin_instance.__class__.__name__ == "DummyPlugin"
        assert hasattr(plugin_instance, "discover")
        assert callable(plugin_instance.discover)
        plugins = list(plugin_instance.discover())
        assert isinstance(plugins, (list, tuple))
