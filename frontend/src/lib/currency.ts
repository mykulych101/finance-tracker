// Legacy function for backward compatibility
export function formatCurrency(amount: number) {
  return new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: 'GBP',
  }).format(amount);
};

// Updated function that accepts currency parameters
export function formatCurrencyWithLocale(amount: number, currencyCode: string, locale: string) {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currencyCode,
  }).format(amount);
};
