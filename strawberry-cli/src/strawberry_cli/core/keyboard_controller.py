"""Focus-aware Windows Standalone ALT Emergency Kill-Switch."""

import atexit
import os
import sys
import threading
from typing import Optional

try:
    import ctypes
    from ctypes import wintypes
except ImportError:
    ctypes = None
    wintypes = None


class KeyboardController:
    """Monitors keyboard input for a standalone ALT key press and release.

    Terminates the process instantly and silently if triggered while the console has focus.
    """

    def __init__(self):
        self._hook = None
        self._thread: Optional[threading.Thread] = None
        self._thread_id: Optional[int] = None
        self._alt_pressed: bool = False
        self._combo_detected: bool = False
        self._hook_proc_ref = None  # Prevent garbage collection of callback

    def start(self) -> None:
        """Starts the low-level keyboard listener thread on Windows."""
        if sys.platform != "win32" or ctypes is None:
            return

        self._thread = threading.Thread(target=self._run_hook_loop, daemon=True, name="StrawberryAltHook")
        self._thread.start()
        atexit.register(self.stop)

    def stop(self) -> None:
        """Cleans up the Windows hook handle."""
        if sys.platform != "win32" or ctypes is None:
            return

        if self._hook and ctypes:
            try:
                ctypes.windll.user32.UnhookWindowsHookEx(self._hook)
                self._hook = None
            except Exception:
                pass

        if self._thread_id and ctypes:
            try:
                # WM_QUIT = 0x0012
                ctypes.windll.user32.PostThreadMessageW(self._thread_id, 0x0012, 0, 0)
            except Exception:
                pass

    def _run_hook_loop(self) -> None:
        """Message pump loop for the low-level keyboard hook."""
        try:
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            self._thread_id = kernel32.GetCurrentThreadId()

            WH_KEYBOARD_LL = 13
            WM_KEYDOWN = 0x0100
            WM_KEYUP = 0x0101
            WM_SYSKEYDOWN = 0x0104
            WM_SYSKEYUP = 0x0105

            VK_MENU = 0x12
            VK_LMENU = 0xA4
            VK_RMENU = 0xA5

            class KBDLLHOOKSTRUCT(ctypes.Structure):
                _fields_ = [
                    ("vkCode", wintypes.DWORD),
                    ("scanCode", wintypes.DWORD),
                    ("flags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", ctypes.c_ulong),
                ]

            HOOKPROC = ctypes.WINFUNCTYPE(
                ctypes.c_long, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
            )

            def low_level_keyboard_proc(nCode, wParam, lParam):
                if nCode >= 0:
                    kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                    vk = kb.vkCode

                    # Verify if Strawberry's console window has foreground focus
                    console_hwnd = kernel32.GetConsoleWindow()
                    foreground_hwnd = user32.GetForegroundWindow()
                    is_focused = (console_hwnd != 0 and console_hwnd == foreground_hwnd)

                    if wParam in (WM_KEYDOWN, WM_SYSKEYDOWN):
                        if vk in (VK_MENU, VK_LMENU, VK_RMENU):
                            if is_focused:
                                self._alt_pressed = True
                                self._combo_detected = False
                        else:
                            # Another key was pressed while ALT is down (e.g. ALT+TAB, ALT+F4)
                            if self._alt_pressed:
                                self._combo_detected = True

                    elif wParam in (WM_KEYUP, WM_SYSKEYUP):
                        if vk in (VK_MENU, VK_LMENU, VK_RMENU):
                            if self._alt_pressed and not self._combo_detected and is_focused:
                                # Clean standalone ALT release in focused console -> Silent emergency exit
                                self.stop()
                                os._exit(0)

                            self._alt_pressed = False
                            self._combo_detected = False

                return user32.CallNextHookEx(self._hook, nCode, wParam, lParam)

            self._hook_proc_ref = HOOKPROC(low_level_keyboard_proc)
            self._hook = user32.SetWindowsHookExW(
                WH_KEYBOARD_LL,
                self._hook_proc_ref,
                kernel32.GetModuleHandleW(None),
                0,
            )

            if not self._hook:
                return

            # Windows message pump to keep hook alive
            msg = wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) > 0:
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))

        except Exception:
            pass
        finally:
            self.stop()


# Global singleton
keyboard_controller = KeyboardController()
