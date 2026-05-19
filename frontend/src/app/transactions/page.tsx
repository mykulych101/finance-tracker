'use client';

import ProtectedRoute from '@/components/ProtectedRoute';
import { Transactions } from '@/components/Transactions';

export default function TransactionsPage() {
  return (
    <ProtectedRoute>
      <Transactions />
    </ProtectedRoute>
  );
}
