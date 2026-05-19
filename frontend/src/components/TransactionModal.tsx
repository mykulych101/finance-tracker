'use client';

import { useEffect, useMemo } from 'react';
import { useForm } from 'react-hook-form';
import {
  AccountSlimRead,
  ReadTransactionRead,
  WriteTransactionWrite,
  useAccountsAutocompleteListQuery,
  useTransactionsCreateMutation,
  useTransactionsPartialUpdateMutation,
} from '@/redux/api';
import { allPages } from '@/constants/constants';
import { toast } from 'sonner';

interface TransactionModalProps {
  isOpen: boolean;
  transaction: ReadTransactionRead | null;
  onClose: () => void;
}

export const TransactionModal = ({ isOpen, transaction, onClose }: TransactionModalProps) => {
  const { data: accountsData } = useAccountsAutocompleteListQuery({ pageSize: allPages });
  const accounts: AccountSlimRead[] = useMemo(() => accountsData?.results || [], [accountsData]);

  const [createTransaction, { isLoading: isCreating }] = useTransactionsCreateMutation();
  const [updateTransaction, { isLoading: isUpdating }] = useTransactionsPartialUpdateMutation();
  const isLoading = isCreating || isUpdating;

  const { register, handleSubmit, reset } = useForm<WriteTransactionWrite>({
    defaultValues: { type: 'expense', date: new Date().toISOString().split('T')[0] },
  });

  useEffect(() => {
    if (transaction) {
      reset({
        type: transaction.type,
        amount: transaction.amount,
        date: transaction.date,
        description: transaction.description,
        raw_category: transaction.raw_category,
        account_id: transaction.account.id,
      });
    } else {
      reset({ type: 'expense', date: new Date().toISOString().split('T')[0] });
    }
  }, [transaction, reset]);

  const onSubmit = (data: WriteTransactionWrite) => {
    const action = transaction
      ? updateTransaction({ id: transaction.id, patchedWriteTransaction: data })
      : createTransaction({ writeTransaction: data });

    action
      .unwrap()
      .then(() => {
        toast.success(transaction ? 'Transaction updated' : 'Transaction added');
        onClose();
      })
      .catch(err => toast.error(JSON.stringify(err)));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-gray-900/30 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-md rounded-2xl bg-white dark:bg-neutral-800 p-6 shadow-xl border border-gray-100 dark:border-neutral-700">
        <h2 className="text-xl font-bold text-gray-800 dark:text-neutral-100 mb-5">
          {transaction ? 'Edit Transaction' : 'Add Transaction'}
        </h2>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-1">Type</label>
            <select
              {...register('type', { required: true })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="expense">Expense</option>
              <option value="income">Income</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-1">Account</label>
            <select
              {...register('account_id', { required: true, valueAsNumber: true })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select account</option>
              {accounts.map(a => (
                <option key={a.id} value={a.id}>{a.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-1">Amount</label>
            <input
              type="text"
              {...register('amount', { required: true })}
              placeholder="0.00"
              className="w-full px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-1">Date</label>
            <input
              type="date"
              {...register('date', { required: true })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-1">
              Description{' '}
              <span className="text-gray-400 dark:text-neutral-500 font-normal">(optional)</span>
            </label>
            <input
              type="text"
              {...register('description')}
              placeholder="e.g. Grocery shopping"
              className="w-full px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-1">
              Category{' '}
              <span className="text-gray-400 dark:text-neutral-500 font-normal">(optional)</span>
            </label>
            <input
              type="text"
              {...register('raw_category')}
              placeholder="e.g. Food"
              className="w-full px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {isLoading ? 'Saving…' : transaction ? 'Save Changes' : 'Add Transaction'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 bg-gray-100 dark:bg-neutral-700 text-gray-700 dark:text-neutral-200 rounded-md hover:bg-gray-200 dark:hover:bg-neutral-600 transition-colors font-medium"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
