'use client';

import { HistoricalTracking } from '@/components/HistoricalTracking';
import ProtectedRoute from '@/components/ProtectedRoute';

export default function HistoricalPage() {
  return (
    <ProtectedRoute>
      <div>
        <HistoricalTracking />
      </div>
    </ProtectedRoute>
  );
}
