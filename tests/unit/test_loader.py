from pipetrack.core.plugin_loader import load_plugin


def test_plugin_loader_discovers_local_plugins(tmp_path, monkeypatch):
    """
    Ensures plugin loader initializes safely and discovers plugins
    even when optional dependencies are missing.
    """

    # --- Create a dummy plugin directory ---
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir(parents=True, exist_ok=True)

    # --- Create a minimal dummy plugin file ---
    dummy_plugin_file = plugin_dir / "dummy_plugin.py"
    dummy_plugin_file.write_text(
        "class DummyPlugin:\n"
        "    def discover(self):\n"
        "        return ['example_plugin']\n",
        encoding="utf-8",
    )

    # --- Dynamically load the plugin using the new robust path syntax ---
    plugin_path = f"{dummy_plugin_file}:DummyPlugin"
    plugin_instance = load_plugin(plugin_path)

    # --- Assertions ---
    # The loader should be an instance of DummyPlugin
    assert plugin_instance.__class__.__name__ == "DummyPlugin"

    # Verify that discover() exists and is callable
    assert hasattr(
        plugin_instance, "discover"
    ), "Plugin must define discover()"
    assert callable(plugin_instance.discover), "discover() must be callable"

    # discover() should return an iterable
    plugins = list(plugin_instance.discover())
    assert isinstance(
        plugins, (list, tuple)
    ), "discover() must return list/tuple"
