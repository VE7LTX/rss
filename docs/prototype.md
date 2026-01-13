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
python -m http.server 8000
```

Open `http://localhost:8000/public/index.html`.

## Notes

- The "Live Updates" panel uses demo items generated during the build step.
- Feed selections persist in local storage.
- Re-run the build step after changing `data/`.
