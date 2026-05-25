import { SortDir, TransactionSortField } from '@/types/transactions';

interface SortIconProps {
  field: TransactionSortField;
  activeField: TransactionSortField | null;
  direction: SortDir;
}

export const SortIcon = ({ field, activeField, direction }: SortIconProps) => {
  if (activeField !== field)
    return <span className="ml-1 text-gray-300 dark:text-neutral-600">↕</span>;
  return <span className="ml-1">{direction === 'asc' ? '↑' : '↓'}</span>;
};
