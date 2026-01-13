# The RSS Encyclopedia Quickstart

## Document header

- Purpose: Run the prototype UI and understand its live updates behavior.
- Audience: Developers and reviewers validating the UI.
- Scope: Validation/build prerequisites, local server, and live updates API.
- Last updated: 2026-01-13.

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
- Live updates are cached in `cache/updates.json` for 10 minutes.
- Use the Refresh button to force a re-fetch (`force=1` on the API).

## Live updates API

- Endpoint: `/api/updates?ids=feed-a,feed-b&limit=30`
- Returns JSON with `updates` and `feeds` metadata.
- Limits: 10 items per feed and 30 total items per response.
