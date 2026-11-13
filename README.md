# Strawberry 🍓
> **"Pick your program. Paste your code."**

Strawberry is an offline-first laboratory program retrieval system designed specifically for engineering college departments (2nd, 3rd, and 4th-year students). It completely replaces disorganized code distribution channels—such as WhatsApp group messages, scattered Google Drive links, and messy repositories—with a single, ultra-fast Windows command-line utility and a unified faculty admin portal.

With Strawberry, students open their terminal, make three quick selections, and immediately receive verified source code copied directly to their Windows clipboard ready to paste (`CTRL + V`).

---

## 📑 Table of Contents
- [Key Features](#key-features)
- [Architecture & Data Flow](#architecture--data-flow)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [1. Clone Repository](#1-clone-repository)
  - [2. Setting Up Strawberry CLI](#2-setting-up-strawberry-cli)
  - [3. Setting Up Strawberry Admin Portal](#3-setting-up-strawberry-admin-portal)
  - [4. Setting Up Supabase Backend](#4-setting-up-supabase-backend)
- [Environment Variables](#environment-variables)
- [Available Commands & Scripts](#available-commands--scripts)
- [Project Directory Structure](#project-directory-structure)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [Production Deployment & Windows Packaging](#production-deployment--windows-packaging)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## 🌟 Key Features

### 🖥️ Strawberry Lite CLI
* **Sub-100ms Instant Startup:** Zero network handshake latency on startup; reads immediately from local SQLite.
* **Non-Blocking 7-Second Countdown:** Every prompt displays an animated, real-time ASCII progress bar (`[███████] 7s`) rendered on the line above the input without flickering or garbling typed keystrokes.
* **Timer Reset on Invalid Input:** Input errors display clear guidance and restart the 7-second countdown. Expiration automatically terminates the process cleanly.
* **Focus-Aware Standalone ALT Kill-Switch:** Pressing and releasing the standalone `ALT` key when Strawberry is focused terminates the application instantly with 0 terminal output. Combinations like `ALT+TAB` and `ALT+F4` are safely ignored.
* **Direct Clipboard Integration:** Automatically copies code to the Windows clipboard with full UTF-8 and native Windows CRLF line-ending preservation.
* **SHA-256 Integrity Verification:** Every retrieved program is checked against its cryptographic hash before copying to ensure zero corruption or tampering.

### 🔄 Offline-First & Background Sync
* **100% Disconnected Operation:** Local SQLite database (`catalog.db`) and file cache (`cache/`) stored in `%LOCALAPPDATA%\Strawberry\`. Works inside firewalled or offline college lab rooms.
* **Windows Startup Daemon:** Background worker (`strawberry daemon`) registers in Windows Startup (`shell:startup`) and checks for network connectivity every 3–5 minutes, silently pre-caching the entire department catalog and code files.

### 👩‍🏫 Faculty Admin Web App
* **Curriculum Management:** Clean web interface for faculty to organize academic years, semesters, and subjects.
* **Drag-and-Drop Publishing:** Upload source code files (`.py`, `.java`, `.c`, `.cpp`, `.sql`) with automatic in-browser SHA-256 calculation via Web Crypto API.
* **Row-Level Security (RLS):** Authenticated staff can publish/update programs; student CLI clients maintain secure public read-only access.

---

## 🏗️ Architecture & Data Flow

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
│   └── Storage Bucket (Encrypted Source Files)            │
└──────────────┬────────────────────────────┬──────────────┘
               │ Read-Only (Anon)           │ Read-Only (Anon)
               ▼                            ▼
┌──────────────────────────────┐  ┌────────────────────────┐
│     Windows Startup          │  │     Student Console    │
│  [ Background Sync Daemon ]  │  │  [ Strawberry Lite CLI]│
│  (Polls every 3–5 min)       │  │  (Interactive 7s Input)│
└──────────────┬───────────────┘  └───────────┬────────────┘
               │ Reconciles & Pre-caches      │ Instant Reads (<5ms)
               ▼                              ▼
┌──────────────────────────────────────────────────────────┐
│         Local Storage (%LOCALAPPDATA%\Strawberry\)       │
│   ├── catalog.db (SQLite)                                │
│   └── cache/ (SHA-256 verified source files)             │
└──────────────────────────────────────────────────────────┘
```

### Student Retrieval Lifecycle
1. Student types `strawberry` in Command Prompt or PowerShell.
2. Background Win32 low-level hook starts listening for emergency focus-aware `ALT` key events.
3. System loads Academic Years from local SQLite (`catalog.db`).
4. Student selects Year (`1. 2nd Year`, `2. 3rd Year`, `3. 4th Year`) under a 7-second countdown.
5. All subjects for both semesters of that year are displayed (e.g., `[Sem 3] Computer Networks`).
6. Student inputs the experiment index (`01. Socket Programming`).
7. CLI reads the cached source file, verifies its SHA-256 hash, and copies it to the Windows clipboard.
8. CLI outputs confirmation and terminates automatically. Student presses `CTRL + V` to paste code anywhere.

---

## 💻 Tech Stack

### Core CLI (`strawberry-cli`)
* **Language:** Python 3.11+
* **Package Manager:** `uv`
* **CLI Routing & Terminal UI:** Typer, Rich
* **Console & Input:** Win32 API (`ctypes`), `msvcrt`, `time.monotonic()`
* **Low-Level Keyboard Hook:** Win32 `WH_KEYBOARD_LL` (focus-aware via `GetForegroundWindow()`)
* **Local Database:** SQLite3 (`%LOCALAPPDATA%\Strawberry\catalog.db`)
* **Local Storage & Cache:** File system with SHA-256 verification
* **Clipboard:** Native Win32 Clipboard API (`OpenClipboard`, `SetClipboardData`) + `pyperclip` fallback
* **Sync Client:** `httpx`

### Admin Portal (`strawberry-admin`)
* **Framework:** React 18 + Vite
* **Language:** TypeScript
* **Styling:** Tailwind CSS v4
* **Icons:** Lucide React
* **Backend Client:** `@supabase/supabase-js`
* **Cryptography:** Browser Web Crypto API (`crypto.subtle`)

### Backend (`supabase`)
* **Database:** PostgreSQL with Row-Level Security (RLS)
* **File Storage:** Supabase Storage (`programs` bucket)
* **Authentication:** Supabase Auth (Faculty administrators)

---

## 📋 Prerequisites

* **Operating System:** Windows 10 or Windows 11 (Command Prompt or PowerShell)
* **Python:** Python 3.11 or higher (managed via `uv` or standard Python)
* **Node.js:** Node.js v18 or higher with `npm` (for the Admin Web App)
* **Package Manager:** `uv` recommended for ultra-fast Python builds (`pip install uv` or `winget install astral-sh.uv`)

---

## 🚀 Getting Started

### 1. Clone Repository

```bash
git clone https://github.com/Kittyboy06/Strawberry.git
cd Strawberry
```

---

### 2. Setting Up Strawberry CLI

The Python CLI lives in `strawberry-cli/`:

```bash
cd strawberry-cli

# Install dependencies into virtual environment using uv
uv sync

# Launch the Strawberry Lite CLI interface
uv run strawberry

# View CLI options and commands
uv run strawberry --help
```

---

### 3. Setting Up Strawberry Admin Portal

The faculty web dashboard lives in `strawberry-admin/`:

```bash
cd ../strawberry-admin

# Install dependencies
npm install

# Start local development server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

To build the production web assets:
```bash
npm run build
```

---

### 4. Setting Up Supabase Backend

1. Create a project at [Supabase](https://supabase.com).
2. Open the **SQL Editor** in your Supabase dashboard.
3. Run the schema migration script located at [`supabase/migrations/001_initial_schema.sql`](file:///e:/Projects/Works/Strawberry/supabase/migrations/001_initial_schema.sql).
4. Run the seed data script located at [`supabase/seed.sql`](file:///e:/Projects/Works/Strawberry/supabase/seed.sql).
5. Copy your **Project URL** and **Anon Public Key** from `Settings -> API`.

---

## 🔐 Environment Variables

### CLI Configuration (`strawberry-cli`)

Configuration can be set via system environment variables:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `STRAWBERRY_SUPABASE_URL` | Supabase Project URL for remote sync | `""` (Uses local demo catalog) |
| `STRAWBERRY_SUPABASE_ANON_KEY` | Public anonymous read key | `""` |
| `LOCALAPPDATA` | Windows Local AppData directory | `%USERPROFILE%\AppData\Local` |

### Admin Web App (`strawberry-admin/.env`)

Create a `.env` file inside `strawberry-admin/`:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOi...
```

*Note: If no Supabase credentials are provided, both the CLI and the Admin Web App run in complete offline demonstration mode with built-in curriculum data.*

---

## 🛠️ Available Commands & Scripts

### Strawberry CLI Commands

| Command | Description |
| :--- | :--- |
| `strawberry` | Launch the primary guided Strawberry Lite terminal interface. |
| `strawberry lite` | Explicitly launch the Lite interface. |
| `strawberry pro` | Launch the advanced Strawberry Pro interactive TUI. |
| `strawberry daemon` | Run the background synchronization worker. |
| `strawberry daemon --interval 180` | Run daemon with custom polling interval (in seconds). |
| `strawberry sync` | Trigger a manual one-shot synchronization check with Supabase. |
| `strawberry install-startup` | Automatically register the background daemon in Windows Startup (`shell:startup`). |
| `strawberry --version` | Output application version and tagline. |

### Development & Build Scripts

| Directory | Command | Description |
| :--- | :--- | :--- |
| `strawberry-cli/` | `uv run pytest` | Execute full automated Python test suite. |
| `strawberry-admin/` | `npm run dev` | Launch local Vite dev server with HMR. |
| `strawberry-admin/` | `npm run build` | Compile TypeScript and bundle production web assets. |
| `strawberry-admin/` | `npm run preview` | Preview production build locally. |

---

## 📂 Project Directory Structure

```text
Strawberry/
├── docs/
│   └── architecture.md            # Complete validated design specification
│
├── strawberry-cli/                # Python CLI & Background Sync Daemon
│   ├── src/
│   │   └── strawberry_cli/
│   │       ├── __init__.py
│   │       ├── main.py            # CLI command router
│   │       ├── core/
│   │       │   ├── config.py      # App paths (%LOCALAPPDATA%) & settings
│   │       │   ├── timer.py       # 7-second countdown & progress bar renderer
│   │       │   ├── input_handler.py # Non-blocking input & cursor control
│   │       │   └── keyboard_controller.py # Focus-aware silent ALT hook
│   │       ├── lite/
│   │       │   ├── interface.py   # Screen rendering & formatting
│   │       │   └── workflow.py    # 4-step guided student journey
│   │       ├── models/            # Pydantic data models
│   │       ├── repository/
│   │       │   ├── base.py        # Abstract repository contract
│   │       │   ├── sqlite_repo.py # Offline SQLite storage manager
│   │       │   ├── mock_data.py   # Seed demonstration curriculum
│   │       │   └── supabase_sync.py # Remote Supabase reconciliation
│   │       └── services/
│   │           ├── cache.py       # Local file cache & SHA-256 verification
│   │           ├── clipboard.py   # Windows UTF-8/CRLF clipboard service
│   │           └── daemon.py      # Background sync loop & Windows Startup
│   ├── tests/
│   │   ├── test_timer.py          # Timer & progress bar tests
│   │   ├── test_storage.py        # SQLite & cache integrity tests
│   │   ├── test_clipboard.py      # Line endings & clipboard tests
│   │   └── test_workflow.py       # End-to-end simulated CLI workflow tests
│   └── pyproject.toml
│
├── strawberry-admin/              # React + Vite + Tailwind Admin Web App
│   ├── src/
│   │   ├── components/            # Navbar, UploadModal, etc.
│   │   ├── lib/                   # Supabase client & Web Crypto SHA-256
│   │   ├── types/                 # TypeScript interfaces
│   │   ├── App.tsx                # Curriculum dashboard & uploader
│   │   ├── main.tsx
│   │   └── index.css              # Tailwind styling
│   ├── package.json
│   └── vite.config.ts
│
├── supabase/                      # Cloud Backend Database
│   ├── migrations/
│   │   └── 001_initial_schema.sql # Tables, RLS policies, storage bucket
│   └── seed.sql                   # Sample curriculum data
│
├── .gitignore                     # Git ignore rules
└── README.md                      # This documentation
```

---

## 🗄️ Database Schema

```
years
├── id (UUID, PK)
├── year_number (INT, UNIQUE: 2, 3, 4)
└── display_name (TEXT: "2nd Year", "3rd Year", "4th Year")

semesters
├── id (UUID, PK)
├── year_id (UUID, FK → years.id)
├── semester_number (INT: 3 to 8)
└── display_name (TEXT: "Semester 3", etc.)

subjects
├── id (UUID, PK)
├── semester_id (UUID, FK → semesters.id)
├── subject_code (TEXT, UNIQUE: "CS301")
├── subject_name (TEXT: "Computer Networks")
└── is_active (BOOLEAN)

experiments
├── id (UUID, PK)
├── subject_id (UUID, FK → subjects.id)
├── experiment_number (INT: 1, 2, 3...)
├── title (TEXT: "Socket Programming")
├── description (TEXT)
└── is_published (BOOLEAN)

experiment_versions
├── id (UUID, PK)
├── experiment_id (UUID, FK → experiments.id)
├── version_number (INT)
├── storage_path (TEXT: "programs/CS301_01_v1.java")
├── filename (TEXT: "SocketServer.java")
└── sha256 (TEXT: Cryptographic hash)
```

---

## 🧪 Testing

Strawberry includes a comprehensive automated test suite testing timer math, cursor buffers, SQLite connections, file hashing, and full CLI workflows.

To run the test suite:

```bash
cd strawberry-cli
uv run pytest -v
```

Expected output:
```text
tests/test_clipboard.py::test_line_endings_normalization PASSED
tests/test_clipboard.py::test_clipboard_copy PASSED
tests/test_storage.py::test_sqlite_repository_initialization_and_seed PASSED
tests/test_storage.py::test_cache_service PASSED
tests/test_timer.py::test_timer_initial_state PASSED
tests/test_timer.py::test_timer_countdown_and_bar PASSED
tests/test_timer.py::test_timer_expiration PASSED
tests/test_workflow.py::test_end_to_end_lite_workflow PASSED

============================== 8 passed in 1.50s ==============================
```

---

## 📦 Production Deployment & Windows Packaging

### Standalone Executable Packaging (`strawberry.exe`)
To package the CLI as a single standalone Windows executable that students can run without Python installed:

```bash
cd strawberry-cli
uv run pyinstaller --onefile --name strawberry src/strawberry_cli/main.py
```
The output binary will be generated at `strawberry-cli/dist/strawberry.exe`.

### Windows Startup Registration
To enable automatic background synchronization on login:
```bash
strawberry install-startup
```
This registers a background VBScript launcher in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\StrawberryDaemon.vbs` which silently invokes `strawberry daemon` using `pythonw.exe` without creating a console window.

### Deploying the Admin Portal
The `strawberry-admin` Vite app can be deployed in one click to [Vercel](https://vercel.com), [Netlify](https://netlify.com), or [Cloudflare Pages]:
1. Connect your GitHub repository.
2. Set Root Directory to `strawberry-admin`.
3. Set Build Command to `npm run build` and Output Directory to `dist`.
4. Configure `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` in your hosting dashboard's Environment Variables.

---

## 🔧 Troubleshooting

### 1. Terminal ANSI Colors / Progress Bar Not Rendering
* **Cause:** Older Windows Command Prompt sessions without Virtual Terminal processing enabled.
* **Resolution:** Strawberry automatically enables `ENABLE_VIRTUAL_TERMINAL_PROCESSING` (0x0004) via the Win32 Console API on launch. If running in a legacy terminal, upgrade to the latest Windows Terminal or PowerShell.

### 2. Standalone ALT Key Kill-Switch Not Triggering
* **Cause:** Strawberry's console window does not have foreground focus, or another key was pressed simultaneously (such as `ALT+TAB`).
* **Resolution:** Click inside the Strawberry terminal window to focus it. Tap the `ALT` key alone without holding other keys.

### 3. Clipboard Access Denied
* **Cause:** Restrictive Windows Group Policy or another background application locking the clipboard.
* **Resolution:** Strawberry will output a yellow notice and display the exact local path to the verified cached source code file (e.g., `%LOCALAPPDATA%\Strawberry\cache\socket_server.py`) so you can open or copy it manually.

### 4. Background Sync Offline Notice
* **Cause:** No internet connection or university firewall blocking Supabase endpoints.
* **Resolution:** Strawberry is offline-first! It automatically uses the cached local SQLite catalog and previously downloaded programs. Background sync will resume seamlessly once network connectivity is restored.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](file:///e:/Projects/Works/Strawberry/LICENSE) file for details.
