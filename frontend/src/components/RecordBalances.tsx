'use client';

import { useEffect, useMemo, useState } from 'react';
import { useForm } from 'react-hook-form';
import {
  AccountRead,
  BalanceRecord,
  useAccountsListQuery,
  useBalancesListQuery,
  useBalancesBulkCreateCreateMutation,
} from '@/redux/api';
import { allPages } from '@/constants/constants';
import { ConfirmationModal } from '@/components/ui/ConfirmationModal';
import { toast } from 'sonner';

type FormValues = {
  date: string;
  amounts: Record<string, string>;
};

export const RecordBalances = () => {
  const { register, handleSubmit, watch, setValue, reset } = useForm<FormValues>({
    defaultValues: {
      date: new Date().toISOString().split('T')[0],
      amounts: {},
    },
  });

  const selectedDate = watch('date');

  const { data: accountsData, isLoading: accountsLoading } = useAccountsListQuery({ pageSize: allPages });
  const { data: balancesData } = useBalancesListQuery({ date: selectedDate, pageSize: allPages });
  const [bulkCreate, { isLoading }] = useBalancesBulkCreateCreateMutation();
  const [pendingUpdates, setPendingUpdates] = useState<BalanceRecord[]>([]);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);

  const accounts = useMemo(() => accountsData?.results || [], [accountsData]);
  const balances = useMemo(() => balancesData?.results || [], [balancesData]);

  useEffect(() => {
    const amounts: Record<string, string> = {};
    accounts.forEach(account => {
      const existing = balances.find(b => b.account === account.id);
      amounts[String(account.id)] = existing?.amount ?? '';
    });
    reset({ date: selectedDate, amounts });
  }, [selectedDate, accounts, balances, reset]);

  const submit = (updates: BalanceRecord[]) => {
    bulkCreate({ body: updates })
      .unwrap()
      .then(() =>
        toast.success(`Updated ${updates.length} balance${updates.length > 1 ? 's' : ''}`)
      )
      .catch(err => toast.error(JSON.stringify(err)));
  };

  const onSubmit = (data: FormValues) => {
    const updates = Object.entries(data.amounts)
      .filter(([, amount]) => typeof amount === 'string' && amount.trim() !== '')
      .map(([accountId, amount]) => ({
        account: Number(accountId),
        amount,
        date: data.date,
      }))
      .filter(update => {
        const existing = balances.find(b => b.account === update.account);
        return !existing || existing.amount !== update.amount;
      });

    if (updates.length === 0) return;

    const updatesOverExisting = updates.filter(u => balances.some(b => b.account === u.account));
    if (updatesOverExisting.length > 0) {
      setPendingUpdates(updates);
      setIsConfirmOpen(true);
      return;
    }

    submit(updates);
  };

  const handleConfirm = () => {
    setIsConfirmOpen(false);
    submit(pendingUpdates);
  };

  const groupedAccounts = accounts.reduce((groups, account) => {
    if (!groups[account.type]) groups[account.type] = {};
    if (!groups[account.type][account.category]) groups[account.type][account.category] = [];
    groups[account.type][account.category].push(account);
    return groups;
  }, {} as Record<string, Record<string, AccountRead[]>>);

  if (accountsLoading) return null;

  if (accounts.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 dark:text-neutral-400 text-lg mb-4">No accounts to update</div>
        <p className="text-gray-400 dark:text-neutral-500">Add some accounts first to record their balances.</p>
      </div>
    );
  }

  const existingBalanceNames = balances
    .filter(b => pendingUpdates.some(u => u.account === b.account))
    .map(b => accounts.find(a => a.id === b.account)?.name ?? `Account #${b.account}`);

  return (
    <>
    <ConfirmationModal
      isOpen={isConfirmOpen}
      onClose={() => setIsConfirmOpen(false)}
      onConfirm={handleConfirm}
      title="Replace existing balances?"
      variant="warning"
      confirmText="Replace"
      message={
        <span>
          The following accounts already have balances for this date:
          <ul className="mt-2 mb-1 list-disc list-inside">
            {existingBalanceNames.map(name => <li key={name}>{name}</li>)}
          </ul>
        </span>
      }
    />
    <div className="max-w-4xl mx-auto">
      <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-lg dark:shadow-neutral-900/50 p-6">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 dark:text-neutral-100 mb-2">Record Account Balances</h1>
          <p className="text-gray-600 dark:text-neutral-400">Update the current balances for your accounts</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
          <div>
            <label htmlFor="balance-date" className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-2">
              Balance Date
            </label>
            <input
              type="date"
              id="balance-date"
              {...register('date')}
              className="px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100"
            />
            <p className="text-sm text-gray-500 dark:text-neutral-400 mt-1">
              Record balances for this specific date. Defaults to today.
            </p>
          </div>

          {Object.entries(groupedAccounts).map(([type, categories]) => (
            <div key={type} className="border dark:border-neutral-600 rounded-lg p-4">
              <h2 className="text-xl font-bold text-gray-800 dark:text-neutral-100 mb-4 capitalize">
                {type === 'asset' ? 'Assets' : type === 'liability' ? 'Liabilities' : 'Equity'}
              </h2>

              {Object.entries(categories).map(([category, categoryAccounts]) => (
                <div key={category} className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-700 dark:text-neutral-300 mb-3">{category}</h3>
                  <div className="space-y-3">
                    {categoryAccounts.map((account) => (
                      <div key={account.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-neutral-700/50 rounded-lg">
                        <div className="flex-1">
                          <div className="font-medium text-gray-800 dark:text-neutral-200">{account.name}</div>
                          <div className="text-sm text-gray-500 dark:text-neutral-400">
                            Current: {account.current_balance}
                          </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <label htmlFor={`balance-${account.id}`} className="text-sm font-medium text-gray-700 dark:text-neutral-300">
                            New Balance:
                          </label>
                          <input
                            type="text"
                            id={`balance-${account.id}`}
                            {...register(`amounts.${account.id}`, {
                              onChange: (e) => {
                                const v = e.target.value;
                                if (v !== '' && !/^-?\d*\.?\d*$/.test(v)) {
                                  setValue(`amounts.${account.id}`, v.slice(0, -1));
                                }
                              },
                            })}
                            disabled={isLoading}
                            className="w-32 px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-right bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100"
                            placeholder="0.00"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ))}

          <div className="flex justify-center pt-6">
            <button
              type="submit"
              disabled={isLoading}
              className="px-8 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? 'Updating...' : 'Update All Balances'}
            </button>
          </div>
        </form>
      </div>
    </div>
    </>
  );
};
