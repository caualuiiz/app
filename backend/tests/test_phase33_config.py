from ai.config import ConfigurationError, get_ai_config


def test_ai_config_requires_anthropic_key_and_model(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "claude")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)

    try:
        get_ai_config()
    except ConfigurationError as exc:
        assert "ANTHROPIC_API_KEY" in str(exc)
    else:
        raise AssertionError("Expected missing API key configuration error")


def test_ai_config_accepts_explicit_runtime_values(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "claude")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-secret")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-sonnet-5")

    config = get_ai_config()

    assert config.provider == "claude"
    assert config.anthropic_model == "claude-sonnet-5"
    assert config.anthropic_api_key == "test-key-not-secret"