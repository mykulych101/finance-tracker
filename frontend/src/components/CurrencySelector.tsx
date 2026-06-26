'use client';

import React from 'react';
import { useAppDispatch, useAppSelector } from '@/redux/hooks';
import { setConvertTo } from '@/redux/currencySlice';
import type { CurrencyEnum } from '@/redux/api';
import { useAnalytics } from '@/hooks/useAnalytics';

interface CurrencySelectorProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export const CURRENCY_SYMBOLS: Record<CurrencyEnum, string> = {
  USD: '$',
  EUR: '€',
  UAH: '₴',
};

const CURRENCY_OPTIONS: CurrencyEnum[] = ['USD', 'EUR', 'UAH'];

export const CurrencySelector: React.FC<CurrencySelectorProps> = ({
  className = '',
  size = 'md',
  showLabel = true
}) => {
  const dispatch = useAppDispatch();
  const convertTo = useAppSelector(state => state.currency.convertTo);
  const { trackEvent } = useAnalytics();

  const sizeClasses = {
    sm: 'px-2 py-1 text-sm',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-3 text-base'
  };

  const handleChange = (value: string) => {
    const next = value === '' ? null : value as CurrencyEnum;
    trackEvent('currency_changed', {
      from_currency: convertTo ?? 'default',
      to_currency: next ?? 'default',
    });
    dispatch(setConvertTo(next));
  };

  return (
    <div className={`flex flex-col ${className}`}>
      {showLabel && (
        <label htmlFor="currency-select" className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-1">
          Currency
        </label>
      )}
      <select
        id="currency-select"
        value={convertTo ?? ''}
        onChange={(e) => handleChange(e.target.value)}
        className={`
          ${sizeClasses[size]}
          border border-gray-300 dark:border-neutral-600 rounded-md shadow-sm
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100
        `}
      >
        <option value="">Default</option>
        {CURRENCY_OPTIONS.map((currency) => (
          <option key={currency} value={currency}>
            {CURRENCY_SYMBOLS[currency]} {currency}
          </option>
        ))}
      </select>
    </div>
  );
};
