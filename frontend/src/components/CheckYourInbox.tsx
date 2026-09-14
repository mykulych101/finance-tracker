'use client';

import Link from 'next/link';

interface CheckYourInboxProps {
  email: string;
}

const CheckYourInbox = ({ email }: CheckYourInboxProps) => {
  return (
    <div className="flex items-center justify-center">
      <div className="w-full max-w-md">
        <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-md dark:shadow-neutral-900/50 p-8 text-center">
          <div className="text-5xl mb-6">📬</div>
          <h1 className="text-2xl font-bold text-gray-800 dark:text-neutral-100 mb-2">Check your inbox</h1>
          <p className="text-sm text-gray-500 dark:text-neutral-400">
            We sent an activation link to{' '}
            <span className="font-semibold text-gray-800 dark:text-neutral-200">{email}</span>.
            Open it to finish setting up your account.
          </p>
          <p className="text-center text-sm text-gray-500 dark:text-neutral-400 mt-6">
            Already activated?{' '}
            <Link href="/login" className="text-blue-600 dark:text-blue-400 hover:underline font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default CheckYourInbox;
