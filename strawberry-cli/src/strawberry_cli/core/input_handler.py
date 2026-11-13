"""Non-blocking Windows Console Input Handler with 7-second countdown progress bar."""

import os
import sys
import time
from typing import Callable, Optional
from .timer import CountdownTimer

try:
    import msvcrt
except ImportError:
    msvcrt = None


class TimedInputHandler:
    """Handles terminal input with an animated 7-second countdown progress bar."""

    def __init__(self, timeout_seconds: float = 7.0):
        self.timeout_seconds = timeout_seconds

    def _enable_windows_vt_mode(self) -> None:
        """Enable Virtual Terminal processing for ANSI escape sequences in Windows CMD."""
        if sys.platform != "win32":
            return
        try:
            import ctypes
            from ctypes import wintypes

            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = wintypes.DWORD()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass

    def get_input(
        self,
        prompt: str,
        validator: Optional[Callable[[str], bool]] = None,
        error_message: str = "Invalid selection! Please enter a valid option.",
        timeout_seconds: Optional[float] = None,
    ) -> str:
        """Prompts the user with a visual 7-second countdown bar rendered above the prompt.

        Restarts the countdown upon invalid input.
        Terminates the application upon timeout expiration.
        """
        self._enable_windows_vt_mode()
        timeout = timeout_seconds or self.timeout_seconds
        timer = CountdownTimer(duration_seconds=timeout)

        # Fallback for non-interactive / non-Windows environments (such as pipes or automated tests)
        if msvcrt is None or not sys.stdin.isatty():
            return self._fallback_input(prompt, validator, error_message, timeout)

        while True:
            timer.reset()
            buffer: list[str] = []
            last_second: Optional[int] = None

            # 1. Print initial progress bar on line 1
            sys.stdout.write(f"\n{timer.render_bar()}\n")
            # 2. Print input prompt on line 2
            sys.stdout.write(prompt)
            sys.stdout.flush()

            while not timer.is_expired:
                current_sec = timer.remaining_seconds_int
                # Update progress bar when the second changes
                if current_sec != last_second:
                    last_second = current_sec
                    current_typed = "".join(buffer)
                    # Move up 1 line, clear line, write bar, return to prompt line and restore typed text
                    sys.stdout.write(
                        f"\r\033[A\033[K{timer.render_bar()}\n\r\033[K{prompt}{current_typed}"
                    )
                    sys.stdout.flush()

                # Check for keyboard input
                if msvcrt.kbhit():
                    char = msvcrt.getwch()

                    # Handle Enter (Submit input)
                    if char in ("\r", "\n"):
                        sys.stdout.write("\n")
                        sys.stdout.flush()
                        value = "".join(buffer).strip()

                        # Validate input if validator provided
                        if validator is None or validator(value):
                            return value

                        # Invalid input: show error and restart loop
                        sys.stdout.write(f"\033[91m{error_message}\033[0m\n")
                        sys.stdout.flush()
                        break  # Breaks inner loop to restart 7-second timer

                    # Handle Backspace
                    elif char in ("\x08", "\x7f"):
                        if buffer:
                            buffer.pop()
                            current_typed = "".join(buffer)
                            sys.stdout.write(f"\r\033[K{prompt}{current_typed}")
                            sys.stdout.flush()

                    # Handle Ctrl+C (Interrupt)
                    elif char == "\x03":
                        sys.stdout.write("\n")
                        raise KeyboardInterrupt

                    # Handle Printable Characters
                    elif char.isprintable():
                        buffer.append(char)
                        sys.stdout.write(char)
                        sys.stdout.flush()

                time.sleep(0.04)

            # Check if inner loop finished because of timeout
            if timer.is_expired:
                sys.stdout.write("\n\n\033[91mSession expired.\033[0m\nClosing Strawberry...\n")
                sys.stdout.flush()
                sys.exit(0)

    def _fallback_input(
        self,
        prompt: str,
        validator: Optional[Callable[[str], bool]],
        error_message: str,
        timeout: float,
    ) -> str:
        """Standard input fallback for non-tty or non-Windows test environments."""
        while True:
            sys.stdout.write(f"[{'█' * 7}] {int(timeout)}s\n")
            sys.stdout.write(prompt)
            sys.stdout.flush()
            val = sys.stdin.readline().strip()
            if validator is None or validator(val):
                return val
            sys.stdout.write(f"{error_message}\n")
            sys.stdout.flush()
