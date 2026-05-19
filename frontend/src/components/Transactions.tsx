'use client';

import { useEffect, useMemo, useState } from 'react';
import { IconEdit, IconTrash } from '@tabler/icons-react';
import { useForm } from 'react-hook-form';
import {
  ReadTransactionRead,
  TransactionsListApiArg,
  useAccountsAutocompleteListQuery,
  useTransactionsDestroyMutation,
  useTransactionsListQuery,
} from '@/redux/api';
import { allPages, SEARCH_DEBOUNCE_MS } from '@/constants/constants';
import { useDebounce } from '@/hooks/useDebounce';
import { ConfirmationModal } from '@/components/ui/ConfirmationModal';
import { Pagination } from '@/components/ui/Pagination';
import { TransactionModal } from '@/components/TransactionModal';
import { toast } from 'sonner';

const DEFAULT_PAGE_SIZE = 20;

export const Transactions = () => {
  const { register, watch, setValue } = useForm<TransactionsListApiArg>({
    defaultValues: { page: 1, pageSize: DEFAULT_PAGE_SIZE },
  });
  const formValues = watch();
  const debouncedDescription = useDebounce(formValues.description, SEARCH_DEBOUNCE_MS);
  const debouncedRawCategory = useDebounce(formValues.rawCategory, SEARCH_DEBOUNCE_MS);

  const queryArg: TransactionsListApiArg = {
    ...formValues,
    description: debouncedDescription || undefined,
    rawCategory: debouncedRawCategory || undefined,
  };

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState<ReadTransactionRead | null>(null);
  const [transactionToDelete, setTransactionToDelete] = useState<ReadTransactionRead | null>(null);

  useEffect(() => {
    setValue('page', 1);
  }, [formValues.type, formValues.account, formValues.dateAfter, formValues.dateBefore,
      debouncedDescription, debouncedRawCategory, setValue]);

  const { data, isLoading } = useTransactionsListQuery(queryArg);
  const { data: accountsData } = useAccountsAutocompleteListQuery({ pageSize: allPages });
  const [destroyTransaction] = useTransactionsDestroyMutation();

  const transactions = useMemo(() => data?.results || [], [data]);
  const accounts = useMemo(() => accountsData?.results || [], [accountsData]);

  const onDelete = (id: number) => {
    destroyTransaction({ id })
      .unwrap()
      .then(() => toast.success('Transaction deleted'))
      .catch(err => toast.error(JSON.stringify(err)));
  };

  const inputClass = 'px-3 py-2 text-sm border border-gray-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100 focus:outline-none focus:ring-2 focus:ring-blue-500';

  return (
    <>
      <div className="max-w-5xl mx-auto">
        <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-lg dark:shadow-neutral-900/50 p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-3xl font-bold text-gray-800 dark:text-neutral-100">Transactions</h1>
            <button
              onClick={() => setIsCreateOpen(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium text-sm"
            >
              + Add Transaction
            </button>
          </div>

          {/* Filter bar — row 1: categorical + date filters */}
          <div className="flex flex-wrap gap-3 mb-3">
            <select
              value={queryArg.type ?? ''}
              onChange={e => setValue('type', (e.target.value || undefined) as 'income' | 'expense' | undefined)}
              className={inputClass}
            >
              <option value="">All types</option>
              <option value="income">Income</option>
              <option value="expense">Expense</option>
            </select>

            <select
              value={queryArg.account?.[0] ?? ''}
              onChange={e => setValue('account', e.target.value ? [Number(e.target.value)] : undefined)}
              className={inputClass}
            >
              <option value="">All accounts</option>
              {accounts.map(a => (
                <option key={a.id} value={a.id}>{a.name}</option>
              ))}
            </select>

            <input type="date" {...register('dateAfter')}  className={inputClass} />
            <input type="date" {...register('dateBefore')} className={inputClass} />
          </div>

          {/* Filter bar — row 2: text search filters */}
          <div className="flex gap-3 mb-6">
            <input type="text" {...register('description')} placeholder="Description" className={`${inputClass} flex-1`} />
            <input type="text" {...register('rawCategory')} placeholder="Category"    className={`${inputClass} flex-1`} />
          </div>

          {/* Content */}
          {isLoading ? (
            <div className="animate-pulse space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-10 bg-gray-200 dark:bg-neutral-700 rounded" />
              ))}
            </div>
          ) : transactions.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-500 dark:text-neutral-400 text-lg mb-2">No transactions found</div>
              <p className="text-gray-400 dark:text-neutral-500 text-sm">Add a transaction or adjust your filters.</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-neutral-700 text-left text-gray-500 dark:text-neutral-400">
                      <th className="pb-2 pr-4 font-medium">Date</th>
                      <th className="pb-2 pr-4 font-medium">Account</th>
                      <th className="pb-2 pr-4 font-medium">Type</th>
                      <th className="pb-2 pr-4 font-medium">Amount</th>
                      <th className="pb-2 pr-4 font-medium">Description</th>
                      <th className="pb-2 pr-4 font-medium">Category</th>
                      <th className="pb-2 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 dark:divide-neutral-700">
                    {transactions.map(t => (
                      <tr key={t.id} className="hover:bg-gray-50 dark:hover:bg-neutral-700/50 transition-colors">
                        <td className="py-3 pr-4 text-gray-700 dark:text-neutral-300">{t.date}</td>
                        <td className="py-3 pr-4 text-gray-700 dark:text-neutral-300">{t.account.name}</td>
                        <td className="py-3 pr-4">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                            t.type === 'income'
                              ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                              : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                          }`}>
                            {t.type}
                          </span>
                        </td>
                        <td className={`py-3 pr-4 font-medium ${
                          t.type === 'income'
                            ? 'text-green-600 dark:text-green-400'
                            : 'text-red-600 dark:text-red-400'
                        }`}>
                          {t.type === 'expense' ? '−' : '+'}{t.amount}
                        </td>
                        <td className="py-3 pr-4 text-gray-500 dark:text-neutral-400">{t.description ?? '—'}</td>
                        <td className="py-3 pr-4 text-gray-500 dark:text-neutral-400">{t.raw_category ?? '—'}</td>
                        <td className="py-3">
                          <div className="flex gap-1">
                            <button
                              onClick={() => setEditingTransaction(t)}
                              className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 p-1 rounded hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors"
                            >
                              <IconEdit size={16} />
                            </button>
                            <button
                              onClick={() => setTransactionToDelete(t)}
                              className="text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 p-1 rounded hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors"
                            >
                              <IconTrash size={16} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <Pagination
                page={queryArg.page ?? 1}
                pageSize={queryArg.pageSize ?? DEFAULT_PAGE_SIZE}
                count={data?.count ?? 0}
                onPageChange={page => setValue('page', page)}
                onPageSizeChange={size => { setValue('pageSize', size); setValue('page', 1); }}
              />
            </>
          )}
        </div>
      </div>

      <TransactionModal
        isOpen={isCreateOpen || !!editingTransaction}
        transaction={editingTransaction}
        onClose={() => { setIsCreateOpen(false); setEditingTransaction(null); }}
      />

      <ConfirmationModal
        isOpen={!!transactionToDelete}
        onClose={() => setTransactionToDelete(null)}
        onConfirm={() => {
          if (transactionToDelete) {
            onDelete(transactionToDelete.id);
            setTransactionToDelete(null);
          }
        }}
        title="Delete Transaction"
        message={`Delete "${transactionToDelete?.description || transactionToDelete?.amount}"?`}
        confirmText="Delete"
        variant="danger"
      />
    </>
  );
};
