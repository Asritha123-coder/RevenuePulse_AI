import React from 'react';
import { Search, Bell, Moon, Sun, Menu } from 'lucide-react';
import { useTheme } from '@/context/ThemeContext';
import { useAuth } from '@/context/AuthContext';

export function Header() {
  const { theme, setTheme } = useTheme();
  const { user } = useAuth();

  return (
    <header className="h-16 border-b bg-card flex items-center justify-between px-4 lg:px-8 z-10 sticky top-0">
      <div className="flex items-center gap-4 flex-1">
        <button className="md:hidden text-slate-500 dark:text-slate-400 hover:text-foreground">
          <Menu className="w-6 h-6" />
        </button>
        
        {/* Global Search */}
        <div className="hidden sm:flex items-center relative w-full max-w-md">
          <Search className="w-4 h-4 absolute left-3 text-slate-400 dark:text-slate-400" />
          <input 
            type="text"
            placeholder="Search accounts, campaigns, or ask AI..."
            className="w-full pl-9 pr-4 py-2 bg-slate-100 dark:bg-slate-800 border-transparent rounded-md text-sm focus:bg-transparent focus:border-brand-500 focus:ring-2 focus:ring-brand-500 transition-all outline-none"
          />
          <div className="absolute right-3 flex items-center gap-1 text-xs text-slate-400 dark:text-slate-400 font-medium">
            <kbd className="px-1.5 py-0.5 bg-slate-200 dark:bg-slate-700 rounded">Ctrl</kbd>
            <span>+</span>
            <kbd className="px-1.5 py-0.5 bg-slate-200 dark:bg-slate-700 rounded">K</kbd>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Theme Toggle */}
        <button 
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 transition-colors"
        >
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>

        {/* Notifications */}
        <button className="relative p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full border-2 border-card"></span>
        </button>

        {/* Profile */}
        <div className="flex items-center gap-3 pl-4 border-l border-border cursor-pointer">
          <div className="hidden md:flex flex-col items-end">
            <span className="text-sm font-medium leading-none">{user?.name}</span>
            <span className="text-xs text-slate-500 dark:text-slate-400 mt-1">{user?.role}</span>
          </div>
          <img 
            src={user?.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=Admin`} 
            alt="Profile" 
            className="w-8 h-8 rounded-full border bg-slate-100 dark:bg-slate-800"
          />
        </div>
      </div>
    </header>
  );
}
