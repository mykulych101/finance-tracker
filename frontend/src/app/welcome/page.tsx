import Link from 'next/link';

const WelcomePage = () => {
  return (
    <div className="min-h-screen">
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-md dark:shadow-neutral-900/50 p-8">
          {/* Hero Section */}
          <div className="text-center mb-8">
            <div className="text-6xl mb-4">📈</div>
            <h1 className="text-4xl font-bold text-gray-800 dark:text-neutral-200 mb-4">Welcome to Personal Finance Tracker</h1>
            <p className="text-xl text-gray-600 dark:text-neutral-400 max-w-2xl mx-auto">
              Take control of your finances with a simple, private, and secure balance sheet tracker
              that keeps all your data local to your browser.
            </p>
          </div>



          {/* Getting Started Steps */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-neutral-200 mb-6 text-center">🚀 Getting Started in 3 Easy Steps</h2>
            <div className="grid md:grid-cols-3 gap-6">
              {/* Step 1 */}
              <div className="bg-blue-50 dark:bg-blue-900/30 rounded-lg p-6 text-center">
                <div className="text-3xl mb-4">1️⃣</div>
                <h3 className="text-lg font-semibold text-blue-800 dark:text-blue-300 mb-3">Add Your Accounts</h3>
                <p className="text-blue-700 dark:text-blue-400 mb-4">
                  Create accounts for your assets (savings, investments), liabilities (loans, credit cards),
                  and equity to build your financial picture.
                </p>
                <Link
                  href="/add-account"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors inline-block"
                >
                  Add Account
                </Link>
              </div>

              {/* Step 2 */}
              <div className="bg-green-50 dark:bg-green-900/30 rounded-lg p-6 text-center">
                <div className="text-3xl mb-4">2️⃣</div>
                <h3 className="text-lg font-semibold text-green-800 dark:text-green-300 mb-3">Record Balances</h3>
                <p className="text-green-700 dark:text-green-400 mb-4">
                  Enter current balances for all your accounts. You can update these regularly
                  to track your progress over time.
                </p>
                <Link
                  href="/record-balances"
                  className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors inline-block"
                >
                  Record Balances
                </Link>
              </div>

              {/* Step 3 */}
              <div className="bg-purple-50 dark:bg-purple-900/30 rounded-lg p-6 text-center">
                <div className="text-3xl mb-4">3️⃣</div>
                <h3 className="text-lg font-semibold text-purple-800 dark:text-purple-300 mb-3">Track Progress</h3>
                <p className="text-purple-700 dark:text-purple-400 mb-4">
                  View your balance sheet and historical tracking to see your net worth
                  and financial progress over time.
                </p>
                <Link
                  href="/historical"
                  className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors inline-block"
                >
                  View Tracking
                </Link>
              </div>
            </div>
          </section>

          {/* Features Overview */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-neutral-200 mb-6 text-center">✨ Key Features</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-start">
                  <span className="text-2xl mr-3 mt-1">📊</span>
                  <div>
                    <h3 className="font-semibold text-gray-800 dark:text-neutral-200">Balance Sheet View</h3>
                    <p className="text-gray-600 dark:text-neutral-400">See all your assets, liabilities, and net worth at a glance</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="text-2xl mr-3 mt-1">📈</span>
                  <div>
                    <h3 className="font-semibold text-gray-800 dark:text-neutral-200">Historical Tracking</h3>
                    <p className="text-gray-600 dark:text-neutral-400">Track your financial progress with charts and trends over time</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="text-2xl mr-3 mt-1">💰</span>
                  <div>
                    <h3 className="font-semibold text-gray-800 dark:text-neutral-200">Multiple Account Types</h3>
                    <p className="text-gray-600 dark:text-neutral-400">Support for various asset and liability categories</p>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex items-start">
                  <span className="text-2xl mr-3 mt-1">📤</span>
                  <div>
                    <h3 className="font-semibold text-gray-800 dark:text-neutral-200">Data Export/Import</h3>
                    <p className="text-gray-600 dark:text-neutral-400">Backup and restore your data with easy export/import tools</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="text-2xl mr-3 mt-1">🔒</span>
                  <div>
                    <h3 className="font-semibold text-gray-800 dark:text-neutral-200">Complete Privacy</h3>
                    <p className="text-gray-600 dark:text-neutral-400">All data stored locally - no servers, no tracking, no accounts</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="text-2xl mr-3 mt-1">📱</span>
                  <div>
                    <h3 className="font-semibold text-gray-800 dark:text-neutral-200">Mobile Friendly</h3>
                    <p className="text-gray-600 dark:text-neutral-400">Works perfectly on desktop, tablet, and mobile devices</p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Account Categories Guide */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-neutral-200 mb-6 text-center">📝 Account Categories Guide</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-green-50 dark:bg-green-900/30 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-green-800 dark:text-green-300 mb-3">💚 Assets</h3>
                <p className="text-green-700 dark:text-green-400 text-sm mb-3">Things you own that have value:</p>
                <ul className="text-green-700 dark:text-green-400 text-sm space-y-1">
                  <li>• Cash & Savings Accounts</li>
                  <li>• Investment Accounts</li>
                  <li>• Real Estate</li>
                  <li>• Personal Property</li>
                  <li>• Retirement Accounts</li>
                </ul>
              </div>
              <div className="bg-red-50 dark:bg-red-900/30 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-red-800 dark:text-red-300 mb-3">❤️ Liabilities</h3>
                <p className="text-red-700 dark:text-red-400 text-sm mb-3">Money you owe to others:</p>
                <ul className="text-red-700 dark:text-red-400 text-sm space-y-1">
                  <li>• Credit Card Debt</li>
                  <li>• Student Loans</li>
                  <li>• Car Loans</li>
                  <li>• Mortgages</li>
                  <li>• Personal Loans</li>
                </ul>
              </div>
              <div className="bg-blue-50 dark:bg-blue-900/30 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-blue-800 dark:text-blue-300 mb-3">💙 Equity</h3>
                <p className="text-blue-700 dark:text-blue-400 text-sm mb-3">Your net worth calculation:</p>
                <ul className="text-blue-700 dark:text-blue-400 text-sm space-y-1">
                  <li>• Total Assets minus Liabilities</li>
                  <li>• Automatically calculated</li>
                  <li>• Track wealth building progress</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Important Tips */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-neutral-200 mb-6 text-center">💡 Important Tips</h2>
            <div className="bg-yellow-50 dark:bg-yellow-900/30 border border-yellow-200 dark:border-yellow-800 rounded-md p-6">
              <ul className="space-y-3 text-yellow-800 dark:text-yellow-300">
                <li className="flex items-start">
                  <span className="font-bold mr-2">💾</span>
                  <span><strong>Regular Backups:</strong> Export your data regularly using the Settings page to prevent data loss.</span>
                </li>
                <li className="flex items-start">
                  <span className="font-bold mr-2">🔄</span>
                  <span><strong>Update Regularly:</strong> Record new balances monthly or quarterly to track your progress.</span>
                </li>
                <li className="flex items-start">
                  <span className="font-bold mr-2">🎯</span>
                  <span><strong>Be Accurate:</strong> Use actual account balances for the most useful financial picture.</span>
                </li>
                <li className="flex items-start">
                  <span className="font-bold mr-2">📱</span>
                  <span><strong>Browser Specific:</strong> Data is tied to this specific browser - bookmark this site!</span>
                </li>
              </ul>
            </div>
          </section>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 pt-6 border-t border-gray-200 dark:border-neutral-700">
            <Link
              href="/add-account"
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md font-medium transition-colors text-center flex-1"
            >
              🚀 Start by Adding an Account
            </Link>
            <Link
              href="/"
              className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-md font-medium transition-colors text-center"
            >
              📊 View Balance Sheet
            </Link>
            <Link
              href="/disclaimer"
              className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-md font-medium transition-colors text-center"
            >
              📋 Read Disclaimer
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomePage;
