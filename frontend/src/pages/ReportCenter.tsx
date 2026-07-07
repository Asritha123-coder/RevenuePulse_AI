import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FileBarChart, Download, FileText, TrendingUp, Users, Megaphone, LifeBuoy, Database, Brain } from 'lucide-react';
import { toast } from 'react-toastify';

const REPORTS = [
  {
    key: 'executive',
    title: 'Executive Report',
    description: 'High-level KPIs, MRR/ARR, growth metrics, and strategic insights.',
    icon: TrendingUp,
    bg: 'bg-blue-50 dark:bg-blue-900/20',
    color: 'text-blue-600',
  },
  {
    key: 'revenue',
    title: 'Revenue Report',
    description: 'Detailed revenue breakdown by industry, country, and time period.',
    icon: FileBarChart,
    bg: 'bg-emerald-50 dark:bg-emerald-900/20',
    color: 'text-emerald-600',
  },
  {
    key: 'customer',
    title: 'Customer Report',
    description: 'Customer segmentation, retention rates, CLV, and churn analysis.',
    icon: Users,
    bg: 'bg-violet-50 dark:bg-violet-900/20',
    color: 'text-violet-600',
  },
  {
    key: 'marketing',
    title: 'Marketing Report',
    description: 'Campaign performance, ROI rankings, CTR/CPC, and channel mix.',
    icon: Megaphone,
    bg: 'bg-rose-50 dark:bg-rose-900/20',
    color: 'text-rose-600',
  },
  {
    key: 'support',
    title: 'Support Report',
    description: 'Ticket volumes, resolution time, CSAT scores, and priority distribution.',
    icon: LifeBuoy,
    bg: 'bg-amber-50 dark:bg-amber-900/20',
    color: 'text-amber-600',
  },
  {
    key: 'ml',
    title: 'ML Model Report',
    description: 'Model accuracy, precision/recall, feature importance, and version history.',
    icon: Brain,
    bg: 'bg-indigo-50 dark:bg-indigo-900/20',
    color: 'text-indigo-600',
  },
  {
    key: 'etl',
    title: 'ETL Report',
    description: 'Pipeline execution logs, row counts, validation errors, and performance.',
    icon: Database,
    bg: 'bg-cyan-50 dark:bg-cyan-900/20',
    color: 'text-cyan-600',
  },
];

function handleDownload(reportKey: string, format: string) {
  toast.info(`Generating ${reportKey.toUpperCase()} report as ${format.toUpperCase()}...`, { autoClose: 3000 });
  // In production, this would call an API endpoint that returns a file
  setTimeout(() => {
    toast.success(`${reportKey.toUpperCase()} ${format.toUpperCase()} report downloaded!`);
  }, 2000);
}

export default function ReportCenter() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Report Center</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">Generate and download enterprise-grade reports across all intelligence modules.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {REPORTS.map(({ key, title, description, icon: Icon, bg, color }) => (
          <Card key={key} className="flex flex-col hover:shadow-md transition-shadow">
            <CardHeader className="pb-2">
              <div className="flex items-center gap-3">
                <div className={`p-2.5 rounded-lg ${bg} ${color}`}><Icon className="w-5 h-5" /></div>
                <CardTitle className="text-base">{title}</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col">
              <p className="text-sm text-slate-500 dark:text-slate-400 flex-1 mb-4">{description}</p>
              <div className="flex gap-2 flex-wrap">
                {['CSV', 'Excel', 'PDF'].map(fmt => (
                  <Button
                    key={fmt}
                    variant="outline"
                    size="sm"
                    onClick={() => handleDownload(key, fmt)}
                    className="flex items-center gap-1.5 text-xs"
                  >
                    <Download className="w-3 h-3" />
                    {fmt}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Downloads */}
      <Card>
        <CardHeader><CardTitle>Recent Report Downloads</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { name: 'Executive Report — Q2 2026', format: 'PDF', size: '1.2 MB', date: '2026-07-06 23:15' },
              { name: 'Revenue Report — June 2026', format: 'Excel', size: '842 KB', date: '2026-07-06 22:40' },
              { name: 'Customer Report — YTD', format: 'CSV', size: '3.4 MB', date: '2026-07-05 18:30' },
              { name: 'ML Model Report — v3', format: 'PDF', size: '2.1 MB', date: '2026-07-05 11:00' },
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b last:border-0">
                <div className="flex items-center gap-3">
                  <FileText className="w-4 h-4 text-slate-400 dark:text-slate-400" />
                  <div>
                    <p className="text-sm font-medium">{item.name}</p>
                    <p className="text-xs text-slate-400 dark:text-slate-400">{item.date} · {item.size}</p>
                  </div>
                </div>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 dark:text-slate-400">
                  {item.format}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
