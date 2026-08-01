'use client';

import { useEffect } from 'react';
import { Account, AccountRead, useAccountsPartialUpdateMutation } from '@/redux/api';
import { useForm } from 'react-hook-form';
import { ACCOUNT_CATEGORIES, ACCOUNT_TYPES, CURRENCY_OPTIONS } from '@/constants/financeConstants';
import { toast } from 'sonner';

interface ManageAccountModalProps {
  account: AccountRead;
  onClose: () => void;
}

export const ManageAccountModal = ({ account, onClose }: ManageAccountModalProps) => {
  const [updateAccount, { isLoading: isUpdating }] = useAccountsPartialUpdateMutation();
  const { register, handleSubmit, watch, setValue } = useForm<Account>({
    defaultValues: {
      ...account,
      category: account.category
    }
  })
  const selectedType = watch('type', 'asset')
  const selectedCategory = watch('category')

  useEffect(() => {
    setValue('category', ACCOUNT_CATEGORIES[selectedType][0]);
  }, [selectedType, setValue]);


  const onSubmit = (values: Account) => {

    updateAccount({ id: account.id, patchedWriteAccount: values }).unwrap().then(() => {
      toast.success('Account updated successfully!');
      onClose();
    }).catch(error => toast.error(JSON.stringify(error)))
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">
      <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-xl dark:shadow-neutral-900/50 w-full max-w-md p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-neutral-100">Edit Account</h2>
            <p className="text-sm text-gray-500 dark:text-neutral-400">Update the account name, type, or category.</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 dark:text-neutral-400 hover:text-gray-700 dark:hover:text-neutral-200"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label htmlFor="account-name" className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-1">
              Account Name
            </label>
            <input
              id="account-name"
              type="text"
              {...register('name', { required: true })}
              className="w-full border border-gray-300 dark:border-neutral-600 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100"
              placeholder="e.g., Checking Account"
            />
          </div>

          <div>
            <label htmlFor="accountType" className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-1">
              Account Type
            </label>
            <select
              id="accountType"
              {...register('type', { required: true })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100"
            >
              {ACCOUNT_TYPES.map(type => <option key={type} value={type}>
                {type}
              </option>)}
            </select>
          </div>

          <div>
            <label htmlFor="accountCategory" className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-1">
              Category
            </label>
            <select
              id="accountCategory"
              {...register('category', { required: true })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100"
            >
              {ACCOUNT_CATEGORIES[selectedType].map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="accountCurrency" className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-1">
              Currency
            </label>
            <select
              id="accountCurrency"
              {...register('currency', { required: true })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100"
            >
              {CURRENCY_OPTIONS.map((currency) => (
                <option key={currency} value={currency}>
                  {currency}
                </option>
              ))}
            </select>
          </div>

          {selectedCategory === 'credit_card' && (
            <div>
              <label htmlFor="creditLimit" className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-1">
                Credit Limit
              </label>
              <input
                type="number"
                id="creditLimit"
                {...register('credit_limit')}
                className="w-full border border-gray-300 dark:border-neutral-600 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100"
                placeholder="e.g., 5000"
              />
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-md border border-gray-300 dark:border-neutral-600 text-gray-700 dark:text-neutral-300 hover:bg-gray-50 dark:hover:bg-neutral-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700"
              disabled={isUpdating}
            >
              {isUpdating ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
