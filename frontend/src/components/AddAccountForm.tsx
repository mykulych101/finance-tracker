'use client';

// import { useFinance } from '@/context/FinanceContext';
import { useAnalytics } from '@/hooks/useAnalytics';
import { useForm } from 'react-hook-form';
import { Account, useAccountsCreateMutation } from '@/redux/api';
import { ACCOUNT_TYPES, ACCOUNT_CATEGORIES, CURRENCY_OPTIONS } from '@/constants/financeConstants';
import { toast } from 'sonner';
import { useEffect } from 'react';

export const AddAccountForm = () => {
  const { trackEvent } = useAnalytics();
  const [addAccount, { isLoading }] = useAccountsCreateMutation();
  const { register, handleSubmit, watch, reset, setValue } = useForm<Account>()
  const selectedType = watch('type', 'asset')
  const selectedCategory = watch('category')

  useEffect(() => {
    setValue('category', ACCOUNT_CATEGORIES[selectedType][0]);
  }, [selectedType, setValue]);

  const onSubmit = (values: Account) => {
    addAccount({
      writeAccount: values
    }).unwrap()
      .then(() => {
        toast.success('Account added successfully!');
        // Track account creation
        trackEvent('account_created', {
          account_type: values.type,
          account_category: values.category,
        });
      }).catch(error => toast.error(JSON.stringify(error)))

    reset();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="accountName" className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-2">
          Account Name
        </label>
        <input
          type="text"
          id="accountName"
          {...register('name', { required: true })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100"
          placeholder="e.g., Checking Account, Credit Card, etc."
        />
      </div>

      <div>
        <label htmlFor="accountType" className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-2">
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
        <label htmlFor="accountCategory" className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-2">
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
        <label htmlFor="accountCurrency" className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-2">
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
          <label htmlFor="creditLimit" className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-2">
            Credit Limit
          </label>
          <input
            type="number"
            id="creditLimit"
            {...register('credit_limit')}
            className="w-full px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100"
            placeholder="e.g., 5000"
          />
        </div>
      )}

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-800 transition-colors"
      >
        {isLoading ? 'Adding...' : 'Add Account'}
      </button>
    </form>
  );
};
