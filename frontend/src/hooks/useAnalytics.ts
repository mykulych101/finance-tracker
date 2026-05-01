'use client';

type GtagConfig = {
  page_path?: string;
  page_title?: string;
  page_location?: string;
  custom_map?: Record<string, string>;
  [key: string]: string | number | boolean | undefined | Record<string, string>;
};

declare global {
  interface Window {
    gtag: (
      command: 'config' | 'event' | 'js',
      targetId: string | Date,
      config?: GtagConfig
    ) => void;
  }
}

export const useAnalytics = () => {
  const trackEvent = (
    eventName: string,
    parameters?: GtagConfig
  ) => {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', eventName, parameters);
    }
  };

  const trackPageView = (url: string) => {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('config', process.env.NEXT_PUBLIC_GA_TRACKING_ID || '', {
        page_path: url,
      });
    }
  };

  return {
    trackEvent,
    trackPageView,
  };
};
