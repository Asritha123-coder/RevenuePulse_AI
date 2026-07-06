import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, PieChart, Pie, Cell, Legend
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Users, Activity, Heart, Globe } from 'lucide-react';

const COLORS = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'];

const RETENTION_DATA = [
  { month: 'Jan', rate: 94.2 }, { month: 'Feb', rate: 93.8 }, { month: 'Mar', rate: 95.1 },
  { month: 'Apr', rate: 94.7 }, { month: 'May', rate: 96.2 }, { month: 'Jun', rate: 95.8 },
];

const SEGMENT_DATA = [
  { name: 'Enterprise', value: 38 }, { name: 'Mid Market', value: 31 },
  { name: 'Small Business', value: 19 }, { name: 'Startup', value: 12 },
];

const CLV_DATA = [
  { industry: 'Healthcare', clv: 48000 }, { industry: 'Finance', clv: 42000 },
  { industry: 'Retail', clv: 28000 }, { industry: 'Technology', clv: 55000 },
  { industry: 'Manufacturing', clv: 32000 }, { industry: 'Education', clv: 22000 },
];

export default function CustomerIntelligence() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Customer Intelligence</h1>
        <p className="text-slate-500 mt-1">Customer segmentation, retention, and lifetime value analysis.</p>
      </div>

      {/* KPI Row */}
      <div className="grid gap-4 md:grid-cols-4">
        {[
          { label: 'Total Customers', value: '3,000', icon: Users, bg: 'bg-blue-50 dark:bg-blue-900/20', color: 'text-blue-600' },
          { label: 'Avg Retention', value: '94.8%', icon: Heart, bg: 'bg-emerald-50 dark:bg-emerald-900/20', color: 'text-emerald-600' },
          { label: 'Avg CLV', value: '$38,200', icon: Activity, bg: 'bg-violet-50 dark:bg-violet-900/20', color: 'text-violet-600' },
          { label: 'Countries', value: '47', icon: Globe, bg: 'bg-amber-50 dark:bg-amber-900/20', color: 'text-amber-600' },
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

      <div className="grid gap-6 md:grid-cols-3">
        {/* Retention Trend */}
        <Card className="md:col-span-2">
          <CardHeader><CardTitle>Monthly Retention Rate (%)</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={RETENTION_DATA}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-slate-200 dark:stroke-slate-700" />
                <XAxis dataKey="month" tickLine={false} axisLine={false} className="text-xs" />
                <YAxis domain={[88, 100]} tickLine={false} axisLine={false} className="text-xs" />
                <Tooltip formatter={(v: any) => [`${v}%`, 'Retention']} />
                <Bar dataKey="rate" fill="#10b981" radius={[4, 4, 0, 0]} barSize={36} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Customer Segments */}
        <Card>
          <CardHeader><CardTitle>Customer Segments</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={SEGMENT_DATA} dataKey="value" nameKey="name" cx="50%" cy="45%" outerRadius={75} innerRadius={40}>
                  {SEGMENT_DATA.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Legend iconType="circle" iconSize={8} />
                <Tooltip formatter={(v: any) => [`${v}%`, 'Share']} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* CLV by Industry */}
      <Card>
        <CardHeader><CardTitle>Customer Lifetime Value by Industry</CardTitle></CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={CLV_DATA} margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-slate-200 dark:stroke-slate-700" />
              <XAxis dataKey="industry" tickLine={false} axisLine={false} className="text-xs" />
              <YAxis tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} tickLine={false} axisLine={false} className="text-xs" />
              <Tooltip formatter={(v: any) => [`$${v.toLocaleString()}`, 'Avg CLV']} />
              <Bar dataKey="clv" radius={[4, 4, 0, 0]}>
                {CLV_DATA.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
