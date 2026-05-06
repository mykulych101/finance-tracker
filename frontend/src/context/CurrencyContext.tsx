'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

export interface Currency {
  code: string;
  name: string;
  symbol: string;
  locale: string;
}

export const SUPPORTED_CURRENCIES: Currency[] = [
  { code: 'USD', name: 'US Dollar', symbol: '$', locale: 'en-US' },
  { code: 'GBP', name: 'British Pound', symbol: '£', locale: 'en-GB' },
  { code: 'EUR', name: 'Euro', symbol: '€', locale: 'en-EU' },
  { code: 'JPY', name: 'Japanese Yen', symbol: '¥', locale: 'ja-JP' },
  { code: 'CAD', name: 'Canadian Dollar', symbol: 'C$', locale: 'en-CA' },
  { code: 'AUD', name: 'Australian Dollar', symbol: 'A$', locale: 'en-AU' },
  { code: 'CHF', name: 'Swiss Franc', symbol: 'CHF', locale: 'de-CH' },
  { code: 'CNY', name: 'Chinese Yuan', symbol: '¥', locale: 'zh-CN' },
  { code: 'INR', name: 'Indian Rupee', symbol: '₹', locale: 'en-IN' },
  { code: 'KRW', name: 'South Korean Won', symbol: '₩', locale: 'ko-KR' },
];

interface CurrencyContextType {
  selectedCurrency: Currency;
  setSelectedCurrency: (currency: Currency) => void;
  formatCurrency: (amount: number) => string;
}

const CurrencyContext = createContext<CurrencyContextType | undefined>(undefined);

export const useCurrency = () => {
  const context = useContext(CurrencyContext);
  if (!context) {
    throw new Error('useCurrency must be used within a CurrencyProvider');
  }
  return context;
};

export const CurrencyProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [selectedCurrency, setSelectedCurrencyState] = useState<Currency>(SUPPORTED_CURRENCIES[1]); // Default to GBP

  // Load currency preference from localStorage on mount
  useEffect(() => {
    const savedCurrencyCode = localStorage.getItem('finance-currency');
    if (savedCurrencyCode) {
      const savedCurrency = SUPPORTED_CURRENCIES.find(currency => currency.code === savedCurrencyCode);
      if (savedCurrency) {
        setSelectedCurrencyState(savedCurrency);
      }
    }
  }, []);

  // Save to localStorage whenever currency changes
  const setSelectedCurrency = (currency: Currency) => {
    setSelectedCurrencyState(currency);
    localStorage.setItem('finance-currency', currency.code);
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat(selectedCurrency.locale, {
      style: 'currency',
      currency: selectedCurrency.code,
    }).format(amount);
  };

  return (
    <CurrencyContext.Provider
      value={{
        selectedCurrency,
        setSelectedCurrency,
        formatCurrency,
      }}
    >
      {children}
    </CurrencyContext.Provider>
  );
};
