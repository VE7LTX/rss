# Setup

Purpose: Provide local setup and startup instructions for the registry tools and prototype UI.

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

## Run tests

```bash
python -m unittest discover -s tests
```

## Common tasks

- Add or edit feeds in `data/feeds/`.
- Update categories/tags/locales in `data/`.
- Re-run validation, build, and tests after data changes.
