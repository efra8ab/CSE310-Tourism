import {
  CategoryScale,
  Chart as ChartJS,
  ChartOptions,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
} from "chart.js";
import { Line } from "react-chartjs-2";
import { YearTotal } from "../types";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

type Props = {
  data: YearTotal[];
  region: string;
};

export const TrendsLineChart = ({ data, region }: Props) => {
  const sorted = [...data].sort((a, b) => a.year - b.year);
  const labels = sorted.map((item) => item.year);
  const values = sorted.map((item) => Number(item.totalUsdBillions.toFixed(2)));

  const options: ChartOptions<"line"> = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: `Receipts trend (${region})`,
        color: "#e8edf7",
        font: { size: 16, weight: "600", family: "Space Grotesk, Inter" },
      },
      tooltip: {
        callbacks: {
          label: (ctx) =>
            `${ctx.parsed.y.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })} B USD`,
        },
      },
    },
    scales: {
      x: {
        ticks: { color: "#b8c1d9" },
        grid: { display: false },
      },
      y: {
        ticks: { color: "#b8c1d9" },
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
        fill: false,
        tension: 0.3,
        borderColor: "rgba(118, 210, 255, 1)",
        backgroundColor: "rgba(118, 210, 255, 0.15)",
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  };

  return (
    <div className="panel chart">
      <Line options={options} data={chartData} />
    </div>
  );
};
