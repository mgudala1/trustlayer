# Architecture Overview

## Plugin Components
- **overlay.js**: Injects trust badge and overlay on supported product pages, handles product detection and data matching.
- **popup.js**: Renders the extension popup UI, showing trust scores and pros/cons for the current product.
- **summarize.py**: (External) Summarizes product feedback from sources like Reddit/YouTube.
- **match_api.py**: (External/optional) API for serving trust data to the extension or other clients.

## Data Flow
```
scrape → summarize → validate → JSON → load in extension / serve via API
```
- Data is scraped and summarized externally, validated, and stored as JSON.
- The extension loads this JSON for product matching and display.
- Optionally, an API can serve the same data for dynamic updates.
