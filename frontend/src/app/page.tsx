'use client';

import { BalanceSheet } from "@/components/BalanceSheet";
import ClientOnly from "@/components/ClientOnly";

export default function Home() {

  return (
    <div>
      <ClientOnly
        fallback={
          <div className="max-w-4xl mx-auto">
            <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-lg dark:shadow-neutral-900/50 p-6">
              <div className="text-center py-12">
                <div className="text-gray-500 dark:text-neutral-400 text-lg mb-4">Loading...</div>
                <p className="text-gray-400 dark:text-neutral-500">Please wait while we load your financial data.</p>
              </div>
            </div>
          </div>
        }
      >
        <BalanceSheet />
      </ClientOnly>
    </div>
  );
}
