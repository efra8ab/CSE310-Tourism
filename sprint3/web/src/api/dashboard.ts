import mockDashboard from "../mocks/dashboard_sample.json";
import {
  CountryRow,
  DashboardApiResponse,
  DashboardData,
  DashboardFilters,
  YearTotal,
} from "../types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

const toCountryRow = (row: {
  country: string;
  code: string;
  region: string;
  year: number;
  receipts_usd: number;
  receipts_usd_billions: number;
}): CountryRow => ({
  country: row.country,
  code: row.code,
  region: row.region,
  year: row.year,
  receiptsUsd: row.receipts_usd,
  receiptsUsdBillions: row.receipts_usd_billions,
});

const toYearTotal = (row: {
  year: number;
  total_usd_billions: number;
  region?: string | null;
}): YearTotal => ({
  year: row.year,
  totalUsdBillions: row.total_usd_billions,
  region: row.region,
});

const toMockCountryRow = (row: {
  country: string;
  code: string;
  region: string;
  year: number;
  receiptsUsd: number;
  receiptsUsdBillions: number;
}): CountryRow => ({
  country: row.country,
  code: row.code,
  region: row.region,
  year: row.year,
  receiptsUsd: row.receiptsUsd,
  receiptsUsdBillions: row.receiptsUsdBillions ?? row.receiptsUsd / 1e9,
});

const toMockTotal = (row: {
  year: number;
  totalUsdBillions: number;
  region?: string;
}): YearTotal => ({
  year: row.year,
  totalUsdBillions: row.totalUsdBillions,
  region: row.region,
});

const normalizeDashboard = (payload: DashboardApiResponse): DashboardData => ({
  source: payload.source,
  latestYear: payload.latest_year,
  year: payload.year,
  years: payload.years,
  regions: payload.regions,
  topCountries: payload.top_countries.map(toCountryRow),
  totalsByYear: payload.totals_by_year.map(toYearTotal),
  tableRows: payload.table_rows.map(toCountryRow),
});

export const buildMockDashboard = (
  filters: DashboardFilters,
  limit = 5
): DashboardData => {
  const targetYear = filters.year ?? mockDashboard.latestYear;
  const region = filters.region ?? "All";
  const tableRows = mockDashboard.tableRows
    .filter(
      (row) =>
        row.year === targetYear && (region === "All" || row.region === region)
    )
    .map(toMockCountryRow);

  const topCountries = [...tableRows]
    .sort((a, b) => b.receiptsUsd - a.receiptsUsd)
    .slice(0, limit);

  const regionTotals =
    region === "All"
      ? mockDashboard.totalsByYear
      : (mockDashboard.regionTotals || []).filter(
          (row) => row.region === region
        );

  const totalsByYear =
    regionTotals.length > 0
      ? regionTotals.map(toMockTotal)
      : mockDashboard.totalsByYear.map(toMockTotal);

  return {
    source: "mock-local",
    latestYear: mockDashboard.latestYear,
    year: targetYear,
    years: mockDashboard.years,
    regions: mockDashboard.regions,
    topCountries,
    totalsByYear,
    tableRows,
  };
};

export async function fetchDashboard(
  filters: DashboardFilters,
  limit = 5
): Promise<DashboardData> {
  if (USE_MOCK) {
    return buildMockDashboard(filters, limit);
  }

  const params = new URLSearchParams();
  if (filters.year) params.set("year", String(filters.year));
  if (filters.region) params.set("region", filters.region);
  params.set("limit", String(limit));

  const response = await fetch(`${API_URL}/dashboard?${params.toString()}`);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(
      `API error ${response.status}${detail ? `: ${detail}` : ""}`
    );
  }

  const payload = (await response.json()) as DashboardApiResponse;
  return normalizeDashboard(payload);
}
