import pytest
from unittest.mock import patch
from pipetracker.plugins import loader
from pipetracker.plugins.base import LogSourcePlugin


class DummyPlugin(LogSourcePlugin):
    """A plugin that extends LogSourcePlugin."""

    def fetch_logs(self):
        # Stub implementation to satisfy abstract base class.
        return []


def test_load_plugin_success():
    """Test successful loading of a plugin, ensuring it returns a valid \
        LogSourcePlugin instance."""
    dummy_instance = DummyPlugin()

    with patch(
        "pipetracker.plugins.loader.core_loader.load_plugin",
        return_value=dummy_instance,
    ) as mock_load:
        result = loader.load_plugin("dummy:DummyPlugin", arg1="value")
        mock_load.assert_called_once_with("dummy:DummyPlugin", arg1="value")
        assert isinstance(result, LogSourcePlugin)
        assert result is dummy_instance


def test_load_plugin_wrong_type():
    """Test that a TypeError is raised when the loaded object is not \
        a LogSourcePlugin."""
    fake_instance = object()

    with patch(
        "pipetracker.plugins.loader.core_loader.load_plugin",
        return_value=fake_instance,
    ):
        with pytest.raises(TypeError):
            loader.load_plugin("bad:FakePlugin")


def test_load_plugin_value_error():
    """Test that a ValueError is raised when the core loader fails \
        to load the plugin."""
    with patch(
        "pipetracker.plugins.loader.core_loader.load_plugin",
        side_effect=ValueError("Invalid plugin"),
    ):
        with pytest.raises(ValueError):
            loader.load_plugin("invalid:plugin")


def test_load_plugin_type_error_logged(caplog):
    """Test that a TypeError is logged and re-raised when loading \
        an invalid plugin type."""
    caplog.set_level("ERROR")

    with patch(
        "pipetracker.plugins.loader.core_loader.load_plugin",
        side_effect=TypeError("Invalid type"),
    ):
        with pytest.raises(TypeError):
            loader.load_plugin("invalid:type")

    assert any(
        "Failed to load plugin from invalid:type" in rec.message
        for rec in caplog.records
    )


def test_discover_plugins():
    """Test the discover_plugins function to ensure it returns \
        the list from core_loader.discover_plugins."""
    mock_plugins = ["plugin_a:ClassA", "plugin_b:ClassB"]

    with patch(
        "pipetracker.plugins.loader.core_loader.discover_plugins",
        return_value=mock_plugins,
    ):
        result = loader.discover_plugins()
        assert result == mock_plugins


def test_instantiate_all_plugins():
    """Test the instantiate_all_plugins function to ensure it \
        returns a list of instantiated plugins."""
    mock_instances = [DummyPlugin(), DummyPlugin()]

    with patch(
        "pipetracker.plugins.loader.core_loader.instantiate_all_plugins",
        return_value=mock_instances,
    ):
        result = loader.instantiate_all_plugins()
        assert all(isinstance(p, LogSourcePlugin) for p in result)
        assert len(result) == 2
