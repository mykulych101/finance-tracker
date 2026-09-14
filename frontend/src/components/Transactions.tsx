'use client';

import { useEffect, useState } from 'react';
import { IconEdit, IconTrash } from '@tabler/icons-react';
import { useForm } from 'react-hook-form';
import { toast } from 'sonner';
import { TransactionModal } from '@/components/TransactionModal';
import { ConfirmationModal } from '@/components/ui/ConfirmationModal';
import { Pagination } from '@/components/ui/Pagination';
import { SortIcon } from '@/components/ui/SortIcon';
import { allPages, CURRENCY_SYMBOLS, SEARCH_DEBOUNCE_MS } from '@/constants/constants';
import { useDebounce } from '@/hooks/useDebounce';
import {
  ReadTransactionRead,
  TransactionsListApiArg,
  useAccountsAutocompleteListQuery,
  useTransactionsDestroyMutation,
  useTransactionsListQuery,
} from '@/redux/api';
import { TransactionSort, TransactionSortField } from '@/types/transactions';

const DEFAULT_PAGE_SIZE = 20;

export const Transactions = () => {
  const { register, watch, setValue } = useForm<TransactionsListApiArg>({
    defaultValues: { page: 1, pageSize: DEFAULT_PAGE_SIZE },
  });
  const formValues = watch();
  const debouncedDescription = useDebounce(formValues.description, SEARCH_DEBOUNCE_MS);
  const debouncedRawCategory = useDebounce(formValues.rawCategory, SEARCH_DEBOUNCE_MS);

  const [sort, setSort] = useState<TransactionSort | null>(null);

  const ordering = sort
    ? ([sort.dir === 'desc' ? `-${sort.field}` : sort.field] as TransactionsListApiArg['ordering'])
    : undefined;

  const queryArg: TransactionsListApiArg = {
    ...formValues,
    description: debouncedDescription || undefined,
    rawCategory: debouncedRawCategory || undefined,
    ordering,
  };

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState<ReadTransactionRead | null>(null);
  const [transactionToDelete, setTransactionToDelete] = useState<ReadTransactionRead | null>(null);

  useEffect(() => {
    setValue('page', 1);
  }, [formValues.type, formValues.account, formValues.dateAfter, formValues.dateBefore,
    debouncedDescription, debouncedRawCategory, setValue]);

  const { data: transactions, isLoading } = useTransactionsListQuery(queryArg);
  const { data: accounts } = useAccountsAutocompleteListQuery({ pageSize: allPages });
  const [destroyTransaction] = useTransactionsDestroyMutation();


  const handleSort = (field: TransactionSortField) => {
    setSort(prev => {
      if (prev?.field !== field) return { field, dir: 'asc' };
      if (prev.dir === 'asc') return { field, dir: 'desc' };
      return null;
    });
    setValue('page', 1);
  };

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
            <div className="flex flex-col gap-1">
              <select
                multiple
                value={(queryArg.account ?? []).map(String)}
                onChange={e => {
                  const selected = Array.from(e.target.selectedOptions, o => Number(o.value));
                  setValue('account', selected.length ? selected : undefined);
                }}
                className={`${inputClass} min-w-[200px]`}
              >
                {accounts?.results.map(a => (
                  <option key={a.id} value={a.id}>{CURRENCY_SYMBOLS[a.currency]} {a.name}</option>
                ))}
              </select>
              {!!queryArg.account?.length && (
                <button
                  type="button"
                  onClick={() => setValue('account', undefined)}
                  className="self-start text-xs text-blue-600 dark:text-blue-400 hover:underline"
                >
                  Clear accounts
                </button>
              )}
            </div>
            <select
              value={queryArg.type ?? ''}
              onChange={e => setValue('type', (e.target.value || undefined) as 'income' | 'expense' | undefined)}
              className={inputClass}
            >
              <option value="">All types</option>
              <option value="income">Income</option>
              <option value="expense">Expense</option>
            </select>

            <input type="date" {...register('dateAfter')} className={inputClass} />
            <input type="date" {...register('dateBefore')} className={inputClass} />
          </div>

          {/* Filter bar — row 2: text search filters */}
          <div className="flex gap-3 mb-6">
            <input type="text" {...register('description')} placeholder="Description" className={`${inputClass} flex-1`} />
            <input type="text" {...register('rawCategory')} placeholder="Category" className={`${inputClass} flex-1`} />
          </div>

          {/* Content */}
          {isLoading ? (
            <div className="animate-pulse space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-10 bg-gray-200 dark:bg-neutral-700 rounded" />
              ))}
            </div>
          ) : transactions?.results.length === 0 ? (
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
                      <th className="pb-2 pr-4 font-medium cursor-pointer select-none hover:text-gray-700 dark:hover:text-neutral-200" onClick={() => handleSort('date')}>Date<SortIcon activeField={sort?.field ?? null} direction={sort?.dir ?? 'asc'} field="date" /></th>
                      <th className="pb-2 pr-4 font-medium">Account</th>
                      <th className="pb-2 pr-4 font-medium cursor-pointer select-none hover:text-gray-700 dark:hover:text-neutral-200" onClick={() => handleSort('type')}>Type<SortIcon activeField={sort?.field ?? null} direction={sort?.dir ?? 'asc'} field="type" /></th>
                      <th className="pb-2 pr-4 font-medium cursor-pointer select-none hover:text-gray-700 dark:hover:text-neutral-200" onClick={() => handleSort('amount')}>Amount<SortIcon activeField={sort?.field ?? null} direction={sort?.dir ?? 'asc'} field="amount" /></th>
                      <th className="pb-2 pr-4 font-medium cursor-pointer select-none hover:text-gray-700 dark:hover:text-neutral-200" onClick={() => handleSort('description')}>Description<SortIcon activeField={sort?.field ?? null} direction={sort?.dir ?? 'asc'} field="description" /></th>
                      <th className="pb-2 pr-4 font-medium cursor-pointer select-none hover:text-gray-700 dark:hover:text-neutral-200" onClick={() => handleSort('raw_category')}>Category<SortIcon activeField={sort?.field ?? null} direction={sort?.dir ?? 'asc'} field="raw_category" /></th>
                      <th className="pb-2 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 dark:divide-neutral-700">
                    {transactions?.results.map(t => (
                      <tr key={t.id} className="hover:bg-gray-50 dark:hover:bg-neutral-700/50 transition-colors">
                        <td className="py-3 pr-4 text-gray-700 dark:text-neutral-300">{t.date}</td>
                        <td className="py-3 pr-4 text-gray-700 dark:text-neutral-300">{t.account.name}</td>
                        <td className="py-3 pr-4">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${t.type === 'income'
                            ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                            : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                            }`}>
                            {t.type}
                          </span>
                        </td>
                        <td className={`py-3 pr-4 font-medium ${t.type === 'income'
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
                count={transactions?.count ?? 0}
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
