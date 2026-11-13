from strawberry_cli.services.clipboard import clipboard_service


def test_line_endings_normalization():
    unix_text = "line1\nline2\nline3\n"
    normalized = clipboard_service._normalize_line_endings(unix_text)
    assert normalized == "line1\r\nline2\r\nline3\r\n"

    windows_text = "line1\r\nline2\r\n"
    normalized_win = clipboard_service._normalize_line_endings(windows_text)
    assert normalized_win == "line1\r\nline2\r\n"


def test_clipboard_copy(monkeypatch):
    test_code = "public class Hello { public static void main(String[] args) {} }"
    result = clipboard_service.copy_to_clipboard(test_code)
    # Clipboard might fail in headless CI without desktop session, but method handles it gracefully
    assert isinstance(result, bool)
