'use client';

import { useState, useEffect } from 'react';
import { format, subDays } from 'date-fns';
import { allPages } from '@/constants/constants';
import { useCurrency } from '@/context/CurrencyContext';
import {
  AccountRead,
  CurrencyEnum,
  useAccountsListQuery,
  useAnalyticsNetWorthHistoryListQuery,
  useAnalyticsNetWorthRetrieveQuery,
} from '@/redux/api';
import { useAppSelector } from '@/redux/hooks';
import { BalanceChart } from './BalanceChart';
import { CurrencySelector } from './CurrencySelector';
import { NetWorthChart } from './NetWorthChart';

type DateRange = '7d' | '30d' | '90d' | '1y' | 'all';
type Period = 'daily' | 'monthly' | 'weekly';

const getDateParams = (range: DateRange): { dateAfter: string; dateBefore: string } => {
  const today = format(new Date(), 'yyyy-MM-dd');
  const days: Partial<Record<DateRange, number>> = { '7d': 7, '30d': 30, '90d': 90, '1y': 365 };
  const dateAfter = range !== 'all'
    ? format(subDays(new Date(), days[range]!), 'yyyy-MM-dd')
    : '2000-01-01';
  return { dateAfter, dateBefore: today };
};

const getPeriod = (range: DateRange): Period => {
  if (range === '7d' || range === '30d') return 'daily';
  if (range === '90d') return 'weekly';
  return 'monthly';
};

const getBalanceField = (type: string): 'assets' | 'liabilities' =>
  type === 'asset' ? 'assets' : 'liabilities';

interface AccountQueryProps {
  account: AccountRead;
  dateAfter: string;
  dateBefore: string;
  period: Period;
  convertTo?: CurrencyEnum;
}

const AccountSummaryCard = ({ account, dateAfter, dateBefore, period, convertTo }: AccountQueryProps) => {
  const { formatCurrency } = useCurrency();
  const { data: history = [] } = useAnalyticsNetWorthHistoryListQuery({
    account: account.id,
    dateAfter,
    dateBefore,
    period,
    convertTo,
  });
  const field = getBalanceField(account.type);
  const latest = history.length > 0 ? history[history.length - 1][field] : 0;
  const first = history.length > 0 ? history[0][field] : 0;
  const change = latest - first;
  const changePct = first !== 0 ? (change / Math.abs(first)) * 100 : 0;

  return (
    <div className="bg-gray-50 dark:bg-neutral-700/50 rounded-lg p-4 border dark:border-neutral-600">
      <h3 className="font-semibold text-gray-800 dark:text-neutral-200 mb-2">{account.name}</h3>
      <div className="text-lg font-bold mb-1 text-gray-900 dark:text-neutral-100">
        {formatCurrency(latest)}
      </div>
      <div className={`text-sm flex items-center space-x-2 ${change >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
        <span>{change >= 0 ? '↗' : '↘'}</span>
        <span>
          {formatCurrency(Math.abs(change))}
          ({Math.abs(changePct).toFixed(1)}%)
        </span>
      </div>
      <div className="text-xs text-gray-500 dark:text-neutral-400 mt-1">
        {history.length} data points
      </div>
    </div>
  );
};

const AccountChartSection = ({ account, dateAfter, dateBefore, period, convertTo }: AccountQueryProps) => {
  const { data: items = [] } = useAnalyticsNetWorthHistoryListQuery({
    account: account.id,
    dateAfter,
    dateBefore,
    period,
    convertTo,
  });
  const field = getBalanceField(account.type);
  const history = items.map(item => ({ date: item.date, amount: item[field] }));

  return (
    <div className="border dark:border-neutral-600 rounded-lg p-4">
      <BalanceChart account={account} history={history} height={300} />
    </div>
  );
};

const IndividualAccountView = ({ account, dateAfter, dateBefore, period, convertTo }: AccountQueryProps) => {
  const { formatCurrency } = useCurrency();
  const { data: history = [] } = useAnalyticsNetWorthHistoryListQuery({
    account: account.id,
    dateAfter,
    dateBefore,
    period,
    convertTo,
  });
  const field = getBalanceField(account.type);
  const balanceHistory = history.map(item => ({ date: item.date, amount: item[field] }));
  const latest = history.length > 0 ? history[history.length - 1][field] : 0;
  const change = history.length >= 2 ? history[history.length - 1][field] - history[0][field] : 0;

  return (
    <div>
      <BalanceChart account={account} history={balanceHistory} height={500} />

      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
          <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">Current Balance</h3>
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {formatCurrency(latest)}
          </div>
        </div>

        <div className="bg-gray-50 dark:bg-neutral-700/50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-800 dark:text-neutral-200 mb-2">Change</h3>
          <div className={`text-2xl font-bold ${change >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
            {formatCurrency(change)}
          </div>
        </div>

        <div className="bg-gray-50 dark:bg-neutral-700/50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-800 dark:text-neutral-200 mb-2">Data Points</h3>
          <div className="text-2xl font-bold text-gray-600 dark:text-neutral-300">
            {history.length}
          </div>
        </div>
      </div>
    </div>
  );
};

export const HistoricalTracking = () => {
  const convertTo = useAppSelector(state => state.currency.convertTo);
  const [selectedAccount, setSelectedAccount] = useState<string>('all');
  const [dateRange, setDateRange] = useState<DateRange>('30d');
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const { dateAfter, dateBefore } = getDateParams(dateRange);
  const period = getPeriod(dateRange);

  const { data: overallHistory = [], isLoading: isHistoryLoading } = useAnalyticsNetWorthHistoryListQuery({
    dateAfter,
    dateBefore,
    period,
    convertTo: convertTo ?? undefined,
  });

  const { data: netWorthSnapshot, isLoading: isSnapshotLoading } = useAnalyticsNetWorthRetrieveQuery({
    convertTo: convertTo ?? undefined,
  });

  const { data: accountsData, isLoading: isAccountsLoading } = useAccountsListQuery({
    pageSize: allPages,
    convertTo: convertTo ?? undefined,
  });

  const isLoading = isHistoryLoading || isSnapshotLoading || isAccountsLoading;

  const snapshotAccountIds = new Set((netWorthSnapshot?.accounts ?? []).map(a => a.id));
  const accountsWithHistory = (accountsData?.results ?? []).filter(a => snapshotAccountIds.has(a.id));
  const selectedAccountData = accountsData?.results.find(a => String(a.id) === selectedAccount);

  if (!isClient || isLoading) {
    return (
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-lg dark:shadow-neutral-900/50 p-6">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-800 dark:text-neutral-100 mb-2">Historical Tracking</h1>
            <p className="text-gray-600 dark:text-neutral-400">Loading your historical data...</p>
          </div>
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 dark:bg-neutral-700 rounded w-3/4"></div>
            <div className="h-64 bg-gray-200 dark:bg-neutral-700 rounded"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="h-32 bg-gray-200 dark:bg-neutral-700 rounded"></div>
              <div className="h-32 bg-gray-200 dark:bg-neutral-700 rounded"></div>
              <div className="h-32 bg-gray-200 dark:bg-neutral-700 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (accountsWithHistory.length === 0) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-lg dark:shadow-neutral-900/50 p-6">
          <div className="text-center py-12">
            <div className="text-gray-500 dark:text-neutral-400 text-lg mb-4">No historical data available</div>
            <p className="text-gray-400 dark:text-neutral-500">Record some balances to see charts and trends.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-lg dark:shadow-neutral-900/50 p-6">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 dark:text-neutral-100 mb-2">Historical Tracking</h1>
          <p className="text-gray-600 dark:text-neutral-400">View balance trends and historical data for your accounts</p>
        </div>

        {/* Currency Selection */}
        <div className="mb-6 flex justify-end">
          <CurrencySelector size="sm" />
        </div>

        {/* Controls */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <div className="flex-1">
            <label htmlFor="account-select" className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-2">
              Select Account
            </label>
            <select
              id="account-select"
              value={selectedAccount}
              onChange={(e) => setSelectedAccount(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100"
            >
              <option value="all">All Accounts Overview</option>
              {accountsWithHistory.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.name} ({account.type})
                </option>
              ))}
            </select>
          </div>

          <div className="flex-1">
            <label htmlFor="date-range" className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-2">
              Time Period
            </label>
            <select
              id="date-range"
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value as DateRange)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
              <option value="all">All time</option>
            </select>
          </div>
        </div>

        {/* Chart Display */}
        {selectedAccount === 'all' ? (
          <div className="space-y-8">
            {/* Net Worth Chart */}
            <div className="mb-8">
              <NetWorthChart history={overallHistory} height={400} />
            </div>

            <h2 className="text-xl font-bold text-gray-800 dark:text-neutral-100 mb-4">Individual Account Summary</h2>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
              {accountsWithHistory.map((account) => (
                <AccountSummaryCard
                  key={account.id}
                  account={account}
                  dateAfter={dateAfter}
                  dateBefore={dateBefore}
                  period={period}
                  convertTo={convertTo ?? undefined}
                />
              ))}
            </div>

            {/* Individual Charts */}
            <div className="space-y-8">
              {accountsWithHistory.map((account) => (
                <AccountChartSection
                  key={account.id}
                  account={account}
                  dateAfter={dateAfter}
                  dateBefore={dateBefore}
                  period={period}
                  convertTo={convertTo ?? undefined}
                />
              ))}
            </div>
          </div>
        ) : (
          selectedAccountData && (
            <IndividualAccountView
              account={selectedAccountData}
              dateAfter={dateAfter}
              dateBefore={dateBefore}
              period={period}
              convertTo={convertTo ?? undefined}
            />
          )
        )}
      </div>
    </div>
  );
};
