'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useActivateRetrieveQuery } from '@/redux/api';

export default function ActivatePage() {
  const { uidb64, token } = useParams<{ uidb64: string; token: string }>();
  const { isLoading, isSuccess, isError } = useActivateRetrieveQuery({ uidb64, token });

  return (
    <div className="flex items-center justify-center">
      <div className="w-full max-w-md">
        <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-md dark:shadow-neutral-900/50 p-8 text-center">
          <div className="text-5xl mb-6">📈</div>

          {isLoading && (
            <>
              <h1 className="text-2xl font-bold text-gray-800 dark:text-neutral-100 mb-2">Activating your account…</h1>
              <p className="text-sm text-gray-500 dark:text-neutral-400">Please wait.</p>
            </>
          )}

          {/* TODO: If authenticated, redirect to dashboard */}
          {isSuccess && (
            <>
              <h1 className="text-2xl font-bold text-gray-800 dark:text-neutral-100 mb-2">Account activated!</h1>
              <p className="text-sm text-gray-500 dark:text-neutral-400 mb-6">You can now sign in to your account.</p>
              <Link
                href="/login"
                className="inline-block bg-blue-600 text-white py-2 px-6 rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                Sign in
              </Link>
            </>
          )}

          {isError && (
            <>
              <h1 className="text-2xl font-bold text-gray-800 dark:text-neutral-100 mb-2">Activation failed</h1>
              <p className="text-sm text-gray-500 dark:text-neutral-400 mb-6">This link is invalid or has already been used.</p>
              <Link
                href="/signup"
                className="inline-block bg-blue-600 text-white py-2 px-6 rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                Sign up again
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
