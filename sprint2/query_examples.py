"""
Simple query runner for Sprint 2.

Prints:
- Latest-year top 5 earners
- Global totals (USD billions) by year
"""

import os

from dotenv import load_dotenv
from pymongo import MongoClient


def main():
    load_dotenv(".env")
    mongo_uri = os.environ["MONGODB_URI"]
    db_name = os.getenv("DB_NAME", "tourism")
    receipts_name = os.getenv("RECEIPTS_COLLECTION", "receipts")

    client = MongoClient(mongo_uri)
    receipts = client[db_name][receipts_name]

    latest = receipts.find_one(sort=[("year", -1)])
    if not latest:
        raise SystemExit("No receipts found. Load data first with load_data.py.")
    latest_year = latest["year"]

    print(f"Top 5 for {latest_year}:")
    top5 = receipts.find({"year": latest_year}).sort("receipts_usd", -1).limit(5)
    for doc in top5:
        print(f"- {doc['country']} ({doc['code']}): {doc['receipts_usd_billions']} USD billions")

    print("\nGlobal totals (billions) by year:")
    pipeline = [
        {"$group": {"_id": "$year", "total_usd": {"$sum": "$receipts_usd"}}},
        {"$addFields": {"total_billions": {"$round": [{"$divide": ["$total_usd", 1e9]}, 2]}}},
        {"$sort": {"_id": 1}},
    ]
    for row in receipts.aggregate(pipeline):
        print(f"{row['_id']}: {row['total_billions']}")


if __name__ == "__main__":
    main()
