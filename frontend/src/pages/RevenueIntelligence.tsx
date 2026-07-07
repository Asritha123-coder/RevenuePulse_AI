import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { analyticsService } from '@/services/analytics';
import { TrendingUp, Globe, Layers } from 'lucide-react';

const COLORS = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#6366f1'];

function SectionTitle({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="mb-1">
      <h2 className="text-xl font-bold tracking-tight">{title}</h2>
      {subtitle && <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{subtitle}</p>}
    </div>
  );
}

export default function RevenueIntelligence() {
  const { data: trend, isLoading: trendLoading } = useQuery({
    queryKey: ['revenue-trend'],
    queryFn: analyticsService.getRevenueTrend,
  });

  const { data: geo, isLoading: geoLoading } = useQuery({
    queryKey: ['revenue-geo'],
    queryFn: analyticsService.getRevenueByRegion,
  });

  const { data: industry, isLoading: industryLoading } = useQuery({
    queryKey: ['revenue-industry'],
    queryFn: analyticsService.getRevenueByIndustry,
  });

  const trendChartData = Object.entries(trend?.data?.revenue_by_month || {}).map(([name, revenue]) => ({ name, revenue }));
  const geoData = Object.entries(geo?.data?.country_distribution || {}).slice(0, 8).map(([name, value]) => ({ name, value }));
  const industryData = Object.entries(industry?.data?.industry_distribution || {}).slice(0, 8).map(([name, value]) => ({ name, value }));

  const formatCurrency = (v: number) => `$${(v / 1e6).toFixed(2)}M`;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Revenue Intelligence</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Deep-dive revenue analytics, trends, and geographic distribution.</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-emerald-600 font-medium bg-emerald-50 dark:bg-emerald-900/30 px-3 py-1.5 rounded-full">
          <TrendingUp className="w-4 h-4" />
          Live Data
        </div>
      </div>

      {/* Revenue Trend */}
      <div>
        <SectionTitle title="Monthly Revenue Trend" subtitle="MRR performance across the last 12 months" />
        <Card className="mt-4">
          <CardContent className="pt-6">
            {trendLoading ? (
              <div className="h-72 bg-slate-100 dark:bg-slate-800 animate-pulse rounded-lg" />
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={trendChartData} margin={{ top: 10, right: 30, left: 20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-slate-200 dark:stroke-slate-700" />
                  <XAxis dataKey="name" tickLine={false} axisLine={false} className="text-xs" />
                  <YAxis tickFormatter={formatCurrency} tickLine={false} axisLine={false} className="text-xs" />
                  <Tooltip formatter={(v: any) => [formatCurrency(v), 'Revenue']} />
                  <Area type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={3} fill="url(#revGrad)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Geo + Industry */}
      <div className="grid gap-6 md:grid-cols-2">
        <div>
          <SectionTitle title="Revenue by Country" subtitle="Geographic revenue distribution" />
          <Card className="mt-4">
            <CardContent className="pt-6">
              {geoLoading ? (
                <div className="h-72 bg-slate-100 dark:bg-slate-800 animate-pulse rounded-lg" />
              ) : (
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={geoData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-slate-200 dark:stroke-slate-700" />
                    <XAxis dataKey="name" tickLine={false} axisLine={false} className="text-xs" tick={{ fontSize: 11 }} />
                    <YAxis hide />
                    <Tooltip formatter={(v: any) => [`$${v.toLocaleString()}`, 'Revenue']} />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                      {geoData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </div>

        <div>
          <SectionTitle title="Revenue by Industry" subtitle="Industry vertical performance split" />
          <Card className="mt-4">
            <CardContent className="pt-6 flex flex-col items-center">
              {industryLoading ? (
                <div className="h-72 w-full bg-slate-100 dark:bg-slate-800 animate-pulse rounded-lg" />
              ) : (
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie data={industryData} dataKey="value" nameKey="name" cx="50%" cy="45%" outerRadius={90} label={({ name }) => name}>
                      {industryData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip formatter={(v: any) => [`$${v.toLocaleString()}`, 'Revenue']} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
