import { CountryRow } from "../types";

const escapeCell = (value: string | number) =>
  `"${String(value).replace(/"/g, '""')}"`;

export const downloadRowsAsCsv = (
  rows: CountryRow[],
  filename = "tourism_receipts.csv"
) => {
  if (!rows.length) return;
  const header = [
    "Country",
    "Code",
    "Region",
    "Year",
    "Receipts USD",
    "Receipts USD Billions",
  ];
  const body = rows.map((row) =>
    [
      escapeCell(row.country),
      escapeCell(row.code),
      escapeCell(row.region),
      row.year,
      row.receiptsUsd,
      row.receiptsUsdBillions.toFixed(2),
    ].join(",")
  );

  const csv = [header.join(","), ...body].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
};
