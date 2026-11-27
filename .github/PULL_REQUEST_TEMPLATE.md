## Summary
<!-- Briefly describe what this PR changes and why. -->

## Components Touched
- [ ] `strawberry-cli/` (Python CLI / TUI / Daemon)
- [ ] `strawberry-admin/` (React / TypeScript / Vite)
- [ ] `installer/` (Inno Setup / Release packaging)
- [ ] `supabase/` (Migrations / Seeds)
- [ ] `docs/` / `README.md`

## Verification
- [ ] `cd strawberry-cli && uv run pytest -v` passes
- [ ] `cd strawberry-admin && npm run lint && npm run build` passes
- [ ] No real secrets (`STRAWBERRY_SUPABASE_SECRET_KEY`, `.env`) are included
