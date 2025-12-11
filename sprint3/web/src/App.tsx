import { useMemo } from "react";
import { CountriesTable } from "./components/CountriesTable";
import { Filters } from "./components/Filters";
import { StatusMessage } from "./components/StatusMessage";
import { TopCountriesChart } from "./components/TopCountriesChart";
import { TrendsLineChart } from "./components/TrendsLineChart";
import { useDashboardData } from "./hooks/useDashboardData";
import { DashboardFilters } from "./types";

const initialFilters: DashboardFilters = { region: "All" };

const formatBillions = (value: number) =>
  value.toLocaleString(undefined, {
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
  });

function App() {
  const { data, loading, error, filters, setFilters, refresh } =
    useDashboardData(initialFilters, 5);

  const totalBillions = useMemo(
    () =>
      data?.tableRows.reduce(
        (acc, row) => acc + row.receiptsUsdBillions,
        0
      ) ?? 0,
    [data]
  );

  const topCountry = data?.topCountries[0];

  return (
    <div className="app">
      <div className="shell">
        <header className="page-header">
          <div>
            <p className="eyebrow">Module 3 · Web App</p>
            <h1>Tourism receipts dashboard</h1>
            <p className="muted">
              Latest tourism receipts, pulled from MongoDB (Module 2) or the
              bundled mock data. Adjust the filters to explore regions and
              years.
            </p>
          </div>
          <div className="badge">
            Source: {data?.source ?? "loading"}
          </div>
        </header>

        <Filters
          years={data?.years ?? []}
          regions={data?.regions ?? ["All"]}
          filters={filters}
          onChange={setFilters}
          onRefresh={refresh}
        />

        {loading && (
          <StatusMessage
            title="Loading dashboard…"
            detail="Fetching receipts, totals, and top earners."
          />
        )}
        {error && !loading && (
          <StatusMessage title="Heads up" detail={error} variant="error" />
        )}

        {data && !loading && (
          <>
            <div className="stats-grid">
              <div className="panel stat">
                <p className="label">Active year</p>
                <h2>{data.year}</h2>
                <p className="muted">Latest available: {data.latestYear}</p>
              </div>
              <div className="panel stat">
                <p className="label">Total receipts (USD billions)</p>
                <h2>{formatBillions(totalBillions)}</h2>
                <p className="muted">{filters.region}</p>
              </div>
              <div className="panel stat">
                <p className="label">Top country</p>
                <h2>{topCountry?.country ?? "—"}</h2>
                <p className="muted">
                  {topCountry
                    ? `${formatBillions(topCountry.receiptsUsdBillions)} B`
                    : "No data for this selection"}
                </p>
              </div>
            </div>

            <div className="charts-grid">
              <TopCountriesChart
                data={data.topCountries}
                year={data.year}
                region={filters.region}
              />
              <TrendsLineChart data={data.totalsByYear} region={filters.region} />
            </div>

            <CountriesTable rows={data.tableRows} />
          </>
        )}
      </div>
    </div>
  );
}

export default App;
