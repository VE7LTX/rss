# Setup

## Document header

- Purpose: Provide setup, startup, and operational guidance for the registry tooling and UI.
- Audience: Local developers and curators running the pipeline or prototype.
- Scope: Validation, build outputs, live updates server, and common workflows.
- Last updated: 2026-01-13.

## Requirements

- Python 3.9+
- A local clone of the repo

## Install

No external packages are required. The scripts use the standard library only.

Optional: `pytest` is used for the test suite.

## Validate and build

```bash
python scripts/validate/validate.py
python scripts/build/build.py
```

Outputs are written to `dist/`.

## Run the prototype UI

```bash
python scripts/server/server.py
```

Open `http://localhost:8000/public/index.html`.

Static-only demo:

```bash
python -m http.server 8000
```

Note: the live updates panel only works when the local server is running.

## Run tests

```bash
python -m pytest
```

## Health checks

```bash
python scripts/validate/validate.py --health --health-timeout 20
```

Use `--offset` and `--limit` to run in batches.

## Seed feeds

```bash
python scripts/tools/seed_feeds.py --verify --write
```

Use `--offset` and `--limit` to run in batches if needed.

## Common tasks

- Add or edit feeds in `data/feeds/`.
- Update categories/tags/locales in `data/`.
- Re-run validation, build, and tests after data changes.
- Clear `cache/updates.json` if you want to reset live updates.
