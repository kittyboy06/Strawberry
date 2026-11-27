# Design Specification: Admin Portal Auth & CLI/Pro Parity

> **Status:** Validated via Brainstorming  
> **Scope:** `strawberry-admin` (Supabase Auth & RLS Write Access) + `strawberry-cli` (Clean Sync Mirroring, Standalone Config Defaults, & `Strawberry Pro` Parity)

---

## 1. Understanding Summary

* **What Is Being Built:**
  1. Full-portal Supabase Email & Password authentication gate (`signInWithPassword`) in `strawberry-admin`, wiring faculty JWT sessions to all catalog and Storage (`programs` bucket) mutations.
  2. Transactional Supabase-to-SQLite sync mirroring in `strawberry-cli` that prunes stale/mock rows and orphaned cache files, skips initial demo seeding when remote Supabase is configured, and embeds public Supabase URL + Publishable Key defaults for standalone `strawberry.exe`.
  3. Core `Strawberry Pro` TUI parity in `pro/app.py`: SHA-256 verification before clipboard copy, persisted Bookmarks & Recent History (`pro_state.json`), and unified subject + program search.
* **Why It Exists:** Faculty require authenticated browser write access compatible with strict `TO authenticated` PostgreSQL/Storage RLS policies, while students need `strawberry.exe` to work standalone without leftover mock records or unverified copies.
* **Who It Is For:** Engineering department faculty/lab coordinators (Web Admin) and 2nd–4th year students on Windows lab workstations (CLI).
* **Key Constraints:** Zero secret keys (`sb_secret_...`) in client bundles; preserve existing porcelain pink Admin UI aesthetic; preserve sub-100ms offline startup, 7-second countdown, and focus-aware `ALT` kill switch in CLI.
* **Explicit Non-Goals:** Student/public self-registration in Admin; Inno Setup `.exe` installer build; multi-college tenancy; in-TUI manual sync hotkey.

---

## 2. Assumptions & Non-Functional Requirements

* **Security:** Public sign-ups are disabled in Supabase Auth Dashboard; faculty accounts are provisioned by administrators in Supabase Auth. Client binaries and bundles contain only `SUPABASE_URL` and `PUBLISHABLE_KEY` (`sb_publishable_...`).
* **Performance & Scale:** ~100–500 workstations pulling ~50–200 source files; Pro user state (`pro_state.json`) stays lightweight (history capped at 15 entries) so TUI mount remains <100ms.
* **Reliability:** Sync validates all 5 REST responses (`200 OK` JSON arrays) before pruning local SQLite tables or cache files, preventing partial network failures from wiping offline data.
* **Integrity:** Both `lite` and `pro` block clipboard copy (`verify_integrity()`) if a cached file fails SHA-256 verification.

---

## 3. Decision Log

| # | Decision | Alternatives Considered | Rationale |
| :-: | :--- | :--- | :--- |
| **D1** | Full-portal Email & Password login gate in `strawberry-admin` | Public read-only portal with edit unlock modal; Passwordless Magic Link | Protects department catalog & telemetry from unauthenticated access and maps directly to `TO authenticated` RLS. |
| **D2** | Keep existing `TO authenticated` RLS policies + disable public sign-up in Supabase | New SQL migration adding a role/email allowlist table | Zero migration risk; clean separation when sign-ups are disabled by the project admin. |
| **D3** | Embed public Supabase URL + Publishable Key defaults directly in `config.py` (overridable via `.env`) | Bundling `.env` via PyInstaller `datas`; external `.env` copy step | Standalone `strawberry.exe` works out of the box on clean PCs with zero risk of bundling `STRAWBERRY_SUPABASE_SECRET_KEY`. |
| **D4** | Skip demo seed when Supabase is configured + prune stale rows/cache in a single transaction | Keep mock rows on cold start then wipe later; drop & recreate DB file | Keeps synced college catalog exact with zero leftover demo items and avoids Windows SQLite file-lock issues. |
| **D5** | Persist Pro Bookmarks & History in separate `%LOCALAPPDATA%\Strawberry\pro_state.json` | Add user tables to `catalog.db`; session-only memory state | Decouples personal student preferences from synced catalog pruning and persists across 7s inactivity exits. |

---

## 4. Final Design

### Track 1: Admin Portal Authentication (`strawberry-admin`)
1. **`src/components/LoginScreen.tsx`**
   * Renders a centered porcelain-themed card matching the `#FDEBEC` → `#FEF6F5` gradient, botanical logo, and Playfair Display typography.
   * Inputs: `email` and `password`, loading state, accessible inline error message on failed `supabase.auth.signInWithPassword()`.
2. **`src/App.tsx` Auth Lifecycle**
   * Tracks `session: Session | null` and `isAuthLoading: boolean` using `supabase.auth.getSession()` and `supabase.auth.onAuthStateChange()`.
   * Displays `<LoginScreen />` whenever `isSupabaseConfigured && !session`.
   * Displays signed-in user email and **Sign Out** button (`supabase.auth.signOut()`) in the Header/Settings view.
   * Gracefully handles expired sessions (`401`/`403`/RLS `42501`) by notifying the user to re-authenticate.

### Track 2: CLI Config, Sync Mirroring & `Strawberry Pro` (`strawberry-cli`)
1. **Standalone Configuration (`src/strawberry_cli/core/config.py`)**
   * Provides default fallback constants for `SUPABASE_URL` and `PUBLISHABLE_KEY` (`sb_publishable_...`), respecting `.env` and environment variable overrides (`STRAWBERRY_*`, `VITE_*`).
2. **Clean SQLite Repo & Transactional Sync (`repository/sqlite_repo.py`, `repository/supabase_sync.py`)**
   * `SQLiteCatalogRepository(..., seed_demo: Optional[bool] = None)` seeds `mock_data` only when `seed_demo is True` or (`seed_demo is None` and `not config.base_supabase_url`).
   * `SupabaseSyncService.sync()` fetches `years`, `semesters`, `subjects`, `experiments`, and `experiment_versions`, verifies `status_code == 200` and `isinstance(payload, list)` for every table, then inside one SQLite transaction runs `INSERT OR REPLACE` followed by `DELETE` for IDs not present remotely (reverse FK order: `experiment_versions` → `experiments` → `subjects` → `semesters` → `years`), then removes unreferenced files in `cache_dir`.
3. **`Strawberry Pro` Parity (`services/pro_state.py`, `pro/app.py`)**
   * **`ProStateService`:** Reads/writes `%LOCALAPPDATA%\Strawberry\pro_state.json` (`bookmarks: list[str]`, `history: list[dict]` capped at 15 entries).
   * **Integrity Check:** `action_copy_code()` calls `cache_service.verify_integrity(version.filename, version.sha256)` before copying; on mismatch, notifies error and blocks copy; on success, records copy in `history`.
   * **UI Enhancements:** `[B]` hotkey / button to toggle bookmark (`★` indicator), filter mode buttons (`All` / `Bookmarks` / `Recent`), and `/` search filtering across both subject names/codes and experiment titles.

---

## 5. Verification Plan

* **Admin Web App:** `npm run build` (`tsc -b && vite build`) + `npm run lint` (`oxlint`) cleanly pass; verify unauthenticated redirect to `<LoginScreen />` and authenticated build flow.
* **CLI & Pro Tests:** Add/update automated `pytest` tests in `strawberry-cli/tests/` covering:
  * Sync pruning of stale/mock SQLite rows and orphaned cache files.
  * Partial-failure guard (non-200 response aborts without deleting cached catalog).
  * `ProStateService` bookmark toggle and capped history persistence.
  * `StrawberryProApp.action_copy_code()` rejecting corrupted SHA-256 cached files.
* **Packaging & Live Sync:** Rebuild `strawberry-cli/dist/strawberry.exe`, run `strawberry sync` to prune stale demo rows in local `%LOCALAPPDATA%\Strawberry\catalog.db`, and verify `uv run pytest` passes 100%.
