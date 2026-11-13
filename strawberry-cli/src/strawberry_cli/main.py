"""Strawberry CLI application entry point and command routing."""

import sys
from typing import Optional
import typer
from strawberry_cli.core.config import config
from strawberry_cli.core.keyboard_controller import keyboard_controller
from strawberry_cli.lite.workflow import start_lite
from strawberry_cli.services.daemon import run_daemon, register_windows_startup
from strawberry_cli.repository.supabase_sync import supabase_sync

app = typer.Typer(
    name="strawberry",
    help="Strawberry 🍓 — Standalone Windows CLI Laboratory Program Retrieval System.",
    invoke_without_command=True,
)


def version_callback(value: bool):
    if value:
        sys.stdout.write(f"Strawberry 🍓 v{config.version}\n{config.tagline}\n")
        sys.exit(0)


@app.callback()
def default_action(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True, help="Show version."
    ),
):
    """Launches Strawberry Lite by default if no subcommand is specified."""
    if ctx.invoked_subcommand is None:
        # Start the focus-aware silent ALT emergency kill-switch
        keyboard_controller.start()
        try:
            start_lite()
        finally:
            keyboard_controller.stop()


@app.command(name="lite", help="Launch the guided Strawberry Lite terminal interface.")
def lite_command():
    keyboard_controller.start()
    try:
        start_lite()
    finally:
        keyboard_controller.stop()


@app.command(name="pro", help="Launch the advanced Strawberry Pro interactive TUI.")
def pro_command():
    sys.stdout.write("\n\033[91m🍓 STRAWBERRY PRO\033[0m\n")
    sys.stdout.write("Strawberry Pro Textual TUI is scheduled for Milestone 2.\n")
    sys.stdout.write("Redirecting to Strawberry Lite...\n\n")
    lite_command()


@app.command(name="daemon", help="Run the background synchronization daemon.")
def daemon_command(
    interval: Optional[int] = typer.Option(
        None, "--interval", "-i", help="Polling interval in seconds (default 240)."
    )
):
    run_daemon(poll_interval=interval)


@app.command(name="sync", help="Force a one-shot catalog and program sync with Supabase.")
def sync_command():
    sys.stdout.write("Checking connection and syncing with remote Supabase...\n")
    res = supabase_sync.sync()
    if res.get("synced"):
        sys.stdout.write(f"\033[92m[✓] Sync successful! Downloaded {res.get('files_downloaded', 0)} files.\033[0m\n")
    else:
        sys.stdout.write(f"\033[93m[!] Sync skipped or offline: {res.get('status')}\033[0m\n")


@app.command(name="install-startup", help="Register Strawberry background daemon in Windows Startup.")
def startup_command():
    if register_windows_startup():
        sys.stdout.write("\033[92m[✓] Strawberry Sync Daemon registered in Windows Startup.\033[0m\n")
    else:
        sys.stdout.write("\033[91m[!] Failed to register in Windows Startup.\033[0m\n")


def main():
    """Main CLI execution wrapper."""
    app()


if __name__ == "__main__":
    main()
