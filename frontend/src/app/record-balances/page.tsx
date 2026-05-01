'use client';

import { RecordBalances } from '@/components/RecordBalances';
import ProtectedRoute from '@/components/ProtectedRoute';

export default function RecordBalancesPage() {
  return (
    <ProtectedRoute>
      <div>
        <RecordBalances />
      </div>
    </ProtectedRoute>
  );
}
