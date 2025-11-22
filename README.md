## Sprint 1 mini run (sprint1)

This is my small copy of the Sprint 1 pipeline. The World Bank CSV plus the
country metadata already live in `data/`, so `main.py` just loads them,
filters out aggregates, and prints the intermediate steps while it works.
It ends with the same two summaries we promised for Sprint 1.

### Source
https://data.worldbank.org/indicator/ST.INT.TVLR.CD?view=map&year=1995

### What you get
- `outputs/top_countries_<latest_year>.csv` → the top five earners for the most
  recent year that has numbers.
- `outputs/global_receipts_recent_years.csv` → world totals for the last five
  years with data (all countries, not just the top five).
- `outputs/top_countries_<latest_year>.png` → bar chart of the top five (USD billions).
- `outputs/global_receipts_recent_years.png` → line chart of world totals for the last five years.

### How to run it
```bash
cd sprint1
python3 -m venv .venv          # optional but keeps packages separate
source .venv/bin/activate      # skip on Windows
pip install -r requirements.txt
python3 main.py
```

You’ll see the step-by-step log in the terminal, and fresh CSVs will land in
`outputs/` when the script finishes.
