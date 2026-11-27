# Strawberry Installation Guide

> **"Pick your program. Paste your code."**

This guide covers installing, running, updating, and uninstalling the **Strawberry Windows CLI** on student lab workstations and personal Windows 10/11 machines.

---

## 1. Installing via `Strawberry_Setup.exe` (Recommended for Students)

The standalone installer bundles everything needed into one executable with **zero Python installation** or administrator (`UAC`) rights required.

1. Double-click `Strawberry_Setup.exe`.
   * *Note on Windows SmartScreen:* Because releases are not yet Authenticode code-signed, Windows Defender SmartScreen may display *"Windows protected your PC"*. Click **More info → Run anyway** (or have lab coordinators pre-approve the SHA-256 hash).
2. Accept the default per-user install folder (`%LOCALAPPDATA%\Strawberry`).
3. Finish the wizard. The installer automatically:
   * Places `strawberry.exe` inside `%LOCALAPPDATA%\Strawberry\bin`.
   * Adds `%LOCALAPPDATA%\Strawberry\bin` to your user `PATH`.
   * Writes the read-only client `.env` (`STRAWBERRY_SUPABASE_URL` + `STRAWBERRY_SUPABASE_PUBLISHABLE_KEY`) to `%LOCALAPPDATA%\Strawberry\.env`.
   * Registers `StrawberryDaemon.vbs` in Windows Startup (`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`).
   * Performs an initial sync and launches the silent background sync daemon.

### Silent Lab Deployment (Lab Administrators)
Install silently across lab workstations without prompts:
```powershell
.\Strawberry_Setup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
```

---

## 2. Launching Strawberry

Open a **new** Command Prompt (`cmd.exe`), PowerShell, or Windows Terminal window so the updated `PATH` takes effect:

```powershell
# Launch guided Strawberry Lite interface (default)
strawberry

# Launch advanced 3-pane Strawberry Pro TUI (Search, Bookmarks, History)
strawberry pro

# Force immediate sync with Supabase catalog
strawberry sync

# Check installed version
strawberry --version
```

---

## 3. Offline & Background Sync Behavior

* **Local Cache Paths:**
  * SQLite Catalog: `%LOCALAPPDATA%\Strawberry\catalog.db`
  * Verified Source Files: `%LOCALAPPDATA%\Strawberry\cache\`
  * Pro Bookmarks & History: `%LOCALAPPDATA%\Strawberry\pro_state.json`
* **Offline Access:** Once synced, both `strawberry` (Lite) and `strawberry pro` start instantaneously (<100ms) and operate completely offline.
* **SHA-256 Enforcement:** Before copying any program to the Windows clipboard, Strawberry computes its SHA-256 digest and strictly blocks copying if a file is corrupted or modified.

---

## 4. Windows-Specific Behavior & Limitations

* **7-Second Countdown & Terminal Rendering:** Strawberry enables `ENABLE_VIRTUAL_TERMINAL_PROCESSING` (`0x0004`) via the Win32 Console API on launch. Legacy `conhost.exe`, PowerShell, and Windows Terminal render ANSI colors cleanly; redirected/non-TTY pipes fall back gracefully.
* **Focus-Aware Standalone `ALT` Kill-Switch:** Pressing and releasing `ALT` alone immediately terminates `strawberry` **only** when its console window holds foreground focus (`GetForegroundWindow()`). Chords such as `ALT+TAB` or `ALT+F4` are ignored so switching windows never closes Strawberry.
* **SmartScreen / Lab Firewalls:** If campus network rules block outgoing HTTPS to Supabase during lab exams, Strawberry uses the already cached catalog without failing.

---

## 5. Uninstalling

Uninstall cleanly via Windows **Settings → Apps → Installed apps → Strawberry**, or run `%LOCALAPPDATA%\Strawberry\unins000.exe` (`/VERYSILENT` supported). Uninstalling:
1. Terminates any running background `strawberry.exe` daemon.
2. Removes `StrawberryDaemon.vbs` from Windows Startup.
3. Removes `catalog.db`, `.env`, `sync_state.json`, `pro_state.json`, and `cache\`.
4. Cleans only `%LOCALAPPDATA%\Strawberry\bin` from your user `PATH`.
