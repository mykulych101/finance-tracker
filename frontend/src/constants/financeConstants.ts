import { AccountTypeEnum, CategoryEnum, CurrencyEnum } from '@/redux/api';

export const ACCOUNT_TYPES: AccountTypeEnum[] = ['asset', 'liability', 'equity'];
export type ACCOUNT_CATEGORIES_TYPE = Record<AccountTypeEnum, CategoryEnum[]>;
export const ACCOUNT_CATEGORIES: ACCOUNT_CATEGORIES_TYPE = {
    asset: ['cash', 'investments', 'real_estate', 'crypto', 'other'],
    liability: ['credit_card', 'loan', 'mortgage', 'other'],
    equity: ['other'],
};
export const CURRENCY_OPTIONS: CurrencyEnum[] = ['USD', 'EUR', 'UAN'];
