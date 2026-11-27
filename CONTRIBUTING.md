# Contributing to Strawberry 🍓

Thanks for contributing! This repository contains a Windows Python CLI/TUI client, a React + TypeScript faculty admin portal, Supabase SQL definitions, and an Inno Setup installer script.

## Repository Layout

- `strawberry-cli/` — Standalone Windows CLI (`Lite`) and Textual TUI (`Pro`) managed with `uv`
- `strawberry-admin/` — React + TypeScript + Vite faculty workbench deployed on Vercel
- `supabase/` — PostgreSQL schema migrations (`001_initial_schema.sql`) and academic year/semester seed SQL
- `installer/` & `build-release.bat` — Inno Setup packaging script for `Strawberry_Setup.exe`
- `docs/` — Architecture, installation, and admin guides

## Local Development Checks

### CLI (`strawberry-cli/`)
```bash
cd strawberry-cli
uv sync
uv run pytest -v
```

### Admin Portal (`strawberry-admin/`)
```bash
cd strawberry-admin
npm ci
npm run lint
npm run build
```

## Security Hygiene

- Never commit `.env`, `.env.local`, `installer/.env.student`, or any `STRAWBERRY_SUPABASE_SECRET_KEY`.
- Client distributions (`Strawberry_Setup.exe` and `strawberry-admin` frontend builds) must only receive `STRAWBERRY_SUPABASE_URL` / `VITE_SUPABASE_URL` and the public `PUBLISHABLE_KEY`.
