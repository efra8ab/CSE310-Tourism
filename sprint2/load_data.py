"""
Load tourism receipts data from Sprint 1 into MongoDB.

Default locations assume:
- This script lives in sprint2/
- Sprint 1 raw data lives in ../sprint1/data/

It creates/updates two collections:
- countries: one document per real country with region/income metadata
- receipts: one document per country-year with USD totals (and billions helper)
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Tuple

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
from pymongo.collection import Collection


def load_sources(base_dir: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load the raw World Bank CSV and the country metadata CSV."""
    # sprint2 now lives inside sprint1/, so data is one level up in ../data
    sprint1_data = base_dir.parent / "data"
    travel_path = sprint1_data / "travel_items.csv"
    metadata_path = sprint1_data / "metadata_country.csv"

    if not travel_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(
            f"Expected sprint1 data at {travel_path} and {metadata_path}. "
            "Generate or copy them (run sprint1/main.py if needed) before loading."
        )

    raw_df = pd.read_csv(travel_path, skiprows=4, encoding="utf-8-sig")
    meta_df = pd.read_csv(metadata_path, encoding="utf-8-sig")
    return raw_df, meta_df


def clean_data(raw_df: pd.DataFrame, meta_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return (countries_df, receipts_df) ready for Mongo inserts."""
    meta_cols = ["Country Code", "Region", "IncomeGroup", "TableName"]
    meta_df = meta_df[meta_cols]

    combined_df = raw_df.merge(meta_df, on="Country Code", how="left")
    combined_df = combined_df[combined_df["Region"].notna()].copy()

    year_cols = [col for col in combined_df.columns if str(col).isdigit()]
    combined_df[year_cols] = combined_df[year_cols].apply(pd.to_numeric, errors="coerce")

    countries_df = (
        combined_df[["Country Code", "Country Name", "Region", "IncomeGroup", "TableName"]]
        .drop_duplicates()
        .rename(
            columns={
                "Country Code": "code",
                "Country Name": "name",
                "Region": "region",
                "IncomeGroup": "income_group",
                "TableName": "table_name",
            }
        )
    )

    receipts_df = (
        combined_df.melt(
            id_vars=["Country Name", "Country Code", "Region"],
            value_vars=year_cols,
            var_name="year",
            value_name="receipts_usd",
        )
        .dropna(subset=["receipts_usd"])
        .rename(
            columns={
                "Country Name": "country",
                "Country Code": "code",
                "Region": "region",
            }
        )
    )
    receipts_df["year"] = receipts_df["year"].astype(int)
    receipts_df["receipts_usd"] = receipts_df["receipts_usd"].astype(float)
    receipts_df["receipts_usd_billions"] = (receipts_df["receipts_usd"] / 1e9).round(2)

    return countries_df, receipts_df


def upsert_countries(collection: Collection, countries_df: pd.DataFrame) -> int:
    requests = []
    for country in countries_df.to_dict(orient="records"):
        requests.append(
            UpdateOne(
                {"code": country["code"]},
                {"$set": country},
                upsert=True,
            )
        )
    if requests:
        result = collection.bulk_write(requests, ordered=False)
        return result.upserted_count + result.modified_count
    return 0


def upsert_receipts(collection: Collection, receipts_df: pd.DataFrame, batch_size: int = 2000) -> int:
    total_written = 0
    for start in range(0, len(receipts_df), batch_size):
        chunk = receipts_df.iloc[start : start + batch_size]
        requests = []
        for row in chunk.to_dict(orient="records"):
            requests.append(
                UpdateOne(
                    {"code": row["code"], "year": row["year"]},
                    {"$set": row},
                    upsert=True,
                )
            )
        if requests:
            result = collection.bulk_write(requests, ordered=False)
            total_written += result.upserted_count + result.modified_count
    return total_written


def get_collections(client: MongoClient):
    db_name = os.getenv("DB_NAME", "tourism")
    countries_name = os.getenv("COUNTRIES_COLLECTION", "countries")
    receipts_name = os.getenv("RECEIPTS_COLLECTION", "receipts")

    db = client[db_name]
    return db[countries_name], db[receipts_name]


def main():
    parser = argparse.ArgumentParser(description="Load tourism receipts into MongoDB.")
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to .env file with MONGODB_URI and DB_NAME (default: .env)",
    )
    parser.add_argument(
        "--reset-collections",
        action="store_true",
        help="Drop the target collections before loading (useful for first-time demos).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Optional cap on number of receipts rows to load (for quick tests).",
    )
    args = parser.parse_args()

    load_dotenv(args.env_file)

    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise ValueError("Set MONGODB_URI in .env or environment.")

    base_dir = Path(__file__).parent
    raw_df, meta_df = load_sources(base_dir)
    countries_df, receipts_df = clean_data(raw_df, meta_df)

    if args.limit:
        receipts_df = receipts_df.iloc[: args.limit]

    client = MongoClient(mongo_uri)
    countries_col, receipts_col = get_collections(client)

    if args.reset_collections:
        db = countries_col.database
        db.drop_collection(countries_col.name)
        db.drop_collection(receipts_col.name)
        print(f"Dropped {db.name}.{countries_col.name} and {db.name}.{receipts_col.name}")
        countries_col = db[countries_col.name]
        receipts_col = db[receipts_col.name]

    countries_col.create_index("code", unique=True)
    receipts_col.create_index([("code", 1), ("year", 1)], unique=True)
    receipts_col.create_index("year")
    receipts_col.create_index("region")

    countries_written = upsert_countries(countries_col, countries_df)
    receipts_written = upsert_receipts(receipts_col, receipts_df)

    print(f"Countries upserted/updated: {countries_written}")
    print(f"Receipts upserted/updated: {receipts_written}")

    sample = receipts_col.find_one(sort=[("year", -1), ("receipts_usd", -1)])
    if sample:
        latest_year = sample["year"]
        top = receipts_col.find({"year": latest_year}).sort("receipts_usd", -1).limit(5)
        print(f"\nTop 5 earners for {latest_year}:")
        for doc in top:
            billions = doc.get("receipts_usd_billions")
            print(f"- {doc['country']} ({doc['code']}): {billions} USD billions")


if __name__ == "__main__":
    main()
