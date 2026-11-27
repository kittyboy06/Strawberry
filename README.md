# Strawberry 🍓
> **"Pick your program. Paste your code."**

[![CI](https://github.com/Kittyboy06/Strawberry/actions/workflows/ci.yml/badge.svg)](https://github.com/Kittyboy06/Strawberry/actions/workflows/ci.yml)
[![Release v0.1.0](https://img.shields.io/badge/release-v0.1.0-c92a42.svg)](https://github.com/Kittyboy06/Strawberry/releases/tag/v0.1.0)
[![Admin Portal](https://img.shields.io/badge/Admin_Portal-Live_on_Vercel-black.svg)](https://strawberry-cli.vercel.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

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

### 🔄 Offline-First & Background Sync (Default on Install)
* **100% Disconnected Operation:** Local SQLite database (`catalog.db`) and file cache (`cache/`) stored in `%LOCALAPPDATA%\Strawberry\`. Works inside firewalled or offline college lab rooms.
* **Automatic Setup by Default:** Configured automatically upon installation! Strawberry registers a headless VBScript launcher in Windows Startup (`shell:startup`) and launches the background sync daemon without requiring any manual user setup.
* **Continuous Background Sync:** The background daemon polls for internet access every 3–5 minutes and silently pre-caches the full catalog and all source code files with single-instance mutex protection.

### 👩‍🏫 Faculty Admin Web App
* **Supabase Auth Login Gate:** Email & Password sign-in (`signInWithPassword`) enforcing strict `TO authenticated` PostgreSQL and Storage RLS write policies.
* **Academic Catalog & Analytics:** Porcelain-themed workspace with dedicated tabs for Dashboard, Programs, Subjects, Semesters, Years, Versions, Live Analytics, and System Settings.
* **VS Code–Style Browser Code Authoring:** Full-height Dark+ syntax-highlighted workbench popup with line numbers, starter stubs, `Tab` indentation, `Ctrl+S` publishing, local file import, and real-time browser SHA-256 computation via Web Crypto API.
* **Zero Hardcoded Mock Data:** Live database counts, curriculum share percentages, version audit logs, and database latency ping.

---

## 📚 Additional Guides
* [Windows Installation & CLI Guide](docs/installation.md) — Student setup via `Strawberry_Setup.exe`, silent lab deployment, SmartScreen guidance, offline mode, and Windows limitations.
* [Faculty & Admin Guide](docs/admin-guide.md) — Supabase Auth setup, curriculum authoring in the VS Code workbench, Vercel deployment, and installer builds.
* [Architecture Specification](docs/architecture.md) — Core architectural decisions and data flow.
* [Code Signing Setup (Azure Trusted Signing)](docs/code-signing.md) — Independent Windows Authenticode signing for local builds and GitHub Releases.

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
3. Run the schema migration script located at [`supabase/migrations/001_initial_schema.sql`](supabase/migrations/001_initial_schema.sql).
4. Run the seed data script located at [`supabase/seed.sql`](supabase/seed.sql).
5. Copy your **Project URL** and **Publishable Key** (`sb_publishable_...`) from `Settings -> API Keys`.

---

## 🔐 Environment Variables

Strawberry supports Supabase's modern **Publishable Key** and **Secret Key** API model (with automatic fallback to legacy keys).

### Unified Root Configuration (`.env`)

You can create a single `.env` at the repository root to configure both the Python CLI and the React Admin portal simultaneously:

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `STRAWBERRY_SUPABASE_URL` | Supabase Project URL | `https://your-project.supabase.co` |
| `STRAWBERRY_SUPABASE_PUBLISHABLE_KEY` | Public client API key (`sb_publishable_...`) | `sb_publishable_...` |
| `STRAWBERRY_SUPABASE_SECRET_KEY` | Privileged backend API key (`sb_secret_...`) | `sb_secret_...` |
| `STRAWBERRY_INPUT_TIMEOUT_SECONDS` | CLI input countdown duration per prompt | `7.0` |
| `STRAWBERRY_DAEMON_POLL_INTERVAL_SECONDS`| Background sync polling interval (seconds) | `240` |

*Vite-prefixed aliases (`VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`) and legacy keys (`STRAWBERRY_SUPABASE_ANON_KEY`) are also fully supported.*

*Note: Without Supabase credentials, local SQLite initializes cleanly with empty tables ready for synchronization.*

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
├── .github/                       # CI workflows & issue/PR templates
├── docs/
│   ├── architecture.md            # Core architecture & sync specification
│   ├── installation.md            # Student Windows installation & CLI guide
│   ├── admin-guide.md             # Faculty authoring & Vercel deployment guide
│   └── design/                    # Internal concept & implementation specs
│
├── installer/
│   └── strawberry.iss             # Inno Setup 6 script for Strawberry_Setup.exe
│
├── strawberry-cli/                # Python CLI, TUI & Background Sync Daemon
│   ├── src/
│   │   └── strawberry_cli/
│   │       ├── __init__.py
│   │       ├── main.py            # CLI command router
│   │       ├── core/              # Config, timer, input & ALT kill-switch
│   │       ├── lite/              # Guided 4-step terminal interface
│   │       ├── pro/               # Full Textual TUI workspace & theme
│   │       ├── models/            # Pydantic data models
│   │       ├── repository/        # Base contract, SQLite cache & Supabase sync
│   │       └── services/          # File cache, Win32 clipboard, daemon & Pro state
│   ├── tests/                     # Pytest unit & Windows integration tests
│   └── pyproject.toml
│
├── strawberry-admin/              # React + TypeScript + Vite Admin Portal
│   ├── src/
│   │   ├── assets/                # Strawberry brand PNG assets
│   │   ├── components/            # LoginScreen, Navbar, UploadModal, VscWorkbenchModal
│   │   ├── lib/                   # Supabase client, Web Crypto SHA-256 & code stubs
│   │   ├── types/                 # TypeScript interfaces
│   │   ├── App.tsx                # Faculty curriculum & analytics workspace
│   │   ├── main.tsx
│   │   └── index.css              # Tailwind styling
│   ├── scripts/
│   │   └── seed_database.cjs      # Optional local seed importer
│   ├── package.json
│   └── vite.config.ts
│
├── supabase/                      # Cloud Backend Database
│   ├── migrations/
│   │   └── 001_initial_schema.sql # Tables, RLS policies & storage bucket
│   └── seed.sql                   # Academic years & semesters seed
│
├── .env.example                   # Environment variable template
├── .gitattributes                 # Cross-platform line-ending rules
├── .gitignore                     # Git ignore rules
├── build-release.bat              # Automated test, PyInstaller & installer builder
├── CONTRIBUTING.md                # Contributor & verification guide
├── deploy-admin-vercel.bat        # Vercel production deployment helper
├── LICENSE                        # MIT License
├── README.md                      # Project documentation
└── vercel.json                    # Vercel build & SPA routing config
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
tests/test_clipboard.py::test_line_endings_normalization PASSED          [  4%]
tests/test_clipboard.py::test_clipboard_copy PASSED                      [  9%]
tests/test_config.py::test_config_publishable_and_secret_keys PASSED     [ 13%]
...
tests/test_windows_integration.py::test_standalone_exe_runs_without_python_in_path PASSED [ 95%]
tests/test_workflow.py::test_end_to_end_lite_workflow PASSED             [100%]

============================= 22 passed in 3.94s ==============================
```

---

## 📦 Production Deployment & Windows Packaging

### Standalone Executable & Windows Installer (`Strawberry_Setup.exe`)
Run [build-release.bat](build-release.bat) from the repository root to execute `pytest`, compile `strawberry-cli/dist/strawberry.exe` via PyInstaller, bundle a gitignored 2-key client `.env` (`URL` + `Publishable Key` only), and build `dist/Strawberry_Setup.exe` via [installer/strawberry.iss](installer/strawberry.iss):
1. **Per-User Installation:** Installs into `%LOCALAPPDATA%\Strawberry\bin` with zero administrative UAC prompts.
2. **Automatic PATH & Client Config:** Adds Strawberry to the current user's `PATH` and places the read-only client `.env` inside `%LOCALAPPDATA%\Strawberry\`.
3. **Default Background Sync & Startup:** Automatically registers `StrawberryDaemon.vbs` in Windows Startup, performs an initial `sync`, and launches the background sync worker.
4. **Clean Uninstallation:** Terminates active background processes, unregisters the startup runner, deletes cached `.db`/`.json`/`.env` files, and cleanly removes only Strawberry-owned `PATH` entries.

### Deploying the Admin Portal on Vercel
Run [deploy-admin-vercel.bat](deploy-admin-vercel.bat) from the repository root (configured via [vercel.json](vercel.json)):
1. Verifies `npm run build` in `strawberry-admin/`.
2. Links the Vercel project and pushes only `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY` to Vercel Project Environment Variables.
3. Deploys `strawberry-admin` to Vercel production (`vercel deploy --prod`).

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

## 🛡️ Security, Signing & Privacy Policy

* **Independent Code Signing:** Release builds support Microsoft **Azure Trusted Signing** (both locally via [build-release.bat](build-release.bat) and in CI via [.github/workflows/release.yml](.github/workflows/release.yml)). See [docs/code-signing.md](docs/code-signing.md) for setup details.
* **Zero Telemetry:** Strawberry does not collect analytics, usage telemetry, keystrokes outside its active console focus guard, or crash reports.
* **Network Activity:** Strawberry connects solely over HTTPS to the configured Supabase project (`STRAWBERRY_SUPABASE_URL`) to synchronize published lab catalogs and verified source code files.
* **Local Storage:** Cached source files and preferences remain locally inside `%LOCALAPPDATA%\Strawberry\` on the user's workstation and are removed cleanly upon uninstall.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
