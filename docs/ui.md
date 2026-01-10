# Browser UI Prototype

This folder contains a minimal static prototype for browsing the feed registry.

## Location

`web/`

## Files

- `web/index.html` — layout and DOM placeholders
- `web/styles.css` — basic styling
- `web/app.js` — fetches `dist/feeds.json`, applies filters, and manages My Feeds

## Running Locally

1. Generate exports:
   ```bash
   python scripts/build/generate_outputs.py
   ```
2. Serve the repo root with a local web server so `dist/feeds.json` is accessible.
   ```bash
   python -m http.server 8000
   ```
3. Open `http://localhost:8000/web/` in a browser.

If you see “Unable to load feeds.json,” confirm the build script ran and that you are
serving the repo root (not the `web/` folder directly).

## Notes

- The UI limits results to 25 entries to keep browsing manageable.
- Filters include category, tag, region, source type, and search.
- My Feeds selections are saved in local storage.
- Refresh uses a public CORS-friendly proxy (`api.allorigins.win`) to fetch feed items;
  some feeds may block requests or fail to parse in the browser.
- This is intentionally static and can be replaced later with a richer UI.
