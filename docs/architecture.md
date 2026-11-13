# Strawberry 🍓 — System Architecture & Design Specification
**Standalone Windows CLI-Based Laboratory Program Retrieval System & Admin Portal**

**Document Version:** 1.0.0  
**Status:** Approved & Validated  
**Date:** 2026-11-13  

---

## 1. Executive Summary & Purpose

Strawberry is an offline-first laboratory program retrieval system designed specifically for university department students (2nd, 3rd, and 4th years). It replaces chaotic code distribution methods (such as WhatsApp group chats, unstructured cloud drives, and fragmented repositories) with a single, reliable command-line tool.

The system consists of:
1. **Strawberry Lite CLI:** An ultra-lightweight, instant-start (<100ms) Windows command-line application that guides students to select their year, subject, and experiment, then automatically copies the verified source code to their Windows clipboard.
2. **Windows Console Platform Engine:** Implements a strict 7-second countdown per input prompt (featuring an ASCII/Unicode visual progress bar), alongside a focus-aware, low-level emergency kill-switch (`ALT`) that silently terminates the application with zero terminal output.
3. **Background Sync Daemon (`strawberry daemon`):** A headless background worker registered in Windows Startup (`shell:startup`) that polls for internet connectivity every 3–5 minutes and pre-caches the full catalog and all source code files into `%LOCALAPPDATA%\Strawberry\`.
4. **Supabase Cloud Backend:** Hosts the centralized PostgreSQL academic database, source file storage bucket (`programs`), and enforces Row-Level Security (RLS) with public read-only access for students and authenticated write access for administrators.
5. **Strawberry Admin Web App:** A modern, responsive React + Vite + Tailwind web dashboard where faculty can manage academic years, subjects, experiments, and drag-and-drop source files with automated client-side SHA-256 calculation and versioning.

---

## 2. Understanding Summary

* **What is being built:** A two-part ecosystem: (1) A native Windows CLI retrieval client with background sync, and (2) A web-based faculty management portal connected via Supabase.
* **Why it exists:** To eliminate lab exam and class friction by allowing students to acquire verified lab code in seconds directly into their clipboard.
* **Target Audience:** Engineering college students across 2nd, 3rd, and 4th years running Windows 10/11 Command Prompt or PowerShell, and department faculty/lab coordinators.
* **Key Constraints:**
  * Windows-native terminal support (CMD & PowerShell).
  * Strict 7-second countdown per prompt with real-time progress bar rendering above the active input line.
  * Focus-aware standalone `ALT` emergency kill-switch terminating instantly and silently.
  * 100% offline-first capability via local SQLite and cached files.
  * Background daemon automatically pre-caching the entire department catalog and code files.
* **Explicit Non-Goals:**
  * No code execution or auto-compilation (Strawberry only retrieves, verifies, caches, and copies code).
  * No student login or account requirements (Lite is 100% free and open access).
  * No separate semester screen in Lite (year selection presents all subjects across both semesters).

---

## 3. Assumptions & Policies

1. **Phased Milestone Delivery:** Milestone 1 focuses on the Core Engine, Lite CLI, 7s Countdown Handler, Silent Focus-Aware ALT Hook, Local SQLite Storage, Cache Downloader, Windows Startup Background Sync Daemon, and the Admin Web App. (Strawberry Pro Textual TUI and Inno Setup installer are Milestone 2).
2. **Security Model:** Students use public/anonymous Supabase credentials restricted to read-only RLS policies. Faculty log in via Supabase Auth. No administrator or service-role keys are ever packaged into the client executable.
3. **Clipboard Management:** Clipboard operations use UTF-8 encoding with Windows CRLF preservation. If the OS denies clipboard access, the CLI outputs a clean message with the exact local file path.
4. **Seed Database:** The client ships with a bundled SQLite seed database so it is 100% operational immediately upon installation even if the first run occurs without an internet connection.

---

## 4. Decision Log

| ID | Topic | Decision | Alternatives Considered | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **D1** | Scope & Milestones | Milestone 1 implements Core, Lite CLI, 7s Timer, ALT switch, Storage, Sync Daemon, and Admin Web App. | Full end-to-end spec or prototype-first. | De-risks the fundamental user value and backend data pipeline before TUI and installer packaging. |
| **D2** | Data Architecture | Fully offline-first with background sync daemon. | Direct API query on startup or on-demand download. | Ensures instantaneous (<100ms) startup and reliable operation in disconnected or firewalled university lab rooms. |
| **D3** | 7s Timer Rendering | Visual ASCII progress bar (`[███████] 7s`) rendered on the line above the input prompt. | In-place status line below prompt or inline prompt badge. | Prevents cursor jumping and text corruption when students type, backspace, or correct input. |
| **D4** | Emergency Kill-Switch | Focus-aware standalone `ALT` key detection; exits silently (`os._exit(0)`) with 0 console output. | System-wide global hook or visible exit banner. | Prevents accidental app termination when switching windows (`ALT+TAB`), while providing instant discreet exit. |
| **D5** | Pre-Caching Depth | Full pre-caching of catalog metadata and all experiment source files upon internet availability. | On-demand file download or tiered year-only caching. | Lab source files are small (KB scale). Pre-caching ensures complete offline availability in labs. |
| **D6** | Admin Portal Stack | Lightweight React + Vite + Tailwind SPA with Supabase Auth & Storage. | Python FastAPI/Streamlit or Supabase Studio only. | Provides an intuitive, responsive drag-and-drop experience for non-technical faculty with zero backend deployment friction. |
| **D7** | System Architecture | Layered Modular Architecture with Win32 Console Controller (Approach 1). | `prompt_toolkit` / asyncio or procedural monolith. | Guarantees microsecond startup latency, clean separation of concerns, and full reuse for the upcoming Pro TUI. |

---

## 5. System Architecture & Component Specifications

```
┌──────────────────────────────────────────────────────────┐
│              Faculty / Lab Coordinators                  │
│             [ Strawberry Admin Web App ]                 │
│              (React + Vite + Tailwind)                   │
└────────────────────────────┬─────────────────────────────┘
                             │ Authenticated HTTPS (RLS)
                             ▼
┌──────────────────────────────────────────────────────────┐
│                   Supabase Cloud                         │
│   ├── PostgreSQL (Years, Subjects, Experiments, Versions)│
│   └── Storage Bucket (Public Read-Only Source Files)     │
└──────────────┬────────────────────────────┬──────────────┘
               │ Read-Only Sync             │ Read-Only Sync
               ▼                            ▼
┌──────────────────────────────┐  ┌────────────────────────┐
│     Windows Startup          │  │     Student Console    │
│  [ Background Sync Daemon ]  │  │  [ Strawberry Lite CLI]│
│  (Polls every 3–5 min)       │  │  (Interactive 7s Input)│
└──────────────┬───────────────┘  └───────────┬────────────┘
               │ Reconciles & Pre-caches      │ Instant SQLite Read
               ▼                              ▼
┌──────────────────────────────────────────────────────────┐
│         Local Storage (%LOCALAPPDATA%\Strawberry\)       │
│   ├── catalog.db (SQLite)                                │
│   └── cache/ (SHA-256 verified source files)             │
└──────────────────────────────────────────────────────────┘
```

### 5.1 Strawberry Lite CLI Workflow
1. **Welcome Screen:** Displays department branding and prompts for Academic Year (2nd, 3rd, 4th) with an active 7-second countdown bar.
2. **Subject Selection:** Displays all subjects for both semesters of the chosen year with semester badges (e.g. `[Sem 3] Computer Networks`). 7s timer restarts.
3. **Experiment Selection:** Lists all laboratory experiments with two-digit index numbers (e.g. `01. Socket Programming`). 7s timer restarts.
4. **Retrieval & Clipboard:** Fetches the verified file from `%LOCALAPPDATA%\Strawberry\cache\`, verifies its SHA-256 hash, and copies the complete text into the Windows clipboard using native Win32 API / `pyperclip`. Prints completion confirmation and exits cleanly.

### 5.2 Windows Console Engine (`core/`)
* **`timer.py` & `input_handler.py`:**
  * Uses `msvcrt.kbhit()` and `msvcrt.getwch()` in a non-blocking loop with `time.monotonic()`.
  * Renders a 7-bar visual indicator: `[███████] 7s`, decrementing every second.
  * ANSI escape sequences (`\033[s`, `\033[A\r\033[K`, `\033[u`) ensure the countdown updates cleanly on the line above without interfering with typed keystrokes or backspaces.
  * Valid input proceeds immediately. Invalid input re-renders the error prompt and resets the countdown deadline to 7 seconds. Timeout automatically terminates the process.
* **`keyboard_controller.py` (ALT Kill-Switch):**
  * Spawns a dedicated thread with a Win32 Low-Level Keyboard Hook (`WH_KEYBOARD_LL`).
  * Validates window focus: `GetForegroundWindow() == GetConsoleWindow()`.
  * State tracking: If `VK_MENU` (ALT) is pressed, records timestamp. If any other key event occurs before release, marks as combo.
  * If released alone while focused: instantly calls `os._exit(0)` with zero console noise.
  * Cleans up hook handles automatically via `atexit`.

### 5.3 Local Storage & Background Sync Daemon
* **Local Root:** `%LOCALAPPDATA%\Strawberry\`
  * `catalog.db`: SQLite database storing synchronized catalog records.
  * `cache/{subject_code}/{exp_num}_{version}.{ext}`: Cached source files.
  * `sync_state.json`: Last sync timestamp, status, and catalog version.
* **Background Daemon (`strawberry daemon`):**
  * Invoked headless (via `pythonw.exe` or `CREATE_NO_WINDOW`).
  * Checks network reachability via a lightweight `httpx.head` request.
  * Sync cycle:
    1. Fetches remote catalog metadata from Supabase and performs upsert into local SQLite.
    2. Compares local cached files against remote SHA-256 hashes.
    3. Downloads missing or updated files to temporary `.tmp` buffers, validates SHA-256, and atomically replaces cached files.
    4. Sleeps for 3–5 minutes before the next polling cycle.

### 5.4 Strawberry Admin Web App
* **Tech Stack:** React 18, Vite, Tailwind CSS, Lucide React, `@supabase/supabase-js`.
* **Features:**
  * Secure email/password login via Supabase Auth.
  * Hierarchy explorer: Years -> Semesters -> Subjects -> Experiments.
  * Create/Update/Archive subjects and experiments.
  * Drag-and-drop file upload with client-side SHA-256 calculation via Web Crypto API (`crypto.subtle.digest`).
  * In-browser code preview with syntax highlighting.
  * Direct upload to Supabase Storage and atomic version commit.

---

## 6. Database Schema (Supabase PostgreSQL & Local SQLite)

```sql
-- Academic Years
CREATE TABLE years (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    year_number INT NOT NULL UNIQUE, -- 2, 3, 4
    display_name TEXT NOT NULL        -- "2nd Year", "3rd Year", "4th Year"
);

-- Semesters
CREATE TABLE semesters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    year_id UUID NOT NULL REFERENCES years(id) ON DELETE CASCADE,
    semester_number INT NOT NULL,     -- 3, 4, 5, 6, 7, 8
    display_name TEXT NOT NULL        -- "Semester 3", etc.
);

-- Subjects
CREATE TABLE subjects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    semester_id UUID NOT NULL REFERENCES semesters(id) ON DELETE CASCADE,
    subject_code TEXT NOT NULL UNIQUE, -- e.g. "CS301"
    subject_name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Experiments
CREATE TABLE experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    experiment_number INT NOT NULL,   -- 1, 2, 3...
    title TEXT NOT NULL,
    description TEXT,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(subject_id, experiment_number)
);

-- Experiment Versions
CREATE TABLE experiment_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    version_number INT NOT NULL DEFAULT 1,
    storage_path TEXT NOT NULL,       -- Path in Supabase Storage
    filename TEXT NOT NULL,           -- e.g. "SocketServer.java"
    sha256 TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 7. Project Structure

```text
Strawberry/
├── docs/
│   ├── architecture.md          # This validated design specification
│   ├── installation.md
│   └── admin-guide.md
│
├── strawberry-cli/              # Python Client & Daemon
│   ├── src/
│   │   └── strawberry/
│   │       ├── __init__.py
│   │       ├── main.py          # Entry point (CLI router: lite, pro, daemon)
│   │       ├── cli.py
│   │       ├── core/
│   │       │   ├── application.py
│   │       │   ├── config.py
│   │       │   ├── timer.py
│   │       │   ├── input_handler.py
│   │       │   └── keyboard_controller.py
│   │       ├── lite/
│   │       │   ├── interface.py
│   │       │   └── workflow.py
│   │       ├── repository/
│   │       │   ├── base.py
│   │       │   ├── sqlite_repo.py
│   │       │   ├── supabase_sync.py
│   │       │   └── mock_data.py
│   │       ├── services/
│   │       │   ├── clipboard.py
│   │       │   ├── cache.py
│   │       │   └── daemon.py
│   │       └── models/
│   │           ├── academic.py
│   │           ├── subject.py
│   │           └── experiment.py
│   ├── tests/
│   │   ├── test_timer.py
│   │   ├── test_input_handler.py
│   │   ├── test_keyboard.py
│   │   ├── test_clipboard.py
│   │   ├── test_storage.py
│   │   └── test_daemon.py
│   └── pyproject.toml
│
├── strawberry-admin/            # React + Vite + Tailwind Admin Web App
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── lib/
│   │   │   ├── supabase.ts
│   │   │   └── crypto.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
└── supabase/                    # Backend Migrations & Seed
    ├── migrations/
    │   └── 001_initial_schema.sql
    └── seed.sql
```

---

## 8. Implementation Phases (Milestone 1)

1. **Phase 1: Project Initialization & Core Input Engine**
   * Set up Python workspace with `pyproject.toml` and dependencies (`httpx`, `pyperclip`, `rich`, `pytest`).
   * Implement `timer.py` and `input_handler.py` with 7s countdown, visual progress bar, and keystroke buffer.
   * Implement `keyboard_controller.py` with focus-aware Win32 `WH_KEYBOARD_LL` silent ALT hook.
   * Write and execute unit tests for the timer and input handlers.
2. **Phase 2: Local Storage, Models & Seed Catalog**
   * Implement Pydantic data models for Year, Semester, Subject, Experiment, Version.
   * Implement `sqlite_repo.py` managing `%LOCALAPPDATA%\Strawberry\catalog.db`.
   * Create seed demo catalog with realistic computer science laboratory programs.
   * Implement `cache.py` managing local file storage and SHA-256 verification.
3. **Phase 3: Strawberry Lite Workflow & Clipboard Engine**
   * Build the complete guided terminal workflow (`lite/workflow.py` and `lite/interface.py`).
   * Integrate native clipboard copying with CRLF preservation and verification.
   * Test end-to-end Lite flow with 7-second timers and offline cached data.
4. **Phase 4: Supabase Backend & Background Sync Daemon**
   * Write Supabase migration scripts with PostgreSQL tables, indexes, and RLS policies.
   * Build `supabase_sync.py` to reconcile remote catalog updates and download missing code files.
   * Build `services/daemon.py` (`strawberry daemon`) with periodic 3–5 minute polling loop and Windows startup registration.
5. **Phase 5: Strawberry Admin Web App**
   * Initialize Vite + React + Tailwind frontend in `strawberry-admin/`.
   * Implement Supabase Auth, catalog explorer, and experiment editor.
   * Implement drag-and-drop file upload with automated browser-side SHA-256 generation.
