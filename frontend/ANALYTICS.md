# Google Analytics Implementation

This project includes Google Analytics 4 (GA4) tracking to understand user behavior and improve the application.

## Setup

The Google Analytics tracking is configured via environment variables:

```env
# Required: Your Google Analytics tracking ID
NEXT_PUBLIC_GA_TRACKING_ID=G-SE8MSYP3FQ

# Optional: Explicitly enable/disable analytics (default: false)
NEXT_PUBLIC_ENABLE_ANALYTICS=true
```

**Note**: All environment variables that need to be available in the browser must be prefixed with `NEXT_PUBLIC_`. The `NODE_ENV` variable is a special exception that Next.js automatically makes available to the frontend.

## Implementation Details

### Components

- **GoogleAnalytics.tsx**: Main component that loads the Google Analytics scripts
- **useAnalytics.ts**: Custom hook for tracking events and page views

### Privacy & Security

- Analytics only loads in production environments
- Environment variables keep the tracking ID configurable
- No personal financial data is sent to Google Analytics

### Tracked Events

The following user interactions are tracked:

1. **Account Creation** (`account_created`)
   - `account_type`: The type of account (asset, liability, equity)
   - `account_category`: The category of the account

2. **Currency Changes** (`currency_changed`)
   - `from_currency`: Previous currency code
   - `to_currency`: New currency code

### Usage

To track custom events in your components:

```tsx
import { useAnalytics } from '@/hooks/useAnalytics';

const MyComponent = () => {
  const { trackEvent } = useAnalytics();

  const handleUserAction = () => {
    trackEvent('custom_event_name', {
      custom_parameter: 'value',
    });
  };

  return <button onClick={handleUserAction}>Click me</button>;
};
```

### Page View Tracking

Page views are automatically tracked by Google Analytics. For manual page view tracking:

```tsx
import { useAnalytics } from '@/hooks/useAnalytics';

const { trackPageView } = useAnalytics();
trackPageView('/custom-page');
```

## Development

During development, Google Analytics is disabled to avoid polluting production data. The tracking only activates when **ALL** of these conditions are met:

1. `NODE_ENV` is set to `'production'`
2. `NEXT_PUBLIC_GA_TRACKING_ID` environment variable is set
3. `NEXT_PUBLIC_ENABLE_ANALYTICS` is set to `'true'`

This multi-layer approach ensures you have full control over when analytics are active.

## Compliance

This implementation is designed to be privacy-friendly:

- No personal identifiable information (PII) is tracked
- Financial data remains local to the user's browser
- Only high-level usage patterns are collected
- Users can block tracking via browser settings or ad blockers
