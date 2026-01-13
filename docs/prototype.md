# The RSS Encyclopedia Quickstart

Purpose: Run the static UI for The RSS Encyclopedia using outputs from `dist/`.

## Validate data

```bash
python scripts/validate/validate.py
```

## Build outputs

```bash
python scripts/build/build.py
```

## View prototype

```bash
python scripts/server/server.py
```

Open `http://localhost:8000/public/index.html`.

Static-only demo:

```bash
python -m http.server 8000
```

## Notes

- The "Live Updates" panel pulls live feed entries when the local server is running.
- If the server is not running, the UI falls back to demo items from `dist/items.json`.
- Feed selections persist in local storage.
- Re-run the build step after changing `data/`.
