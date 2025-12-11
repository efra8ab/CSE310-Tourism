"""
FastAPI wrapper over the MongoDB tourism receipts data (Module 2).

It returns a single dashboard payload with:
- latest year
- available years/regions
- top-N countries for the selected year/region
- totals by year (optionally filtered by region)
- table rows for the selected year/region (sorted by receipts)

Set `USE_MOCK_DATA=true` to serve the local sample JSON without Mongo.
"""
from __future__ import annotations

import json
import os
import pathlib
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel, Field


load_dotenv()

BASE_DIR = pathlib.Path(__file__).parent
MOCK_FILE = BASE_DIR / "mock_data" / "dashboard_sample.json"

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "tourism")
COUNTRIES_COLLECTION = os.getenv("COUNTRIES_COLLECTION", "countries")
RECEIPTS_COLLECTION = os.getenv("RECEIPTS_COLLECTION", "receipts")

USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "").lower() == "true" or not MONGODB_URI
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]


class CountryRow(BaseModel):
    country: str
    code: str
    region: str
    year: int
    receipts_usd: float = Field(..., description="Raw receipts in USD")
    receipts_usd_billions: float = Field(..., description="Receipts in USD billions")


class YearTotal(BaseModel):
    year: int
    total_usd_billions: float
    region: Optional[str] = None


class DashboardResponse(BaseModel):
    source: str
    latest_year: int
    year: int
    years: List[int]
    regions: List[str]
    top_countries: List[CountryRow]
    totals_by_year: List[YearTotal]
    table_rows: List[CountryRow]


def create_db_client() -> Optional[AsyncIOMotorClient]:
    if USE_MOCK_DATA:
        return None
    if not MONGODB_URI:
        raise RuntimeError("MONGODB_URI is required unless USE_MOCK_DATA=true.")
    return AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)


app = FastAPI(title="Tourism Dashboard API", version="0.1.0")

if ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


async def get_db() -> Optional[AsyncIOMotorDatabase]:
    client = create_db_client()
    return client[DB_NAME] if client else None


def load_mock_payload() -> Dict[str, Any]:
    with MOCK_FILE.open() as f:
        return json.load(f)


async def ensure_connected(db: Optional[AsyncIOMotorDatabase]) -> None:
    if USE_MOCK_DATA:
        return
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not configured. Set MONGODB_URI or USE_MOCK_DATA=true.",
        )
    try:
        await db.command("ping")
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unreachable: {exc}",
        ) from exc


def to_country_row(doc: Dict[str, Any]) -> CountryRow:
    receipts_usd = float(doc.get("receipts_usd") or 0)
    receipts_usd_billions = (
        float(doc.get("receipts_usd_billions"))
        if doc.get("receipts_usd_billions") is not None
        else receipts_usd / 1e9
    )
    return CountryRow(
        country=doc.get("country") or doc.get("name") or "",
        code=doc.get("code") or "",
        region=doc.get("region") or "",
        year=int(doc.get("year")),
        receipts_usd=receipts_usd,
        receipts_usd_billions=receipts_usd_billions,
    )


@app.get("/health")
async def health(db: Optional[AsyncIOMotorDatabase] = Depends(get_db)):
    if USE_MOCK_DATA:
        return {"status": "ok", "source": "mock"}
    await ensure_connected(db)
    latest_year = await db[RECEIPTS_COLLECTION].find_one(
        {}, sort=[("year", -1)], projection={"year": 1}
    )
    return {
        "status": "ok",
        "source": "mongo",
        "latest_year": latest_year.get("year") if latest_year else None,
    }


@app.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    year: Optional[int] = Query(None, description="Target year for the dashboard."),
    region: str = Query("All", description="Region filter; defaults to all regions."),
    limit: int = Query(5, ge=1, le=50, description="Top-N countries to return."),
    db: Optional[AsyncIOMotorDatabase] = Depends(get_db),
):
    if USE_MOCK_DATA:
        payload = load_mock_payload()
        target_year = year or payload["latestYear"]

        def parse_row(raw: Dict[str, Any]) -> CountryRow:
            return CountryRow(
                country=raw["country"],
                code=raw["code"],
                region=raw["region"],
                year=int(raw["year"]),
                receipts_usd=float(raw["receiptsUsd"]),
                receipts_usd_billions=float(
                    raw.get("receiptsUsdBillions")
                    or float(raw["receiptsUsd"]) / 1e9
                ),
            )

        table_rows = [
            parse_row(row)
            for row in payload["tableRows"]
            if int(row["year"]) == target_year and (region == "All" or row["region"] == region)
        ]
        top_rows = sorted(
            table_rows, key=lambda r: r.receipts_usd, reverse=True
        )[:limit]

        totals_source = payload.get("regionTotals") if region != "All" else None
        totals_raw = (
            [t for t in totals_source or [] if t["region"] == region]
            if totals_source
            else payload["totalsByYear"]
        )
        totals_by_year = [
            YearTotal(
                year=int(row["year"]),
                total_usd_billions=float(row["totalUsdBillions"]),
                region=row.get("region"),
            )
            for row in totals_raw
        ]

        return DashboardResponse(
            source="mock",
            latest_year=payload["latestYear"],
            year=target_year,
            years=payload["years"],
            regions=payload["regions"],
            top_countries=top_rows,
            totals_by_year=totals_by_year,
            table_rows=table_rows,
        )

    await ensure_connected(db)
    receipts = db[RECEIPTS_COLLECTION]

    years = sorted(await receipts.distinct("year"))
    if not years:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No receipt data found. Load data with sprint1/sprint2/load_data.py.",
        )
    latest_year = years[-1]
    target_year = year or latest_year
    if target_year not in years:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Year {target_year} not found in data (available: {years}).",
        )

    regions = ["All"] + sorted(await receipts.distinct("region"))
    region_filter: Dict[str, Any] = {"year": target_year}
    totals_filter: Dict[str, Any] = {}
    if region != "All":
        region_filter["region"] = region
        totals_filter["region"] = region

    top_cursor = (
        receipts.find(region_filter, {"_id": 0})
        .sort("receipts_usd", -1)
        .limit(limit)
    )
    top_countries = [to_country_row(doc) async for doc in top_cursor]

    totals_pipeline = [
        {"$match": totals_filter} if totals_filter else {"$match": {}},
        {
            "$group": {
                "_id": "$year",
                "total_usd_billions": {"$sum": "$receipts_usd_billions"},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    totals_cursor = receipts.aggregate(totals_pipeline)
    totals_by_year = [
        YearTotal(year=doc["_id"], total_usd_billions=round(doc["total_usd_billions"], 2))
        async for doc in totals_cursor
    ]

    table_cursor = (
        receipts.find(region_filter, {"_id": 0})
        .sort("receipts_usd", -1)
        .limit(500)
    )
    table_rows = [to_country_row(doc) async for doc in table_cursor]

    return DashboardResponse(
        source="mongo",
        latest_year=latest_year,
        year=target_year,
        years=years,
        regions=regions,
        top_countries=top_countries,
        totals_by_year=totals_by_year,
        table_rows=table_rows,
    )


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
