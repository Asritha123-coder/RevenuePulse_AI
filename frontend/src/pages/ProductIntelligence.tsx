import React from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, LineChart, Line, Cell
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Activity, Cpu, HardDrive, Zap } from 'lucide-react';

const DAU_DATA = [
  { day: 'Mon', dau: 1840 }, { day: 'Tue', dau: 1920 }, { day: 'Wed', dau: 2100 },
  { day: 'Thu', dau: 2040 }, { day: 'Fri', dau: 1980 }, { day: 'Sat', dau: 1200 },
  { day: 'Sun', dau: 980 },
];

const MAU_DATA = [
  { month: 'Jan', mau: 12400 }, { month: 'Feb', mau: 12900 }, { month: 'Mar', mau: 13500 },
  { month: 'Apr', mau: 14100 }, { month: 'May', mau: 14800 }, { month: 'Jun', mau: 15400 },
];

const FEATURE_ADOPTION = [
  { feature: 'Dashboard', usage: 94 }, { feature: 'Analytics', usage: 78 },
  { feature: 'ML Predict', usage: 52 }, { feature: 'Reports', usage: 67 },
  { feature: 'AI Copilot', usage: 41 }, { feature: 'ETL Monitor', usage: 35 },
];

const COLORS = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'];

export default function ProductIntelligence() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Product Intelligence</h1>
        <p className="text-slate-500 mt-1">Usage analytics, feature adoption, and engagement metrics.</p>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-4">
        {[
          { label: 'Daily Active Users', value: '1,980', icon: Activity, bg: 'bg-blue-50 dark:bg-blue-900/20', color: 'text-blue-600' },
          { label: 'Monthly Active Users', value: '15,400', icon: Zap, bg: 'bg-violet-50 dark:bg-violet-900/20', color: 'text-violet-600' },
          { label: 'Avg API Calls/Day', value: '284K', icon: Cpu, bg: 'bg-emerald-50 dark:bg-emerald-900/20', color: 'text-emerald-600' },
          { label: 'Storage Used', value: '12.4 TB', icon: HardDrive, bg: 'bg-amber-50 dark:bg-amber-900/20', color: 'text-amber-600' },
        ].map(({ label, value, icon: Icon, bg, color }) => (
          <Card key={label}>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className={`p-2.5 rounded-lg ${bg} ${color}`}><Icon className="w-5 h-5" /></div>
                <div>
                  <p className="text-xs text-slate-500 font-medium">{label}</p>
                  <p className="text-2xl font-bold">{value}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* DAU Chart */}
        <Card>
          <CardHeader><CardTitle>Daily Active Users (This Week)</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={DAU_DATA}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-slate-200 dark:stroke-slate-700" />
                <XAxis dataKey="day" tickLine={false} axisLine={false} className="text-xs" />
                <YAxis tickLine={false} axisLine={false} className="text-xs" />
                <Tooltip />
                <Bar dataKey="dau" name="DAU" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={32} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* MAU Trend */}
        <Card>
          <CardHeader><CardTitle>Monthly Active Users Trend</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={MAU_DATA}>
                <defs>
                  <linearGradient id="mauGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-slate-200 dark:stroke-slate-700" />
                <XAxis dataKey="month" tickLine={false} axisLine={false} className="text-xs" />
                <YAxis tickLine={false} axisLine={false} className="text-xs" />
                <Tooltip />
                <Area type="monotone" dataKey="mau" name="MAU" stroke="#8b5cf6" strokeWidth={3} fill="url(#mauGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Feature Adoption */}
      <Card>
        <CardHeader><CardTitle>Feature Adoption Rate (%)</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-4">
            {FEATURE_ADOPTION.map(({ feature, usage }, i) => (
              <div key={feature} className="flex items-center gap-4">
                <span className="text-sm font-medium w-28">{feature}</span>
                <div className="flex-1 bg-slate-100 dark:bg-slate-800 rounded-full h-2.5">
                  <div
                    className="h-2.5 rounded-full transition-all duration-700"
                    style={{ width: `${usage}%`, backgroundColor: COLORS[i % COLORS.length] }}
                  />
                </div>
                <span className="text-sm font-semibold w-10 text-right">{usage}%</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
