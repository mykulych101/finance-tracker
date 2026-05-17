'use client';

import { MyTokenObtainPairWrite, useLoginCreateMutation } from '@/redux/api';
import Image from 'next/image';
import Link from 'next/link';
import { useForm, SubmitHandler } from 'react-hook-form';
import { toast } from 'sonner';
import PublicOnlyRoute from '@/components/PublicOnlyRoute';

export default function LoginPage() {
  const [login, { isLoading }] = useLoginCreateMutation()

  const { register, handleSubmit } = useForm<MyTokenObtainPairWrite>()

  const onSubmit: SubmitHandler<MyTokenObtainPairWrite> = (data) => {
    login({ myTokenObtainPair: data }).unwrap().then(() => { }).catch(error => {
      toast.error(JSON.stringify(error))
    })
  }

  return (
    <PublicOnlyRoute>
    <div className="flex items-center justify-center">
      <div className="w-full max-w-md">
        <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-md dark:shadow-neutral-900/50 p-8">
          <div className="text-center mb-8">
            <Image src="/logo.svg" width={60} height={60} alt="Finance tracker" className="mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-800 dark:text-neutral-100">Sign in</h1>
            <p className="text-sm text-gray-500 dark:text-neutral-400 mt-1">Personal Finance Tracker</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                className="w-full px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100"
                placeholder="you@example.com"
                required
                autoComplete="email"
                {...register('email')}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                className="w-full px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100"
                placeholder="••••••••"
                required
                autoComplete="current-password"
                {...register('password')}
              />
            </div>


            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 dark:text-neutral-400 mt-6">
            Don&apos;t have an account?{' '}
            <Link href="/signup" className="text-blue-600 dark:text-blue-400 hover:underline font-medium">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
    </PublicOnlyRoute>
  );
}
