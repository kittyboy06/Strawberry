import os
from strawberry_cli.core.config import StrawberryConfig


def test_config_publishable_and_secret_keys(monkeypatch):
    monkeypatch.setenv("STRAWBERRY_SUPABASE_URL", "https://modern.supabase.co")
    monkeypatch.setenv("STRAWBERRY_SUPABASE_PUBLISHABLE_KEY", "sb_publishable_test_123")
    monkeypatch.setenv("STRAWBERRY_SUPABASE_SECRET_KEY", "sb_secret_test_456")
    monkeypatch.setenv("STRAWBERRY_INPUT_TIMEOUT_SECONDS", "5.5")
    monkeypatch.setenv("STRAWBERRY_DAEMON_POLL_INTERVAL_SECONDS", "180")

    cfg = StrawberryConfig()
    assert cfg.supabase_url == "https://modern.supabase.co"
    assert cfg.supabase_publishable_key == "sb_publishable_test_123"
    assert cfg.supabase_anon_key == "sb_publishable_test_123"
    assert cfg.supabase_secret_key == "sb_secret_test_456"
    assert cfg.input_timeout_seconds == 5.5
    assert cfg.daemon_poll_interval_seconds == 180


def test_config_vite_publishable_prefix(monkeypatch):
    monkeypatch.delenv("STRAWBERRY_SUPABASE_URL", raising=False)
    monkeypatch.delenv("STRAWBERRY_SUPABASE_PUBLISHABLE_KEY", raising=False)
    monkeypatch.delenv("STRAWBERRY_SUPABASE_ANON_KEY", raising=False)
    monkeypatch.setenv("VITE_SUPABASE_URL", "https://vite.supabase.co")
    monkeypatch.setenv("VITE_SUPABASE_PUBLISHABLE_KEY", "sb_publishable_vite_789")

    cfg = StrawberryConfig()
    assert cfg.supabase_url == "https://vite.supabase.co"
    assert cfg.supabase_publishable_key == "sb_publishable_vite_789"
    assert cfg.supabase_anon_key == "sb_publishable_vite_789"


def test_config_legacy_anon_key_backward_compatibility(monkeypatch):
    monkeypatch.delenv("STRAWBERRY_SUPABASE_PUBLISHABLE_KEY", raising=False)
    monkeypatch.delenv("VITE_SUPABASE_PUBLISHABLE_KEY", raising=False)
    monkeypatch.setenv("STRAWBERRY_SUPABASE_ANON_KEY", "legacy_jwt_anon_key")

    cfg = StrawberryConfig()
    assert cfg.supabase_publishable_key == "legacy_jwt_anon_key"
    assert cfg.supabase_anon_key == "legacy_jwt_anon_key"
