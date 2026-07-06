import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, LineChart, Line
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Ticket, Clock, Star, AlertCircle } from 'lucide-react';

const COLORS = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981'];

const PRIORITY_DATA = [
  { name: 'Critical', value: 142, color: '#ef4444' },
  { name: 'High', value: 384, color: '#f59e0b' },
  { name: 'Medium', value: 621, color: '#3b82f6' },
  { name: 'Low', value: 853, color: '#10b981' },
];

const CSAT_TREND = [
  { month: 'Jan', score: 3.9 }, { month: 'Feb', score: 4.1 }, { month: 'Mar', score: 4.0 },
  { month: 'Apr', score: 4.3 }, { month: 'May', score: 4.2 }, { month: 'Jun', score: 4.5 },
];

const CATEGORY_DATA = [
  { category: 'Billing', count: 312 }, { category: 'Technical', count: 548 },
  { category: 'Onboarding', count: 184 }, { category: 'Feature Request', count: 267 },
  { category: 'Account', count: 189 }, { category: 'Integration', count: 143 },
];

export default function SupportIntelligence() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Support Intelligence</h1>
        <p className="text-slate-500 mt-1">Ticket analysis, resolution times, and customer satisfaction scores.</p>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-4">
        {[
          { label: 'Open Tickets', value: '284', icon: Ticket, bg: 'bg-red-50 dark:bg-red-900/20', color: 'text-red-600' },
          { label: 'Avg Resolution', value: '18.4h', icon: Clock, bg: 'bg-amber-50 dark:bg-amber-900/20', color: 'text-amber-600' },
          { label: 'Avg CSAT Score', value: '4.3/5', icon: Star, bg: 'bg-emerald-50 dark:bg-emerald-900/20', color: 'text-emerald-600' },
          { label: 'Critical Issues', value: '142', icon: AlertCircle, bg: 'bg-rose-50 dark:bg-rose-900/20', color: 'text-rose-600' },
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
        {/* Priority Distribution */}
        <Card>
          <CardHeader><CardTitle>Ticket Priority Split</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={PRIORITY_DATA} dataKey="value" nameKey="name" cx="50%" cy="45%" outerRadius={80} innerRadius={45}>
                  {PRIORITY_DATA.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Pie>
                <Legend iconType="circle" iconSize={8} />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* CSAT Trend */}
        <Card className="md:col-span-2">
          <CardHeader><CardTitle>Customer Satisfaction (CSAT) Trend</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={CSAT_TREND}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-slate-200 dark:stroke-slate-700" />
                <XAxis dataKey="month" tickLine={false} axisLine={false} className="text-xs" />
                <YAxis domain={[3.5, 5]} tickLine={false} axisLine={false} className="text-xs" />
                <Tooltip formatter={(v: any) => [`${v}/5`, 'CSAT']} />
                <Line type="monotone" dataKey="score" stroke="#10b981" strokeWidth={3} dot={{ r: 5, fill: '#10b981' }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Category Distribution */}
      <Card>
        <CardHeader><CardTitle>Tickets by Category</CardTitle></CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={CATEGORY_DATA} margin={{ left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-slate-200 dark:stroke-slate-700" />
              <XAxis dataKey="category" tickLine={false} axisLine={false} className="text-xs" />
              <YAxis tickLine={false} axisLine={false} className="text-xs" />
              <Tooltip />
              <Bar dataKey="count" name="Tickets" radius={[4, 4, 0, 0]}>
                {CATEGORY_DATA.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
