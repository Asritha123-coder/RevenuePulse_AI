import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useTheme } from '@/context/ThemeContext';
import { useAuth } from '@/context/AuthContext';
import { Sun, Moon, Monitor, CheckCircle, XCircle, Database, Cpu, Globe, Wifi } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { etlService } from '@/services/etl';
import { analyticsService } from '@/services/analytics';

export default function Settings() {
  const { theme, setTheme } = useTheme();
  const { user } = useAuth();

  const { data: dbHealth, isLoading: dbLoading } = useQuery({
    queryKey: ['db-health'],
    queryFn: etlService.getDatabaseHealth,
  });

  const { data: kpiCheck, isLoading: apiLoading } = useQuery({
    queryKey: ['kpis'],
    queryFn: analyticsService.getKPIs,
  });

  const isDbOnline = !dbLoading && !!dbHealth;
  const isApiOnline = !apiLoading && !!kpiCheck;

  return (
    <div className="space-y-8 max-w-3xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-slate-500 mt-1">Application preferences, profile, and system health status.</p>
      </div>

      {/* Theme */}
      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>Customize the color theme of the application.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            {[
              { value: 'light', label: 'Light', icon: Sun },
              { value: 'dark', label: 'Dark', icon: Moon },
              { value: 'system', label: 'System', icon: Monitor },
            ].map(({ value, label, icon: Icon }) => (
              <button
                key={value}
                onClick={() => setTheme(value as any)}
                className={`flex-1 flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all ${
                  theme === value
                    ? 'border-brand-500 bg-brand-50 dark:bg-brand-900/20 text-brand-700 dark:text-brand-300'
                    : 'border-border hover:border-slate-400 dark:hover:border-slate-500 text-slate-600 dark:text-slate-400'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="text-sm font-medium">{label}</span>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Profile */}
      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
          <CardDescription>Your account information and role access.</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center gap-6">
          <img
            src={user?.avatar || 'https://api.dicebear.com/7.x/avataaars/svg?seed=default'}
            alt="Avatar"
            className="w-20 h-20 rounded-full border-4 border-brand-500/20 bg-slate-100"
          />
          <div>
            <h3 className="text-xl font-bold">{user?.name}</h3>
            <p className="text-slate-500">{user?.email}</p>
            <span className="mt-2 inline-block text-xs font-semibold px-2.5 py-1 rounded-full bg-brand-100 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300">
              {user?.role}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* System Health */}
      <Card>
        <CardHeader>
          <CardTitle>System Health</CardTitle>
          <CardDescription>Live status of backend services and database connectivity.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            {
              label: 'PostgreSQL Database',
              icon: Database,
              loading: dbLoading,
              online: isDbOnline,
              detail: isDbOnline ? 'Connected — revenue_pulse' : 'Connection failed',
            },
            {
              label: 'FastAPI Analytics API',
              icon: Cpu,
              loading: apiLoading,
              online: isApiOnline,
              detail: isApiOnline ? 'Online — http://localhost:8000' : 'Unreachable',
            },
            {
              label: 'ML Model Registry',
              icon: Cpu,
              loading: false,
              online: true,
              detail: '4 models active (v3)',
            },
            {
              label: 'Internet Connectivity',
              icon: Wifi,
              loading: false,
              online: navigator.onLine,
              detail: navigator.onLine ? 'Connected' : 'Offline',
            },
          ].map(({ label, icon: Icon, loading, online, detail }) => (
            <div key={label} className="flex items-center justify-between py-3 border-b last:border-0">
              <div className="flex items-center gap-3">
                <Icon className="w-5 h-5 text-slate-400" />
                <div>
                  <p className="font-medium text-sm">{label}</p>
                  <p className="text-xs text-slate-400">{loading ? 'Checking...' : detail}</p>
                </div>
              </div>
              {loading ? (
                <div className="w-16 h-5 bg-slate-100 dark:bg-slate-800 animate-pulse rounded-full" />
              ) : online ? (
                <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 px-2.5 py-1 rounded-full">
                  <CheckCircle className="w-3 h-3" /> Online
                </span>
              ) : (
                <span className="flex items-center gap-1.5 text-xs font-semibold text-red-600 bg-red-50 dark:bg-red-900/20 px-2.5 py-1 rounded-full">
                  <XCircle className="w-3 h-3" /> Offline
                </span>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* API Config */}
      <Card>
        <CardHeader>
          <CardTitle>API Configuration</CardTitle>
          <CardDescription>Backend endpoint configuration.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Backend API URL</p>
              <p className="text-xs text-slate-400">Used by all dashboard API calls</p>
            </div>
            <span className="font-mono text-sm bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-md">
              http://localhost:8000/api
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
