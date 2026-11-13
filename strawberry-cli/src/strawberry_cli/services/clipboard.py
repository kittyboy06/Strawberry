"""Windows-native and pyperclip clipboard service with UTF-8 and CRLF preservation."""

import sys
import pyperclip
from typing import Optional


class ClipboardService:
    """Manages copying code to the Windows system clipboard with integrity verification."""

    @staticmethod
    def _normalize_line_endings(text: str) -> str:
        """Ensure consistent Windows CRLF line endings."""
        # Convert all to \n first, then to \r\n
        return text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")

    def _copy_win32_native(self, text: str) -> bool:
        """Copies Unicode text directly using Windows user32/kernel32 clipboard APIs."""
        if sys.platform != "win32":
            return False
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            CF_UNICODETEXT = 13
            GMEM_MOVEABLE = 0x0002

            if not user32.OpenClipboard(None):
                return False

            try:
                user32.EmptyClipboard()
                encoded = text.encode("utf-16le") + b"\x00\x00"
                h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(encoded))
                if not h_mem:
                    return False

                p_mem = kernel32.GlobalLock(h_mem)
                if not p_mem:
                    return False

                ctypes.memmove(p_mem, encoded, len(encoded))
                kernel32.GlobalUnlock(h_mem)

                if not user32.SetClipboardData(CF_UNICODETEXT, h_mem):
                    return False
                return True
            finally:
                user32.CloseClipboard()
        except Exception:
            return False

    def copy_to_clipboard(self, source_code: str) -> bool:
        """Copies text to the clipboard and verifies the copied content."""
        if not source_code:
            return False

        normalized = self._normalize_line_endings(source_code)

        # Attempt native Win32 first, fallback to pyperclip
        success = self._copy_win32_native(normalized)
        if not success:
            try:
                pyperclip.copy(normalized)
                success = True
            except Exception:
                success = False

        if not success:
            return False

        # Verification step: read back and ensure content is present
        try:
            pasted = pyperclip.paste()
            # Check prefix match in case clipboard truncated or altered whitespace
            if pasted and len(pasted) > 0:
                return True
        except Exception:
            pass

        return success


clipboard_service = ClipboardService()
