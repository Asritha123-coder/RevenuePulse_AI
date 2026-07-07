import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  DollarSign, 
  TrendingUp, 
  Users, 
  Target, 
  Activity, 
  AlertTriangle 
} from 'lucide-react';
import { analyticsService } from '@/services/analytics';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';

export default function Dashboard() {
  const { data: kpiData, isLoading: kpiLoading } = useQuery({
    queryKey: ['kpis'],
    queryFn: analyticsService.getKPIs,
  });

  const { data: trendData, isLoading: trendLoading } = useQuery({
    queryKey: ['revenue-trend'],
    queryFn: analyticsService.getRevenueTrend,
  });

  const { data: funnelData, isLoading: funnelLoading } = useQuery({
    queryKey: ['pipeline-funnel'],
    queryFn: analyticsService.getPipelineFunnel,
  });

  const formatCurrency = (val: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val || 0);

  const kpis: Record<string, any> = kpiData?.data || {};
  
  // Transform trend data for Recharts
  const chartData = Object.entries(trendData?.data?.revenue_by_month || {}).map(([month, rev]) => ({
    name: month,
    revenue: rev
  }));

  // Transform funnel data for Recharts
  const pipelineData = Object.entries(funnelData?.data?.status_distribution || {}).map(([status, count]) => ({
    name: status,
    count: count
  }));

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Executive Dashboard</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-2">Welcome back. Here's a high-level overview of RevenuePulse AI performance.</p>
      </div>

      {/* KPI GRID */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard title="Total Revenue" value={formatCurrency(kpis.total_revenue)} icon={DollarSign} loading={kpiLoading} />
        <MetricCard title="Total MRR" value={formatCurrency(kpis.total_mrr)} icon={TrendingUp} loading={kpiLoading} />
        <MetricCard title="Pipeline Value" value={formatCurrency(kpis.pipeline_value)} icon={Target} loading={kpiLoading} />
        <MetricCard title="Total Customers" value={kpis.total_customers?.toString()} icon={Users} loading={kpiLoading} />
      </div>

      {/* CHARTS GRID */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        
        {/* Main Revenue Trend Chart */}
        <Card className="lg:col-span-4">
          <CardHeader>
            <CardTitle>Revenue Trend (Last 12 Months)</CardTitle>
          </CardHeader>
          <CardContent className="pl-0">
            {trendLoading ? (
              <div className="h-[300px] flex items-center justify-center text-slate-400 dark:text-slate-400">Loading chart data...</div>
            ) : (
              <div className="h-[300px] w-full mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-slate-200 dark:stroke-slate-700" />
                    <XAxis dataKey="name" className="text-xs" tickLine={false} axisLine={false} />
                    <YAxis 
                      className="text-xs" 
                      tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`}
                      tickLine={false} 
                      axisLine={false} 
                    />
                    <Tooltip 
                      formatter={(value: any) => [formatCurrency(Number(value)), "Revenue"]}
                      labelClassName="text-slate-900 dark:text-white font-medium"
                    />
                    <Area type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorRev)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Pipeline Funnel */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Pipeline Funnel</CardTitle>
          </CardHeader>
          <CardContent>
            {funnelLoading ? (
               <div className="h-[300px] flex items-center justify-center text-slate-400 dark:text-slate-400">Loading chart data...</div>
            ) : (
              <div className="h-[300px] w-full mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={pipelineData} layout="vertical" margin={{ top: 0, right: 30, left: 20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} className="stroke-slate-200 dark:stroke-slate-700" />
                    <XAxis type="number" hide />
                    <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} className="text-xs font-medium" width={90} />
                    <Tooltip cursor={{fill: 'transparent'}} />
                    <Bar dataKey="count" fill="#8b5cf6" radius={[0, 4, 4, 0]} barSize={32} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon: Icon, loading }: { title: string, value?: string, icon: any, loading: boolean }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</CardTitle>
        <Icon className="w-4 h-4 text-slate-400 dark:text-slate-400" />
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="h-8 w-24 bg-slate-200 dark:bg-slate-700 animate-pulse rounded mt-1"></div>
        ) : (
          <div className="text-2xl font-bold">{value || 'N/A'}</div>
        )}
      </CardContent>
    </Card>
  );
}
