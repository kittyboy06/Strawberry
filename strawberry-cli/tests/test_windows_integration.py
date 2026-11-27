"""Windows-specific integration tests for Clipboard Win32 API, ALT kill switch, and standalone exe."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
import pytest

from strawberry_cli.core.config import config
from strawberry_cli.core.keyboard_controller import KeyboardController
from strawberry_cli.services.clipboard import ClipboardService


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only Win32 integration test")
def test_win32_clipboard_crlf_roundtrip():
    """Verifies real Win32 OpenClipboard/SetClipboardData preserves CRLF UTF-8 text."""
    import ctypes

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    CF_UNICODETEXT = 13

    user32.OpenClipboard.argtypes = [ctypes.c_void_p]
    user32.OpenClipboard.restype = ctypes.c_bool
    user32.GetClipboardData.argtypes = [ctypes.c_uint]
    user32.GetClipboardData.restype = ctypes.c_void_p
    user32.CloseClipboard.restype = ctypes.c_bool
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]

    payload = "line_1\nline_2\n"
    svc = ClipboardService()
    copied = svc.copy_to_clipboard(payload)
    if not copied:
        pytest.skip("Windows clipboard locked by another process")

    assert user32.OpenClipboard(None)
    try:
        handle = user32.GetClipboardData(CF_UNICODETEXT)
        assert handle
        ptr = kernel32.GlobalLock(handle)
        assert ptr
        try:
            text = ctypes.wstring_at(ptr)
            assert text == "line_1\r\nline_2\r\n"
        finally:
            kernel32.GlobalUnlock(handle)
    finally:
        user32.CloseClipboard()


def test_keyboard_controller_standalone_alt_vs_combo():
    """Verifies standalone ALT triggers only when focused without chord combos like ALT+TAB."""
    ctrl = KeyboardController()
    WM_KEYDOWN = 0x0100
    WM_KEYUP = 0x0101
    WM_SYSKEYDOWN = 0x0104
    WM_SYSKEYUP = 0x0105
    VK_LMENU = 0xA4
    VK_TAB = 0x09

    # 1. Standalone ALT when focused -> must return True on release
    assert ctrl.handle_key_event(WM_SYSKEYDOWN, VK_LMENU, is_focused=True) is False
    assert ctrl.handle_key_event(WM_KEYUP, VK_LMENU, is_focused=True) is True

    # 2. ALT + TAB chord -> must NOT trigger exit
    assert ctrl.handle_key_event(WM_SYSKEYDOWN, VK_LMENU, is_focused=True) is False
    assert ctrl.handle_key_event(WM_KEYDOWN, VK_TAB, is_focused=True) is False
    assert ctrl.handle_key_event(WM_SYSKEYUP, VK_LMENU, is_focused=True) is False

    # 3. ALT pressed/released when console is unfocused -> must NOT trigger exit
    assert ctrl.handle_key_event(WM_SYSKEYDOWN, VK_LMENU, is_focused=False) is False
    assert ctrl.handle_key_event(WM_SYSKEYUP, VK_LMENU, is_focused=False) is False


@pytest.mark.skipif(sys.platform != "win32", reason="Windows standalone exe check")
def test_standalone_exe_runs_without_python_in_path():
    """Runs strawberry.exe from TEMP with Python stripped from PATH."""
    exe_path = Path(__file__).resolve().parents[1] / "dist" / "strawberry.exe"
    if not exe_path.is_file():
        pytest.skip("strawberry.exe has not been built yet")

    env = os.environ.copy()
    filtered_paths = [
        p for p in env.get("PATH", "").split(os.pathsep) if "python" not in p.lower()
    ]
    env["PATH"] = os.pathsep.join(filtered_paths)

    res = subprocess.run(
        [str(exe_path), "--version"],
        cwd=tempfile.gettempdir(),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
    )
    assert res.returncode == 0
    assert "Strawberry" in res.stdout
    assert f"v{config.version}" in res.stdout
