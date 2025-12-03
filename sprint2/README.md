## Sprint 2 mini run (sprint2)

MongoDB step for the tourism receipts project. It reuses the Sprint 1 CSVs in
`../data/` (`travel_items.csv`, `metadata_country.csv`), upserts every country/year
into MongoDB Atlas (or local), builds indexes, and prints quick summaries.

### Source
World Bank tourism receipts: https://data.worldbank.org/indicator/ST.INT.TVLR.CD

### What you get
- `countries` collection: `{ code, name, region, income_group, table_name }` with a unique index on `code`.
- `receipts` collection: `{ code, country, region, year, receipts_usd, receipts_usd_billions }` with indexes on `(code, year)`, `year`, and `region`.
- Console output after loading: upsert counts plus the latest-year top five earners.
- `query_examples.py` to print the latest-year top five and global totals by year.

### Prerequisites
- Python 3.10+
- Sprint 1 outputs present in `../data/` (run `sprint1/main.py` if they are missing).
- MongoDB URI in `.env` as `MONGODB_URI` (Atlas or local works).

### Environment file (.env)
```bash
MONGODB_URI="mongodb+srv://<user>:<pass>@<cluster>/tourism?retryWrites=true&w=majority"
# Optional overrides (defaults shown)
DB_NAME=tourism
COUNTRIES_COLLECTION=countries
RECEIPTS_COLLECTION=receipts
```
For local Mongo, use `mongodb://localhost:27017/tourism` as `MONGODB_URI`.

### How to run it
```bash
cd sprint1/sprint2
python3 -m venv .venv
source .venv/bin/activate      
pip install -r requirements.txt
python load_data.py                     # full load
python load_data.py --limit 500         # limited load
python load_data.py --env-file my.env   # use a non-default env file
python load_data.py --reset-collections # drop target collections before loading
```
Terminal output will show counts written and the latest-year top five.

Fresh demo / clean slate:
- `--reset-collections` drops `countries` and `receipts` in the target DB, then recreates indexes and loads data. Use this before filming a first-time load.

Expected counts from a full load of the provided CSVs:
- Countries upserted: 217
- Receipts rows upserted: 4,549
- Latest year with data: 2020 (rows: 158)

### Quick verification scripts
```bash
python query_examples.py
```
Prints the latest-year top five and the global totals (USD billions) by year.

### Check in Mongo
- In Atlas/Compass, confirm `countries` and `receipts` exist with the indexes above.
- Default database/collections: `tourism.countries` and `tourism.receipts` (unless overridden in `.env`).
- Run sample queries:
  - Latest top five: `{ year: <latest_year> }` sorted by `receipts_usd` desc.
  - Global totals by year: `db.receipts.aggregate([{ $group: { _id: "$year", total: { $sum: "$receipts_usd_billions" } } }, { $sort: { _id: 1 } }])`
