'use client';

import { useRegisterCreateMutation, UserWrite } from '@/redux/api';
import Link from 'next/link';
import { useForm, SubmitHandler } from 'react-hook-form';
import { toast } from 'sonner';


export default function SignupPage() {
  const [signup, { isLoading }] = useRegisterCreateMutation()


  const { register, handleSubmit } = useForm<UserWrite>()

  const onSubmit: SubmitHandler<UserWrite> = (data) => {
    signup({ user: data }).unwrap().then(() => { }).catch(error => {
      toast.error(JSON.stringify(error))
    })
  }

  return (
    <div className="flex items-center justify-center">
      <div className="w-full max-w-md">
        <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-md dark:shadow-neutral-900/50 p-8">
          <div className="text-center mb-8">
            <div className="text-5xl mb-3">📈</div>
            <h1 className="text-2xl font-bold text-gray-800 dark:text-neutral-100">Create account</h1>
            <p className="text-sm text-gray-500 dark:text-neutral-400 mt-1">Personal Finance Tracker</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-2">
                Name
              </label>
              <input
                id="name"
                type="text"
                className="w-full px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-neutral-700 text-gray-900 dark:text-neutral-100"
                placeholder="John Doe"
                required
                autoComplete="name"
                {...register('name')}
              />
            </div>

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
                autoComplete="new-password"
                {...register('password')}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Creating account…' : 'Create account'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 dark:text-neutral-400 mt-6">
            Already have an account?{' '}
            <Link href="/login" className="text-blue-600 dark:text-blue-400 hover:underline font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
