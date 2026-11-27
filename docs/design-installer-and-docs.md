# Design Specification: Windows Installer Packaging & Phase 6 Documentation

> **Status:** Validated via Brainstorming  
> **Scope:** Inno Setup Packaging (`build-release.bat` + `strawberry.iss`), Automated Windows Integration & Installer Verification, and Phase 6 Documentation (`README.md`, `docs/installation.md`, `docs/admin-guide.md`)

---

## 1. Understanding Summary

* **What Is Being Built:**
  1. One-click `build-release.bat` release pipeline executing unit tests, building `strawberry.exe`, staging a gitignored 2-key client `.env.student`, and compiling `dist/Strawberry_Setup.exe` via Inno Setup (`ISCC.exe`).
  2. Hardened `installer/strawberry.iss` bundling `strawberry.exe`, `%LOCALAPPDATA%\Strawberry\.env`, and docs with safe `HKCU\Path` & `pro_state.json` uninstall cleanup.
  3. Automated Windows integration suite (`tests/test_windows_integration.py`) + live `/VERYSILENT` install/PATH/startup/uninstall verification.
  4. Updated `README.md` + new `docs/installation.md` and `docs/admin-guide.md`.
* **Why It Exists:** Ensures students can install `Strawberry` without Python or manual `.env` setup, verifies Windows-native Win32/installer integration reliably, and brings documentation in sync with Auth, VS Code web authoring, Vercel hosting, and non-mock sync.
* **Who It Is For:** Engineering students (workstation installer & guides) and faculty/lab admins (release builder & admin guide).
* **Constraints & Non-Goals:** `STRAWBERRY_SUPABASE_SECRET_KEY` and personal credentials must never enter release binaries, installers, or Git; code-signing certificate purchase is out of scope.

---

## 2. Assumptions & Non-Functional Requirements

* **Privileges:** Per-user install into `%LOCALAPPDATA%\Strawberry` (`PrivilegesRequired=lowest`) requiring zero UAC elevation.
* **Size & Compression:** `Strawberry_Setup.exe` packaged via `lzma2/ultra64` (~20 MB), shutting down active `strawberry.exe` daemon processes cleanly prior to upgrade/uninstall.
* **Safety:** Only `STRAWBERRY_SUPABASE_URL` and `STRAWBERRY_SUPABASE_PUBLISHABLE_KEY` are staged into `installer/.env.student` (gitignored and cleaned after build).

---

## 3. Decision Log

| # | Decision | Alternatives Considered | Rationale |
| :-: | :--- | :--- | :--- |
| **D1** | Install Inno Setup via `winget` (`JRSoftware.InnoSetup`) and compile `Strawberry_Setup.exe` | Script-only release without compiling; leaving `strawberry.iss` untested | Produces and verifies the real distributable `.exe` installer end-to-end. |
| **D2** | Root `build-release.bat` + gitignored `installer/.env.student` containing 2 public keys only | Bundling root `.env`; custom Inno wizard page prompting per PC; Python `scripts/build.py` | Prevents `SECRET_KEY` exposure cleanly, matches `deploy-admin-vercel.bat`, and avoids manual per-PC paste steps. |
| **D3** | Automated Windows integration harness (`test_windows_integration.py`) + live `/VERYSILENT` install/uninstall check | Headless live `msvcrt` prompts only; manual-only console walkthrough | Verifies Win32 Clipboard, `KeyboardController` hook logic, Python-free `.exe` launch, PATH, startup VBS, and uninstall without hanging automated runners. |
| **D4** | Full Phase 6 documentation suite (`README.md`, `docs/installation.md`, `docs/admin-guide.md`) | Updating `README.md` alone | Matches planned structure in `Idea/Main_Idea.md` with clear separation for students vs. faculty admins. |

---

## 4. Final Design

### Track 1: Release Pipeline & Inno Setup Hardening
1. **[.gitignore](../.gitignore):** Ignore `installer/.env.student`.
2. **[installer/strawberry.iss](../installer/strawberry.iss):**
   * Package `..\strawberry-cli\dist\strawberry.exe` → `{app}\bin\strawberry.exe`.
   * Package `..\installer\.env.student` → `{app}\.env` (`Flags: ignoreversion`).
   * Package `..\README.md`, `..\docs\architecture.md`, `..\docs\installation.md`, `..\docs\admin-guide.md` → `{app}` / `{app}\docs`.
   * Run `taskkill.exe /f /im strawberry.exe` before install & uninstall so binary/VBS upgrades never fail on locked daemon executables.
   * Clean up `pro_state.json`, `sync_state.json`, `catalog.db`, `.env`, `StrawberryDaemon.vbs`, `cache\`, and trim trailing/duplicate semicolons from `HKCU\Environment\Path` cleanly in `CurUninstallStepChanged`.
3. **`build-release.bat`:** Validates Python/`uv`/PyInstaller/`iscc`, runs `uv run pytest`, builds `strawberry.exe`, generates `installer/.env.student` safely from `.env` (strictly URL + Publishable Key), compiles `dist\Strawberry_Setup.exe`, and removes temporary `installer/.env.student`.

### Track 2: Windows Integration Verification & Docs
1. **`strawberry-cli/tests/test_windows_integration.py`:**
   * Tests real Win32 Clipboard CRLF preservation via `ctypes` `GetClipboardData(CF_UNICODETEXT)` (with original clipboard text restored).
   * Tests `KeyboardController` hook decision logic (`standalone ALT` calls `_exit` only when console has focus and no other key/combo like `ALT+TAB` occurred).
   * Runs `strawberry-cli/dist/strawberry.exe --version` from `%TEMP%` with Python paths removed from `PATH`.
2. **Installer Verification:** Runs `/VERYSILENT /SUPPRESSMSGBOXES`, checks binary, `.env`, `HKCU\Environment\Path`, startup `.vbs`, runs installed `strawberry --version` + `strawberry sync`, and verifies uninstaller cleanup.
3. **Phase 6 Docs:** Updates `README.md` and creates `docs/installation.md` and `docs/admin-guide.md`.
