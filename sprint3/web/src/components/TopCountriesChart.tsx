import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  ChartOptions,
  Legend,
  LinearScale,
  Title,
  Tooltip,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import { CountryRow } from "../types";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

type Props = {
  data: CountryRow[];
  year?: number;
  region: string;
};

export const TopCountriesChart = ({ data, year, region }: Props) => {
  const labels = data.map((item) => `${item.country} (${item.code})`);
  const values = data.map((item) =>
    Number(item.receiptsUsdBillions.toFixed(2))
  );

  const options: ChartOptions<"bar"> = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: `Top ${data.length} earners – ${region || "All regions"} ${
          year ?? ""
        }`,
        color: "#e8edf7",
        font: {
          size: 16,
          weight: "600",
          family: "Space Grotesk, Inter, system-ui",
        },
      },
      tooltip: {
        callbacks: {
          label: (ctx) =>
            `${ctx.dataset.label}: ${ctx.parsed.y.toLocaleString()} B USD`,
        },
      },
    },
    scales: {
      x: {
        ticks: { color: "#b8c1d9" },
        grid: { display: false },
      },
      y: {
        ticks: {
          color: "#b8c1d9",
          callback: (value) =>
            typeof value === "number" ? `${value.toFixed(0)}B` : value,
        },
        grid: { color: "rgba(255,255,255,0.05)" },
      },
    },
  };

  const chartData = {
    labels,
    datasets: [
      {
        label: "USD Billions",
        data: values,
        backgroundColor: [
          "rgba(82, 113, 255, 0.8)",
          "rgba(118, 210, 255, 0.8)",
          "rgba(255, 173, 94, 0.85)",
          "rgba(192, 140, 255, 0.8)",
          "rgba(255, 120, 203, 0.7)",
        ],
        borderRadius: 12,
      },
    ],
  };

  return (
    <div className="panel chart">
      <Bar options={options} data={chartData} />
    </div>
  );
};
