def test_load_valid_config(tmp_path):
    """Ensure valid config loads and validates successfully."""
    yaml_path = tmp_path / "config.yaml"
    yaml_path.write_text(
        """
    log_sources: ["sourceA"]
    match_keys: ["id"]
    output:
      format: "json"
      path: "/tmp/out"
    verifier_endpoints: {"local": "http://localhost:8000"}
    security:
      encrypt_logs: false
    """
    )
    from pipetrack.core.config_loader import ConfigLoader

    cfg = ConfigLoader().load(str(yaml_path))
    assert cfg.output.format == "json"
    assert "local" in cfg.verifier_endpoints


def test_load_invalid_config(tmp_path):
    """Raise ValueError on missing required fields."""
    yaml_path = tmp_path / "bad.yaml"
    yaml_path.write_text("invalid: true")
    from pipetrack.core.config_loader import ConfigLoader

    loader = ConfigLoader()
    try:
        loader.load(str(yaml_path))
        assert False, "Expected ValueError"
    except ValueError:
        pass
