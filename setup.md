# Setup

This guide covers local setup and startup for the RSS registry tools and prototype UI.

## Requirements

- Python 3.9+
- A local clone of the repo

## Install

No external packages are required. The scripts use the standard library only.

## Validate and build

```bash
python scripts/validate/validate.py
python scripts/build/build.py
```

Outputs are written to `dist/`.

## Run the prototype UI

```bash
python -m http.server 8000
```

Open `http://localhost:8000/public/index.html`.

## Common tasks

- Add or edit feeds in `data/feeds/`.
- Update categories/tags/locales in `data/`.
- Re-run validate and build after any data changes.
