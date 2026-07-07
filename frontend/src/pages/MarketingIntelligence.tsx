import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Legend
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Megaphone, MousePointer, DollarSign, TrendingUp } from 'lucide-react';

const COLORS = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899'];

const CAMPAIGN_ROI = [
  { name: 'Summer Blast', roi: 340, spend: 45000, revenue: 198000 },
  { name: 'Q2 Enterprise', roi: 280, spend: 62000, revenue: 235600 },
  { name: 'Healthcare Series', roi: 220, spend: 38000, revenue: 121600 },
  { name: 'SMB Growth', roi: 190, spend: 28000, revenue: 81200 },
  { name: 'Webinar Funnel', roi: 410, spend: 12000, revenue: 61200 },
  { name: 'Brand Awareness', roi: 80, spend: 55000, revenue: 99000 },
];

const CTR_TREND = [
  { month: 'Jan', ctr: 3.2 }, { month: 'Feb', ctr: 3.5 }, { month: 'Mar', ctr: 3.8 },
  { month: 'Apr', ctr: 4.1 }, { month: 'May', ctr: 3.9 }, { month: 'Jun', ctr: 4.4 },
];

const CHANNEL_MIX = [
  { name: 'Email', value: 32 }, { name: 'Paid Search', value: 24 },
  { name: 'Social Media', value: 18 }, { name: 'Webinar', value: 14 },
  { name: 'Content', value: 12 },
];

export default function MarketingIntelligence() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Marketing Intelligence</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">Campaign ROI, click-through performance, and marketing spend efficiency.</p>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-4">
        {[
          { label: 'Total Campaigns', value: '124', icon: Megaphone, bg: 'bg-violet-50 dark:bg-violet-900/20', color: 'text-violet-600' },
          { label: 'Avg CTR', value: '3.97%', icon: MousePointer, bg: 'bg-blue-50 dark:bg-blue-900/20', color: 'text-blue-600' },
          { label: 'Total Spend', value: '$1.24M', icon: DollarSign, bg: 'bg-rose-50 dark:bg-rose-900/20', color: 'text-rose-600' },
          { label: 'Avg ROI', value: '254%', icon: TrendingUp, bg: 'bg-emerald-50 dark:bg-emerald-900/20', color: 'text-emerald-600' },
        ].map(({ label, value, icon: Icon, bg, color }) => (
          <Card key={label}>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className={`p-2.5 rounded-lg ${bg} ${color}`}><Icon className="w-5 h-5" /></div>
                <div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">{label}</p>
                  <p className="text-2xl font-bold">{value}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Campaign ROI Leaderboard */}
      <Card>
        <CardHeader><CardTitle>Campaign ROI Ranking</CardTitle></CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={CAMPAIGN_ROI} margin={{ left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-slate-200 dark:stroke-slate-700" />
              <XAxis dataKey="name" tickLine={false} axisLine={false} className="text-xs" tick={{ fontSize: 11 }} />
              <YAxis tickFormatter={(v) => `${v}%`} tickLine={false} axisLine={false} className="text-xs" />
              <Tooltip formatter={(v: any, name: any) => [name === 'roi' ? `${v}%` : `$${v.toLocaleString()}`, name.toUpperCase()]} />
              <Bar dataKey="roi" name="ROI" radius={[4, 4, 0, 0]}>
                {CAMPAIGN_ROI.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        {/* CTR Trend */}
        <Card>
          <CardHeader><CardTitle>Click-Through Rate Trend (%)</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={CTR_TREND}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-slate-200 dark:stroke-slate-700" />
                <XAxis dataKey="month" tickLine={false} axisLine={false} className="text-xs" />
                <YAxis tickFormatter={(v) => `${v}%`} tickLine={false} axisLine={false} className="text-xs" />
                <Tooltip formatter={(v: any) => [`${v}%`, 'CTR']} />
                <Line type="monotone" dataKey="ctr" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 5, fill: '#8b5cf6' }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Channel Mix */}
        <Card>
          <CardHeader><CardTitle>Marketing Channel Mix</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={CHANNEL_MIX} dataKey="value" nameKey="name" cx="50%" cy="45%" outerRadius={80} innerRadius={45}>
                  {CHANNEL_MIX.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Legend iconType="circle" iconSize={8} />
                <Tooltip formatter={(v: any) => [`${v}%`, 'Share']} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
