'use client';

import { Suspense, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import CheckYourInbox from '@/components/CheckYourInbox';
import PublicOnlyRoute from '@/components/PublicOnlyRoute';

const CheckInbox = () => {
  const email = useSearchParams().get('email');
  const router = useRouter();

  useEffect(() => {
    if (!email) {
      router.replace('/signup');
    }
  }, [email, router]);

  if (!email) {
    return null;
  }

  return <CheckYourInbox email={email} />;
};

export default function CheckInboxPage() {
  return (
    <PublicOnlyRoute>
      <Suspense fallback={null}>
        <CheckInbox />
      </Suspense>
    </PublicOnlyRoute>
  );
}
