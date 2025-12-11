import { useMemo, useState } from "react";
import { CountryRow } from "../types";
import { downloadRowsAsCsv } from "../utils/csv";

type Props = {
  rows: CountryRow[];
};

type SortKey = "country" | "region" | "year" | "receiptsUsdBillions";
type SortDirection = "asc" | "desc";

export const CountriesTable = ({ rows }: Props) => {
  const [sortBy, setSortBy] = useState<SortKey>("receiptsUsdBillions");
  const [direction, setDirection] = useState<SortDirection>("desc");

  const sortedRows = useMemo(() => {
    const sorted = [...rows].sort((a, b) => {
      const modifier = direction === "asc" ? 1 : -1;
      if (sortBy === "receiptsUsdBillions") {
        return modifier * (a.receiptsUsdBillions - b.receiptsUsdBillions);
      }
      if (sortBy === "year") {
        return modifier * (a.year - b.year);
      }
      return modifier * a[sortBy].localeCompare(b[sortBy]);
    });
    return sorted;
  }, [rows, sortBy, direction]);

  const onSort = (key: SortKey) => {
    if (key === sortBy) {
      setDirection(direction === "asc" ? "desc" : "asc");
    } else {
      setSortBy(key);
      setDirection(key === "receiptsUsdBillions" ? "desc" : "asc");
    }
  };

  const sortLabel = (key: SortKey) => {
    if (sortBy !== key) return "";
    return direction === "asc" ? "↑" : "↓";
  };

  const exportCsv = () => downloadRowsAsCsv(sortedRows);

  return (
    <div className="panel table">
      <div className="table-header">
        <div>
          <h3>Country receipts</h3>
          <p className="muted">
            Sorted by {sortBy} {direction === "asc" ? "↑" : "↓"}
          </p>
        </div>
        <button onClick={exportCsv}>Export CSV</button>
      </div>
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th onClick={() => onSort("country")}>
                Country {sortLabel("country")}
              </th>
              <th onClick={() => onSort("region")}>
                Region {sortLabel("region")}
              </th>
              <th onClick={() => onSort("year")}>
                Year {sortLabel("year")}
              </th>
              <th className="numeric" onClick={() => onSort("receiptsUsdBillions")}>
                Receipts (USD B) {sortLabel("receiptsUsdBillions")}
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedRows.map((row) => (
              <tr key={`${row.code}-${row.year}`}>
                <td>
                  <span className="pill">{row.code}</span> {row.country}
                </td>
                <td>{row.region}</td>
                <td>{row.year}</td>
                <td className="numeric">
                  {row.receiptsUsdBillions.toLocaleString(undefined, {
                    maximumFractionDigits: 2,
                    minimumFractionDigits: 2,
                  })}
                </td>
              </tr>
            ))}
            {!sortedRows.length && (
              <tr>
                <td colSpan={4} className="muted">
                  No rows for this filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
