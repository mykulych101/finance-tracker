'use client';

import React from 'react';
import { useCurrency, SUPPORTED_CURRENCIES } from '@/context/CurrencyContext';
import { useAnalytics } from '@/hooks/useAnalytics';

interface CurrencySelectorProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export const CurrencySelector: React.FC<CurrencySelectorProps> = ({
  className = '',
  size = 'md',
  showLabel = true
}) => {
  const { selectedCurrency, setSelectedCurrency } = useCurrency();
  const { trackEvent } = useAnalytics();

  const sizeClasses = {
    sm: 'px-2 py-1 text-sm',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-3 text-base'
  };

  const handleCurrencyChange = (currencyCode: string) => {
    const currency = SUPPORTED_CURRENCIES.find(c => c.code === currencyCode);
    if (currency) {
      setSelectedCurrency(currency);
      // Track currency change
      trackEvent('currency_changed', {
        from_currency: selectedCurrency.code,
        to_currency: currency.code,
      });
    }
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
        value={selectedCurrency.code}
        onChange={(e) => handleCurrencyChange(e.target.value)}
        className={`
          ${sizeClasses[size]}
          border border-gray-300 dark:border-neutral-600 rounded-md shadow-sm
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100
          ${className}
        `}
      >
        {SUPPORTED_CURRENCIES.map((currency) => (
          <option key={currency.code} value={currency.code}>
            {currency.symbol} {currency.code} - {currency.name}
          </option>
        ))}
      </select>
    </div>
  );
};
