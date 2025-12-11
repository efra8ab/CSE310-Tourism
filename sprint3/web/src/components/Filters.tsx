import { DashboardFilters } from "../types";

type Props = {
  years: number[];
  regions: string[];
  filters: DashboardFilters;
  onChange: (next: DashboardFilters) => void;
  onRefresh?: () => void;
};

export const Filters = ({
  years,
  regions,
  filters,
  onChange,
  onRefresh,
}: Props) => {
  const handleYearChange = (value: string) => {
    const yearValue = value ? Number(value) : undefined;
    onChange({ ...filters, year: yearValue });
  };

  const handleRegionChange = (value: string) => {
    onChange({ ...filters, region: value });
  };

  return (
    <div className="panel filters">
      <div>
        <p className="label">Year</p>
        <select
          value={filters.year ?? ""}
          onChange={(e) => handleYearChange(e.target.value)}
        >
          <option value="">Latest ({years[years.length - 1] ?? "N/A"})</option>
          {years.map((year) => (
            <option key={year} value={year}>
              {year}
            </option>
          ))}
        </select>
      </div>
      <div>
        <p className="label">Region</p>
        <select
          value={filters.region}
          onChange={(e) => handleRegionChange(e.target.value)}
        >
          {regions.map((region) => (
            <option key={region} value={region}>
              {region}
            </option>
          ))}
        </select>
      </div>
      <button className="ghost" onClick={onRefresh}>
        Refresh data
      </button>
    </div>
  );
};
