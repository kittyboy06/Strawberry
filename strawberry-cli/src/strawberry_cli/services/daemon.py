"""Background synchronization daemon and Windows Startup registration."""

import os
import sys
import time
from typing import Optional
from pathlib import Path
from strawberry_cli.core.config import config
from strawberry_cli.repository.supabase_sync import supabase_sync


def run_daemon(poll_interval: Optional[int] = None) -> None:
    """Runs the continuous synchronization loop in background."""
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
        sys.exit(0)


def register_windows_startup() -> bool:
    """Registers Strawberry Sync Daemon in the Windows Startup directory."""
    if sys.platform != "win32":
        return False

    try:
        startup_dir = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        if not startup_dir.exists():
            return False

        # VBScript launcher runs pythonw without opening a command window
        vbs_path = startup_dir / "StrawberryDaemon.vbs"
        executable = sys.executable.replace("python.exe", "pythonw.exe")
        vbs_content = (
            f'Set WshShell = CreateObject("WScript.Shell")\n'
            f'WshShell.Run """{executable}"" -m strawberry_cli.main daemon", 0, False\n'
        )
        vbs_path.write_text(vbs_content, encoding="utf-8")
        return True
    except Exception:
        return False
