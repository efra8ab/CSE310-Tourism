## Tourism Dashboard API (Module 3)

FastAPI wrapper over the MongoDB data produced in Module 2 (`countries` and
`receipts` collections). It returns a single dashboard payload that the React
frontend consumes. 

### Endpoints
- `GET /health` – ping + latest year (from Mongo).
- `GET /dashboard?year=<int>&region=<str>&limit=<int>` – returns:
  - `latest_year`, available `years`, `regions`
  - `top_countries` (Top-N for the selected year/region)
  - `totals_by_year` (global or region-filtered totals in USD billions)
  - `table_rows` (sorted receipts rows for the selected year/region)

### Setup
```bash
cd sprint1/sprint3/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run
```bash
uvicorn main:app --reload --port 8000

### Notes
- The Mongo collections and field names match Module 2 (`receipts_usd`,
  `receipts_usd_billions`, `year`, `region`, `country`, `code`).
- If no `MONGODB_URI` is set, the service automatically falls back to the
  sample payload in `mock_data/dashboard_sample.json`.
- The `/dashboard` response is capped to 50 top countries per request to keep
  payloads predictable for the frontend table.
