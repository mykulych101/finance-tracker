'use client';

import { createContext, useContext, ReactNode } from 'react';
import { useAppSelector } from '@/redux/hooks';

interface AuthContextType {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  user: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  error: any;
  isLoading: boolean;
  isAuthConfigured: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  return (
      <AuthContextWrapper>{children}</AuthContextWrapper>
  );
}

function AuthContextWrapper({ children }: { children: ReactNode }) {
  const { user } = useAppSelector((state) => state.auth);

  return (
    <AuthContext.Provider value={{ user, error: null, isLoading: false, isAuthConfigured: true }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
