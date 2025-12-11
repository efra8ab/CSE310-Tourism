export type DataSource = "mongo" | "mock" | "mock-local";

export interface CountryRow {
  country: string;
  code: string;
  region: string;
  year: number;
  receiptsUsd: number;
  receiptsUsdBillions: number;
}

export interface YearTotal {
  year: number;
  totalUsdBillions: number;
  region?: string | null;
}

export interface DashboardData {
  source: DataSource;
  latestYear: number;
  year: number;
  years: number[];
  regions: string[];
  topCountries: CountryRow[];
  totalsByYear: YearTotal[];
  tableRows: CountryRow[];
}

export interface DashboardFilters {
  year?: number;
  region: string;
}

export interface DashboardApiResponse {
  source: DataSource;
  latest_year: number;
  year: number;
  years: number[];
  regions: string[];
  top_countries: Array<{
    country: string;
    code: string;
    region: string;
    year: number;
    receipts_usd: number;
    receipts_usd_billions: number;
  }>;
  totals_by_year: Array<{
    year: number;
    total_usd_billions: number;
    region?: string | null;
  }>;
  table_rows: DashboardApiResponse["top_countries"];
}
