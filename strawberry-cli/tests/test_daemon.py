import sys
from strawberry_cli.services.daemon import (
    acquire_daemon_mutex,
    release_daemon_mutex,
    is_daemon_running,
    register_windows_startup,
    ensure_background_services,
)


def test_daemon_mutex_lifecycle():
    # If on windows, verify acquiring and releasing mutex works cleanly
    if sys.platform == "win32":
        acquired = acquire_daemon_mutex()
        assert acquired is True
        assert is_daemon_running() is True
        release_daemon_mutex()


def test_ensure_background_services(monkeypatch):
    # Ensure calling ensure_background_services executes cleanly without raising any exceptions
    ensure_background_services()
