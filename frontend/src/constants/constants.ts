import { CurrencyEnum } from "@/redux/api";

export const allPages = 1000
export const SEARCH_DEBOUNCE_MS = 300

export const CURRENCY_SYMBOLS: Record<CurrencyEnum, string> = {
  USD: '$',
  EUR: '€',
  UAH: '₴',
};
