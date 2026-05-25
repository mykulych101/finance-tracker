import { TransactionsListApiArg } from '@/redux/api';

type OrderingValue = NonNullable<TransactionsListApiArg['ordering']>[number];
export type TransactionSortField = Exclude<OrderingValue, `-${string}`>;
export type SortDir = 'asc' | 'desc';

export interface TransactionSort {
  field: TransactionSortField;
  dir: SortDir;
}
