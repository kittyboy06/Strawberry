"""Background synchronization daemon, mutex locking, and Windows Startup auto-registration."""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional
from strawberry_cli.core.config import config
from strawberry_cli.repository.supabase_sync import supabase_sync

try:
    import ctypes
    from ctypes import wintypes
except ImportError:
    ctypes = None
    wintypes = None

DAEMON_MUTEX_NAME = "Local\\StrawberrySyncDaemonMutex"
_mutex_handle = None


def acquire_daemon_mutex() -> bool:
    """Attempts to acquire a named Windows mutex to guarantee single daemon instance."""
    global _mutex_handle
    if sys.platform != "win32" or ctypes is None:
        return True

    try:
        kernel32 = ctypes.windll.kernel32
        ERROR_ALREADY_EXISTS = 183

        _mutex_handle = kernel32.CreateMutexW(None, True, DAEMON_MUTEX_NAME)
        last_error = kernel32.GetLastError()

        if last_error == ERROR_ALREADY_EXISTS:
            return False
        return bool(_mutex_handle)
    except Exception:
        return True


def release_daemon_mutex() -> None:
    """Releases the Windows mutex handle upon daemon shutdown."""
    global _mutex_handle
    if _mutex_handle and ctypes:
        try:
            ctypes.windll.kernel32.CloseHandle(_mutex_handle)
            _mutex_handle = None
        except Exception:
            pass


def is_daemon_running() -> bool:
    """Checks whether an active daemon process holds the Windows mutex."""
    if sys.platform != "win32" or ctypes is None:
        return False

    try:
        kernel32 = ctypes.windll.kernel32
        SYNCHRONIZE = 0x00100000
        handle = kernel32.OpenMutexW(SYNCHRONIZE, False, DAEMON_MUTEX_NAME)
        if handle:
            kernel32.CloseHandle(handle)
            return True
        return False
    except Exception:
        return False


def run_daemon(poll_interval: Optional[int] = None) -> None:
    """Runs the continuous synchronization loop in background."""
    if not acquire_daemon_mutex():
        sys.stdout.write("Strawberry Sync Daemon is already running.\n")
        sys.exit(0)

    interval = poll_interval or config.daemon_poll_interval_seconds
    sys.stdout.write(f"🍓 Strawberry Sync Daemon started. Polling every {interval}s.\n")
    sys.stdout.flush()

    try:
        while True:
            result = supabase_sync.sync()
            if result.get("synced"):
                sys.stdout.write(
                    f"[{time.strftime('%X')}] Synced catalog. Downloaded {result.get('files_downloaded', 0)} files.\n"
                )
                sys.stdout.flush()
            time.sleep(interval)
    except KeyboardInterrupt:
        sys.stdout.write("\nStrawberry Daemon stopped gracefully.\n")
    finally:
        release_daemon_mutex()
        sys.exit(0)


def register_windows_startup() -> bool:
    """Registers Strawberry Sync Daemon in the Windows Startup directory."""
    if sys.platform != "win32":
        return False

    try:
        startup_dir = (
            Path(os.environ.get("APPDATA", ""))
            / "Microsoft"
            / "Windows"
            / "Start Menu"
            / "Programs"
            / "Startup"
        )
        startup_dir.mkdir(parents=True, exist_ok=True)
        vbs_path = startup_dir / "StrawberryDaemon.vbs"

        # Determine target command based on frozen executable or python runtime
        if getattr(sys, "frozen", False):
            # Compiled pyinstaller executable
            exe_path = sys.executable
            vbs_content = (
                f'Set WshShell = CreateObject("WScript.Shell")\n'
                f'WshShell.Run """{exe_path}"" daemon", 0, False\n'
            )
        else:
            executable = sys.executable.replace("python.exe", "pythonw.exe")
            vbs_content = (
                f'Set WshShell = CreateObject("WScript.Shell")\n'
                f'WshShell.Run """{executable}"" -m strawberry_cli.main daemon", 0, False\n'
            )

        vbs_path.write_text(vbs_content, encoding="utf-8")
        return True
    except Exception:
        return False


def start_daemon_background() -> bool:
    """Silently spawns the daemon process detached without opening any console window."""
    if is_daemon_running():
        return True

    if sys.platform != "win32":
        return False

    try:
        # Flags to create completely invisible detached process
        DETACHED_PROCESS = 0x00000008
        CREATE_NO_WINDOW = 0x08000000
        flags = DETACHED_PROCESS | CREATE_NO_WINDOW

        if getattr(sys, "frozen", False):
            cmd = [sys.executable, "daemon"]
        else:
            pythonw = sys.executable.replace("python.exe", "pythonw.exe")
            cmd = [pythonw, "-m", "strawberry_cli.main", "daemon"]

        subprocess.Popen(
            cmd,
            creationflags=flags,
            close_fds=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
        return True
    except Exception:
        return False


def ensure_background_services() -> None:
    """Guarantees startup registration and active background daemon by default.

    Executed automatically on application launch without blocking the user interface.
    """
    if sys.platform != "win32":
        return

    # 1. Ensure startup runner exists in shell:startup
    startup_dir = (
        Path(os.environ.get("APPDATA", ""))
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
        / "Startup"
    )
    vbs_path = startup_dir / "StrawberryDaemon.vbs"
    if not vbs_path.exists():
        register_windows_startup()

    # 2. Ensure daemon is currently running in background
    if not is_daemon_running():
        start_daemon_background()
