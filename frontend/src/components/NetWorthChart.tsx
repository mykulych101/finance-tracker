'use client';

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  Filler,
  TooltipItem,
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import { Line } from 'react-chartjs-2';
import { useCurrency } from '@/context/CurrencyContext';
import { useTheme } from '@/context/ThemeContext';
import { AnalyticsNetWorthHistoryItem } from '@/redux/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  Filler
);

interface NetWorthChartProps {
  history: AnalyticsNetWorthHistoryItem[];
  height?: number;
}

export const NetWorthChart = ({ history, height = 400 }: NetWorthChartProps) => {
  const { formatCurrency, selectedCurrency } = useCurrency();
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === 'dark';

  const textColor = isDark ? '#e5e5e5' : '#374151';
  const gridColor = isDark ? 'rgba(163, 163, 163, 0.3)' : 'rgba(0, 0, 0, 0.1)';

  if (history.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-neutral-700/50 rounded-lg">
        <p className="text-gray-500 dark:text-neutral-400">No data available for net worth tracking</p>
      </div>
    );
  }

  const data = {
    labels: history.map(item => item.date),
    datasets: [
      {
        label: 'Assets',
        data: history.map(item => item.assets),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        borderWidth: 2,
        fill: false,
        tension: 0.1,
      },
      {
        label: 'Liabilities',
        data: history.map(item => item.liabilities),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        borderWidth: 2,
        fill: false,
        tension: 0.1,
      },
      {
        label: 'Net Worth',
        data: history.map(item => item.net_worth),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: { color: textColor },
      },
      title: {
        display: true,
        text: 'Net Worth Over Time',
        color: textColor,
        font: {
          size: 16,
          weight: 'bold' as const,
        },
      },
      tooltip: {
        callbacks: {
          label: function (context: TooltipItem<'line'>) {
            const y = context.parsed.y;
            return y == null ? 'Balance: N/A' : `Balance: ${formatCurrency(y)}`;
          },
        },
      },
    },
    scales: {
      x: {
        type: 'time' as const,
        time: {
          unit: 'day' as const,
        },
        title: {
          display: true,
          text: 'Date',
          color: textColor,
        },
        ticks: { color: textColor },
        grid: { color: gridColor },
      },
      y: {
        title: {
          display: true,
          text: `Amount (${selectedCurrency.symbol})`,
          color: textColor,
        },
        ticks: {
          color: textColor,
          callback: function (value: number | string) {
            return formatCurrency(Number(value));
          },
        },
        grid: { color: gridColor },
      },
    },
    interaction: {
      intersect: false,
      mode: 'index' as const,
    },
  };

  // Calculate summary stats
  const latestData = history[history.length - 1];
  const firstData = history[0];
  const netWorthChange = latestData.net_worth - firstData.net_worth;
  const netWorthChangePercent = firstData.net_worth !== 0
    ? ((latestData.net_worth - firstData.net_worth) / Math.abs(firstData.net_worth)) * 100
    : 0;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">Current Net Worth</h3>
          <div className={`text-2xl font-bold ${latestData.net_worth >= 0 ? 'text-blue-600 dark:text-blue-400' : 'text-red-600 dark:text-red-400'
            }`}>
            {formatCurrency(latestData.net_worth)}
          </div>
        </div>

        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
          <h3 className="font-semibold text-green-800 dark:text-green-300 mb-2">Total Assets</h3>
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {formatCurrency(latestData.assets)}
          </div>
        </div>

        <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800">
          <h3 className="font-semibold text-red-800 dark:text-red-300 mb-2">Total Liabilities</h3>
          <div className="text-2xl font-bold text-red-600 dark:text-red-400">
            {formatCurrency(latestData.liabilities)}
          </div>
        </div>

        <div className="bg-gray-50 dark:bg-neutral-700/50 rounded-lg p-4 border border-gray-200 dark:border-neutral-600">
          <h3 className="font-semibold text-gray-800 dark:text-neutral-200 mb-2">Change</h3>
          <div className={`text-lg font-bold ${netWorthChange >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
            }`}>
            <div>{formatCurrency(netWorthChange)}</div>
            <div className="text-sm">
              ({netWorthChange >= 0 ? '+' : ''}{netWorthChangePercent.toFixed(1)}%)
            </div>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white dark:bg-neutral-800 rounded-lg border dark:border-neutral-600 p-4">
        <div style={{ height: `${height}px` }} className="w-full">
          <Line data={data} options={options} />
        </div>
      </div>
    </div>
  );
};
