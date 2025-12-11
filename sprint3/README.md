## Module 3 – Web App

A React + TypeScript dashboard that visualizes the tourism receipts data from
Module 2. The backend is a small FastAPI service that reads MongoDB (or serves a
local mock payload) and returns a single `/dashboard` response with top earners,
totals by year, and table rows for the selected filters.

### Layout
- `api/` – FastAPI service exposing `/health` and `/dashboard`.
- `web/` – Vite + React + TS dashboard (Chart.js via `react-chartjs-2`), mock
  data fallback baked in.

### Backend (api/)
```bash
cd sprint1/sprint3/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Mongo-backed
MONGODB_URI="mongodb+srv://..." uvicorn main:app --reload --port 8000
# Mock-only (no Mongo needed)
USE_MOCK_DATA=true uvicorn main:app --reload --port 8000
```
Environment keys: `MONGODB_URI` (or `USE_MOCK_DATA=true`), `DB_NAME`, `COUNTRIES_COLLECTION`,
`RECEIPTS_COLLECTION`, `ALLOWED_ORIGINS`.

### Frontend (web/)
```bash
cd sprint1/sprint3/web
cp .env.example .env    # point VITE_API_URL at the FastAPI host/port
npm install
npm run dev             # http://localhost:5173
npm run build && npm run preview  # prod build + preview
```
The dashboard automatically falls back to the bundled mock JSON if the API
is unreachable or if `VITE_USE_MOCK=true`.

### What the UI shows
- Filters: year selector (latest default) and region selector (All + Mongo
  distinct regions).
- Charts: Top-N bar for the active year/region; multi-year line of totals.
- Table: Sortable receipts table for the active filters with CSV export.
- States: Loading indicator, error banner, and mock-data notice via the source
  badge.

### Expected data shape
The `/dashboard` response mirrors the models in `api/main.py`:
```json
{
  "source": "mongo",
  "latest_year": 2020,
  "year": 2020,
  "years": [2016, 2017, 2018, 2019, 2020],
  "regions": ["All", "Europe & Central Asia", "..."],
  "top_countries": [{ "country": "United States", "code": "USA", "receipts_usd_billions": 72.81, ... }],
  "totals_by_year": [{ "year": 2019, "total_usd_billions": 1392.18 }],
  "table_rows": [{ "country": "...", "year": 2020, "receipts_usd": 72812000000.0, ... }]
}
```
If you use the Module 2 loader defaults, the fields already match.
