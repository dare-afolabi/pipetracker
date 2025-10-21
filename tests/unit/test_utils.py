from pipetracker.core.utils import safe_json_load


class TestSafeJsonLoad:
    """Test suite for the safe_json_load utility function to \
        ensure robust JSON parsing."""

    def test_valid_dict_with_multiple_keys(self):
        line = '{"a": 1, "b": 2}'
        result = safe_json_load(line)
        assert result == {"a": 1, "b": 2}

    def test_valid_dict_with_single_key(self):
        line = '{"a": 1}'
        result = safe_json_load(line)
        assert "default_key" in result
        assert result["default_key"] == "default_value"
        assert len(result) == 2

    def test_non_dict_json_string(self):
        line = '"hello world"'
        result = safe_json_load(line)
        assert result == {"parsed": "hello world", "type": "non_dict"}

    def test_non_dict_json_number(self):
        line = "123"
        result = safe_json_load(line)
        assert result == {"parsed": 123, "type": "non_dict"}

    def test_non_dict_json_list(self):
        line = "[1, 2, 3]"
        result = safe_json_load(line)
        assert result == {"parsed": [1, 2, 3], "type": "non_dict"}

    def test_invalid_json(self):
        line = '{"a": 1,'  # invalid JSON
        result = safe_json_load(line)
        assert result == {
            "status": "invalid_json",
            "default_key": "default_value",
        }

    def test_empty_string(self):
        result = safe_json_load("")
        assert result == {
            "status": "invalid_json",
            "default_key": "default_value",
        }

    def test_whitespace_string(self):
        result = safe_json_load("   ")
        assert result == {
            "status": "invalid_json",
            "default_key": "default_value",
        }

    def test_nested_dict(self):
        line = '{"a": {"b": 2}, "c": 3}'
        result = safe_json_load(line)
        assert result["a"] == {"b": 2}
        assert result["c"] == 3
