'use client';

import Settings from '@/components/Settings';
import ProtectedRoute from '@/components/ProtectedRoute';

const SettingsPage = () => {
  return (
    <ProtectedRoute>
      <div className="min-h-screen">
        <div className="max-w-4xl mx-auto p-6">
          <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-md dark:shadow-neutral-900/50 p-6">
            <h1 className="text-3xl font-bold text-gray-800 dark:text-neutral-200 mb-6">Settings</h1>
            <Settings />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default SettingsPage;
