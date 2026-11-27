# Strawberry Faculty & Admin Guide

This guide explains how faculty and laboratory coordinators manage curriculum catalogs, author verified lab programs, host the Admin Portal on Vercel, and build workstation installers.

---

## 1. Supabase Setup & Faculty Authentication

1. **Create Tables & RLS Policies:** Execute [supabase/migrations/001_initial_schema.sql](file:///e:/Projects/Works/Strawberry/supabase/migrations/001_initial_schema.sql) inside the Supabase SQL Editor.
2. **Initialize Years & Semesters:** Execute [supabase/seed.sql](file:///e:/Projects/Works/Strawberry/supabase/seed.sql) to populate academic years (`2nd`, `3rd`, `4th Year`) and semesters (`Semester 3`–`8`). No mock subjects or experiments are seeded.
3. **Provision Faculty Accounts (Critical for RLS):**
   * All database (`subjects`, `experiments`, `experiment_versions`) and `programs` Storage bucket mutations require `TO authenticated`.
   * In the **Supabase Dashboard → Authentication → Providers / Settings**, **disable public user sign-ups** so students cannot register faculty accounts.
   * Create faculty accounts manually under **Authentication → Users → Add User**.

---

## 2. Managing Curriculum in Strawberry Admin

Once signed in via the Admin Login gate:

* **Academic Structure (`Years` & `Semesters`):** View configured degree cohorts and term allocations (Odd/Fall vs. Even/Spring terms).
* **Registering Subjects (`Subjects`):** Click **Add Subject**, enter the course code (e.g., `CS301`), course name, and assign the target semester.
* **Authoring Programs (`Programs` → VS Code Workbench IDE):**
  * Click **Add Program** (or **Write / Edit Code** on an existing program) to open the embedded VS Code–style dark workbench.
  * Select the target subject, enter the program title & filename (or choose quick extensions `.py`, `.c`, `.cpp`, `.java`, `.sql`, `.pl` / starter stubs).
  * Write or paste source code directly in the editor (or import a local file from the Integrity/Import sidebar tab).
  * Press `Ctrl+S` or click **Save & Publish**: the browser calculates the SHA-256 digest via Web Crypto, uploads the source file to Supabase Storage (`programs/<experiment_id>/<filename>`), and commits the version row to `experiment_versions`.
* **Versions & Analytics:** View live SHA-256 hashes, curriculum distribution per course, signed JSON manifest exports, and real-time PostgreSQL latency.

---

## 3. Hosting the Admin Web App on Vercel

1. Ensure your local root `.env` contains `STRAWBERRY_SUPABASE_URL` and `STRAWBERRY_SUPABASE_PUBLISHABLE_KEY`.
2. Double-click or run [deploy-admin-vercel.bat](file:///e:/Projects/Works/Strawberry/deploy-admin-vercel.bat) from the repository root:
   * Validates `npm run build` in `strawberry-admin/`.
   * Links the Vercel project configured via [vercel.json](file:///e:/Projects/Works/Strawberry/vercel.json).
   * Prompts to push **only** public `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY` to Vercel (`STRAWBERRY_SUPABASE_SECRET_KEY` is never sent).
   * Deploys `strawberry-admin` to Vercel production (`vercel deploy --prod`).

---

## 4. Building Workstation Releases (`Strawberry_Setup.exe`)

1. Ensure [Inno Setup 6](https://jrsoftware.org/isinfo.php) is installed (`winget install JRSoftware.InnoSetup`).
2. Run [build-release.bat](file:///e:/Projects/Works/Strawberry/build-release.bat) from the repository root:
   * Runs `uv run pytest -v` inside `strawberry-cli/`.
   * Builds standalone `strawberry-cli/dist/strawberry.exe` via PyInstaller.
   * Stages a temporary gitignored 2-key client `.env` (`STRAWBERRY_SUPABASE_URL` + `STRAWBERRY_SUPABASE_PUBLISHABLE_KEY` only) for bundling into `%LOCALAPPDATA%\Strawberry\.env`, then deletes the staging file after compilation.
   * Outputs `dist/Strawberry_Setup.exe` ready for student distribution.
