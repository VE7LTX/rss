# Prototype Quickstart

This prototype relies on generated outputs in `dist/` and a static UI in `public/`.

## Validate Data

```bash
python scripts/validate/validate.py
```

## Build Outputs

```bash
python scripts/build/build.py
```

## View Prototype

```bash
python -m http.server 8000
```

Open `http://localhost:8000/public/index.html`.

## Notes

- The "Live Updates" panel uses demo items generated during the build step.
- Feed selections persist in local storage.
- Re-run the build step after changing `data/`.
