'use client';

import { type ReactNode } from 'react';
import { useProfileRetrieveQuery } from '@/redux/api';
import { useAppSelector } from '@/redux/hooks';

export function Loader() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white dark:bg-neutral-950">
      <p className="text-xl font-bold text-gray-800 dark:text-neutral-100 mb-8 tracking-tight">
        Personal Finance Tracker
      </p>

      <div className="flex items-end space-x-1.5 h-12">
        {[3, 5, 4, 7, 5, 6, 4, 7, 5, 3].map((height, i) => (
          <div
            key={i}
            className="w-2 bg-blue-500 dark:bg-blue-400 rounded-t-sm animate-pulse"
            style={{
              height: `${height * 6}px`,
              animationDelay: `${i * 80}ms`,
              animationDuration: '900ms',
            }}
          />
        ))}
      </div>

      <p className="text-sm text-gray-400 dark:text-neutral-500 mt-6">Loading your finances…</p>
    </div>
  );
}

export function AppLoader({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAppSelector((state) => state.auth);
  const { isLoading } = useProfileRetrieveQuery(undefined, { skip: !isAuthenticated });

  if (isLoading) return <Loader />;

  return <>{children}</>;
}
