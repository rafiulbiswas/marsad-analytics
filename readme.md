# MARSAD Analytics

MARSAD Analytics is a browser-based dashboard for exploring and analyzing social and media datasets. It is designed to work mostly offline in the browser, using a local Python runtime via Pyodide and a static HTML/JavaScript interface.

The project lets users load their own datasets, compare files, and explore structured analytical views such as timeline trends, word frequency, framing, reactions, topics, and more.

## Highlights

- Upload and analyze local datasets in common formats such as CSV, TSV, TXT, XLSX/XLS, and JSONL
- Run analyses directly in the browser with no server-side setup required
- Compare multiple datasets or combine them for side-by-side analysis
- Built-in sample datasets for quick testing
- Arabic and English interface support
- Help center and documentation bundled with the app
- Fully static front-end deployment friendly

## What this repository contains

- `index.html` — main application shell and UI
- `help.js` — UI logic, analysis orchestration, and help behavior
- `help.css` — styling for the dashboard and help center
- `plotly.min.js` — charting library
- `pyodide/` — Pyodide runtime assets
- `docs/` — documentation, registry metadata, and analysis definitions
- `samples/` — sample datasets used to demonstrate the app
- `*.wasm` files — packaged Python/runtime assets used by the browser

## Project structure

```text
marsad-analytics/
├── index.html
├── help.js
├── help.css
├── plotly.min.js
├── docs.html
├── docs.json
├── bundle_py.zip.wasm
├── marsad.zip.wasm
├── wordfreq_data.zip.wasm
├── pyodide/
├── docs/
├── samples/
└── README.md
