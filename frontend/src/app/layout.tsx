import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { FinanceProvider } from "@/context/FinanceContext";
import { CurrencyProvider } from "@/context/CurrencyContext";
import { ThemeProvider } from "@/context/ThemeContext";
import Navigation from "@/components/Navigation";
import ClientOnly from "@/components/ClientOnly";
import { GoogleAnalytics } from "@/components/GoogleAnalytics";
import { AppLoader, Loader } from "@/components/AppLoader";
import { StoreProvider } from "@/redux/StoreProvider";
import { Toaster } from "sonner"

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Personal Finance Tracker",
  description: "Track your personal finances with balance sheets and account management",
};

// Inline script to prevent flash of wrong theme on page load
const themeScript = `
  (function() {
    try {
      var theme = localStorage.getItem('finance-theme') || 'system';
      var isDark = theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
      if (isDark) document.documentElement.classList.add('dark');
    } catch(e) {}
  })();
`;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-white dark:bg-neutral-950 min-h-screen transition-colors duration-200`}
      >
        <GoogleAnalytics />
        <Toaster position="top-right" />
        <StoreProvider>
          <ClientOnly fallback={<Loader />}>
            <AppLoader>
              <CurrencyProvider>
                <FinanceProvider>
                  <ThemeProvider>
                    <Navigation />
                    <main className="py-8 px-4">
                      {children}
                    </main>
                  </ThemeProvider>
                </FinanceProvider>
              </CurrencyProvider>
            </AppLoader>
          </ClientOnly>
        </StoreProvider>
      </body>
    </html>
  );
}
