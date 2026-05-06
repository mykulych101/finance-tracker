'use client';

import { useTheme, type Theme } from '@/context/ThemeContext';

const themes: { value: Theme; label: string; icon: string }[] = [
    { value: 'light', label: 'Light', icon: '☀️' },
    { value: 'dark', label: 'Dark', icon: '🌙' },
    { value: 'system', label: 'System', icon: '💻' },
];

interface ThemeToggleProps {
    className?: string;
}

export const ThemeToggle = ({ className = '' }: ThemeToggleProps) => {
    const { theme, setTheme } = useTheme();
    const current = themes.find((t) => t.value === theme) ?? themes[2];

    return (
        <div className={`relative inline-block ${className}`}>
            <div className="pointer-events-none absolute inset-y-0 left-3 flex items-center">
                <span>{current.icon}</span>
            </div>
            <select
                value={theme}
                onChange={(e) => setTheme(e.target.value as Theme)}
                aria-label="Color theme"
                className="appearance-none pl-9 pr-9 py-2 rounded-md border border-gray-300 dark:border-neutral-600
                    bg-white dark:bg-neutral-800 text-sm font-medium
                    text-gray-700 dark:text-neutral-200
                    focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
            >
                {themes.map((t) => (
                    <option key={t.value} value={t.value}>
                        {t.label}
                    </option>
                ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-gray-500 dark:text-neutral-400">
                <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
                </svg>
            </div>
        </div>
    );
};
