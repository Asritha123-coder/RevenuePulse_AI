import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, FunnelChart, Funnel, LabelList, Cell, PieChart, Pie, Legend
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { analyticsService } from '@/services/analytics';
import { Trophy, Target, TrendingUp } from 'lucide-react';

const COLORS = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'];

const MOCK_LEADERBOARD = [
  { name: 'Alex Johnson', deals: 28, value: 1420000, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alex' },
  { name: 'Maria Santos', deals: 24, value: 1280000, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Maria' },
  { name: 'James Chen', deals: 21, value: 980000, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=James' },
  { name: 'Sarah Park', deals: 19, value: 870000, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah' },
  { name: 'David Okafor', deals: 17, value: 760000, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=David' },
];

export default function SalesIntelligence() {
  const { data: funnelData, isLoading: funnelLoading } = useQuery({
    queryKey: ['pipeline-funnel'],
    queryFn: analyticsService.getPipelineFunnel,
  });

  const funnelChartData = Object.entries(funnelData?.data?.status_distribution || {}).map(([name, value]) => ({
    name, value
  }));

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Sales Intelligence</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">Pipeline analysis, deal tracking, and sales rep performance.</p>
      </div>

      {/* KPI Metrics */}
      <div className="grid gap-4 md:grid-cols-3">
        {[
          { label: 'Won Opportunities', value: '847', icon: Trophy, color: 'text-emerald-500' },
          { label: 'Active Pipeline', value: '$24.6M', icon: Target, color: 'text-blue-500' },
          { label: 'Win Rate', value: '42.3%', icon: TrendingUp, color: 'text-violet-500' },
        ].map(({ label, value, icon: Icon, color }) => (
          <Card key={label}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">{label}</p>
                  <p className="text-3xl font-bold mt-2">{value}</p>
                </div>
                <div className={`p-3 rounded-xl bg-slate-50 dark:bg-slate-800 ${color}`}>
                  <Icon className="w-6 h-6" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Funnel + Leaderboard */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Pipeline Funnel</CardTitle></CardHeader>
          <CardContent>
            {funnelLoading ? (
              <div className="h-64 bg-slate-100 dark:bg-slate-800 animate-pulse rounded-lg" />
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={funnelChartData} layout="vertical" margin={{ left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} className="stroke-slate-200 dark:stroke-slate-700" />
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} className="text-xs" width={110} />
                  <Tooltip />
                  <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={28}>
                    {funnelChartData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Sales Rep Leaderboard</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-4">
              {MOCK_LEADERBOARD.map((rep, i) => (
                <div key={rep.name} className="flex items-center gap-3">
                  <span className="text-sm font-bold text-slate-400 dark:text-slate-400 w-4">{i + 1}</span>
                  <img src={rep.avatar} alt={rep.name} className="w-8 h-8 rounded-full border" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">{rep.name}</p>
                    <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5 mt-1">
                      <div
                        className="bg-brand-600 h-1.5 rounded-full"
                        style={{ width: `${(rep.deals / 30) * 100}%` }}
                      />
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold">{rep.deals} deals</p>
                    <p className="text-xs text-slate-400 dark:text-slate-400">${(rep.value / 1e6).toFixed(1)}M</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
