'use client';

import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';

const DisclaimerPage = () => {
  const { isAuthConfigured } = useAuth();
  return (
    <div className="min-h-screen">
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-md dark:shadow-neutral-900/50 p-8">
          <h1 className="text-3xl font-bold text-gray-800 dark:text-neutral-200 mb-6">📋 Privacy Policy & Disclaimer</h1>

          {/* Privacy First Banner */}
          <div className="bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-md p-6 mb-8">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <span className="text-2xl">🔒</span>
              </div>
              <div className="ml-3">
                <h2 className="text-lg font-medium text-green-800 dark:text-green-300">Your Data Stays Private</h2>
                <p className="mt-2 text-green-700 dark:text-green-400">
                  Your financial data is <strong>never sold or shared</strong> with third parties. You have complete control
                  over whether to store your data locally only or enable cloud sync for convenience.
                </p>
              </div>
            </div>
          </div>

          {/* Account Requirement */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-neutral-200 mb-4">👤 Account & Authentication</h2>
            <div className="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-md p-6">
              <p className="text-blue-700 dark:text-blue-300 mb-4">
                All users are required to create an account to use this application. We use <strong>Auth0</strong> for
                secure authentication, which provides:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 text-blue-700 dark:text-blue-300">
                <li>Industry-standard security and encryption</li>
                <li>Secure login and session management</li>
                <li>Multi-factor authentication options</li>
                <li>OAuth integration with Google, GitHub, and other providers</li>
                <li>No storage of passwords on our servers</li>
              </ul>
            </div>
          </section>

          {/* Data Storage Options */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-neutral-200 mb-4">💾 Data Storage Options</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-orange-50 dark:bg-orange-900/30 rounded-lg p-4">
                <h3 className="font-semibold text-orange-800 dark:text-orange-300 mb-2">🏠 Local Storage Only</h3>
                <ul className="text-sm text-orange-700 dark:text-orange-400 space-y-1">
                  <li>• Data stored only in your browser</li>
                  <li>• Never transmitted to our servers</li>
                  <li>• Maximum privacy and control</li>
                  <li>• No cross-device sync</li>
                  <li>• Risk of data loss if browser data cleared</li>
                </ul>
              </div>
              <div className="bg-purple-50 dark:bg-purple-900/30 rounded-lg p-4">
                <h3 className="font-semibold text-purple-800 dark:text-purple-300 mb-2">☁️ Cloud Sync (Optional)</h3>
                <ul className="text-sm text-purple-700 dark:text-purple-400 space-y-1">
                  <li>• Secure cloud backup via MongoDB</li>
                  <li>• Sync across multiple devices</li>
                  <li>• Encrypted data transmission</li>
                  <li>• Hosted on secure AWS infrastructure</li>
                  <li>• Can be disabled at any time</li>
                </ul>
              </div>
            </div>
            <div className="mt-4 p-4 bg-gray-50 dark:bg-neutral-700 rounded-lg">
              <p className="text-gray-700 dark:text-neutral-400 text-sm">
                <strong>Your Choice:</strong> You can enable or disable cloud sync in the Settings page at any time.
                When disabled, your data remains local only. When enabled, your encrypted financial data is stored
                securely in our MongoDB database hosted on AWS.
              </p>
            </div>
          </section>

          {/* Data Protection */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-neutral-200 mb-4">🛡️ Data Protection & Security</h2>
            <div className="space-y-4">
              <div className="bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-md p-4">
                <h3 className="font-semibold text-green-800 dark:text-green-300 mb-2">✅ Our Commitments</h3>
                <ul className="text-green-700 dark:text-green-400 space-y-1 text-sm">
                  <li>• <strong>Never sell or share</strong> your financial data with third parties</li>
                  <li>• <strong>Encryption in transit</strong> - all data transmitted securely via HTTPS</li>
                  <li>• <strong>Encryption at rest</strong> - cloud data encrypted in MongoDB</li>
                  <li>• <strong>AWS security</strong> - leveraging enterprise-grade infrastructure</li>
                  <li>• <strong>Minimal data collection</strong> - only financial data you explicitly enter</li>
                </ul>
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-md p-4">
                <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">🏗️ Technical Infrastructure</h3>
                <ul className="text-blue-700 dark:text-blue-300 space-y-1 text-sm">
                  <li>• <strong>Auth0:</strong> Secure authentication and user management</li>
                  <li>• <strong>MongoDB:</strong> Encrypted database storage for cloud sync</li>
                  <li>• <strong>AWS:</strong> Enterprise-grade cloud hosting with security compliance</li>
                  <li>• <strong>HTTPS/TLS:</strong> All connections encrypted in transit</li>
                  <li>• <strong>Local Storage:</strong> Browser-based storage when cloud sync disabled</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Data You Control */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-neutral-200 mb-4">📊 What Data We Store</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-gray-800 dark:text-neutral-200 mb-3">Account Information</h3>
                <ul className="text-gray-700 dark:text-neutral-400 space-y-1 text-sm">
                  <li>• Email address (via Auth0)</li>
                  <li>• User ID (for data association)</li>
                  <li>• Authentication tokens</li>
                  <li>• Account preferences</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-gray-800 dark:text-neutral-200 mb-3">Financial Data (Optional Cloud)</h3>
                <ul className="text-gray-700 dark:text-neutral-400 space-y-1 text-sm">
                  <li>• Account names and types you create</li>
                  <li>• Balance amounts you enter</li>
                  <li>• Transaction dates you record</li>
                  <li>• Currency preferences</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Your Rights */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-neutral-200 mb-4">⚖️ Your Rights & Control</h2>
            <div className="bg-yellow-50 dark:bg-yellow-900/30 border border-yellow-200 dark:border-yellow-800 rounded-md p-6">
              <h3 className="font-medium text-yellow-800 dark:text-yellow-300 mb-3">You have complete control over your data:</h3>
              <ul className="space-y-2 text-yellow-700 dark:text-yellow-400">
                <li className="flex items-start">
                  <span className="font-bold mr-2">•</span>
                  <span><strong>Export:</strong> Download all your data at any time</span>
                </li>
                <li className="flex items-start">
                  <span className="font-bold mr-2">•</span>
                  <span><strong>Delete:</strong> Remove all cloud data from our servers</span>
                </li>
                <li className="flex items-start">
                  <span className="font-bold mr-2">•</span>
                  <span><strong>Local Only:</strong> Disable cloud sync to keep data browser-only</span>
                </li>
              </ul>
            </div>
          </section>

          {/* Important Limitations */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-neutral-200 mb-4">⚠️ Important Limitations</h2>
            <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-md p-6">
              <h3 className="font-medium text-red-800 dark:text-red-300 mb-3">Please be aware of these limitations:</h3>
              <ul className="space-y-2 text-red-700 dark:text-red-400">
                <li className="flex items-start">
                  <span className="font-bold mr-2">•</span>
                  <span><strong>Local Data Risk:</strong> Without cloud sync, clearing browser data will delete your local data.</span>
                </li>
                <li className="flex items-start">
                  <span className="font-bold mr-2">•</span>
                  <span><strong>No Financial Advice:</strong> This tool is for tracking only, not professional financial guidance.</span>
                </li>
                <li className="flex items-start">
                  <span className="font-bold mr-2">•</span>
                  <span><strong>Data Accuracy:</strong> You are responsible for the accuracy of data you enter.</span>
                </li>
                <li className="flex items-start">
                  <span className="font-bold mr-2">•</span>
                  <span><strong>Service Availability:</strong> While we strive for 100% uptime, occasional maintenance may occur.</span>
                </li>
              </ul>
            </div>
          </section>

          {/* Best Practices */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-neutral-200 mb-4">💡 Best Practices</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-gray-800 dark:text-neutral-200 mb-3">📤 Data Backup</h3>
                <ul className="text-gray-700 dark:text-neutral-400 space-y-1">
                  <li>• Export your data regularly</li>
                  <li>• Store backups in a safe location</li>
                  <li>• Consider enabling cloud sync for automatic backup</li>
                  <li>• Test import functionality occasionally</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-gray-800 dark:text-neutral-200 mb-3">🔐 Account Security</h3>
                <ul className="text-gray-700 dark:text-neutral-400 space-y-1">
                  <li>• Enable multi-factor authentication</li>
                  <li>• Use a strong, unique password</li>
                  <li>• Log out on shared devices</li>
                  <li>• Keep your email account secure</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Legal Disclaimer */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-neutral-200 mb-4">⚖️ Legal Disclaimer</h2>
            <div className="bg-gray-50 dark:bg-neutral-700 rounded-lg p-6 text-sm text-gray-700 dark:text-neutral-400">
              <p className="mb-4">
                This tool is provided &quot;as is&quot; for personal use. While we&apos;ve designed it with privacy and security in mind:
              </p>
              <ul className="space-y-2 list-disc list-inside">
                <li>This is not professional financial advice</li>
                <li>Users are responsible for data accuracy and backups</li>
                <li>No warranty is provided for data integrity or availability</li>
                <li>Use at your own risk and discretion</li>
                <li>Not intended for commercial or business accounting</li>
                <li>We reserve the right to update this privacy policy with notice</li>
              </ul>
            </div>
          </section>

          {/* Contact & Support */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-neutral-200 mb-4">📞 Questions or Data Requests?</h2>
            <div className="bg-blue-50 dark:bg-blue-900/30 rounded-lg p-6">
              <p className="text-blue-700 dark:text-blue-300 mb-4">
                For data deletion requests, privacy questions, or technical support:
              </p>
              <ul className="text-blue-700 dark:text-blue-300 space-y-2">
                <li>• Use the Settings page for data export/import/deletion</li>
                <li>• Check browser console for technical error messages</li>
                <li>• Contact support for account or privacy-related questions</li>
                <li>• Review this page for updates to our privacy practices</li>
              </ul>
            </div>
          </section>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 pt-6 border-t border-gray-200 dark:border-neutral-700">
            <Link
              href="/"
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md font-medium transition-colors text-center"
            >
              🏠 Go to Balance Sheet
            </Link>
            <Link
              href="/settings"
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-md font-medium transition-colors text-center"
            >
              ⚙️ Go to Settings
            </Link>
            {isAuthConfigured && (
              <Link
                href="/auth/login?screen_hint=signup"
                className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-md font-medium transition-colors text-center"
              >
                🔐 Login / Register
              </Link>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DisclaimerPage;
