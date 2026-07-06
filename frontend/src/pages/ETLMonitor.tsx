import React from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { etlService } from '@/services/etl';
import { Play, CheckCircle, XCircle, Clock, AlertTriangle, Database } from 'lucide-react';
import { toast } from 'react-toastify';

const MOCK_ETL_HISTORY = [
  { id: 'ETL-024', table: 'accounts', rows: 3000, failed: 0, duration: '1.2s', status: 'success', timestamp: '2026-07-06 23:32:11' },
  { id: 'ETL-024', table: 'contacts', rows: 12000, failed: 0, duration: '4.1s', status: 'success', timestamp: '2026-07-06 23:32:13' },
  { id: 'ETL-024', table: 'campaigns', rows: 500, failed: 2, duration: '0.8s', status: 'warning', timestamp: '2026-07-06 23:32:14' },
  { id: 'ETL-024', table: 'opportunities', rows: 15000, failed: 0, duration: '5.6s', status: 'success', timestamp: '2026-07-06 23:32:19' },
  { id: 'ETL-024', table: 'subscriptions', rows: 3000, failed: 0, duration: '1.9s', status: 'success', timestamp: '2026-07-06 23:32:22' },
  { id: 'ETL-024', table: 'product_usage', rows: 50000, failed: 0, duration: '18.3s', status: 'success', timestamp: '2026-07-06 23:32:41' },
  { id: 'ETL-024', table: 'website_activity', rows: 40000, failed: 0, duration: '14.7s', status: 'success', timestamp: '2026-07-06 23:32:56' },
  { id: 'ETL-024', table: 'support_tickets', rows: 20000, failed: 0, duration: '7.2s', status: 'success', timestamp: '2026-07-06 23:33:04' },
];

type RowStatus = 'success' | 'warning' | 'error';

function StatusBadge({ status }: { status: RowStatus | string }) {
  const cfg = {
    success: { icon: CheckCircle, bg: 'bg-emerald-100 dark:bg-emerald-900/30', text: 'text-emerald-700 dark:text-emerald-300', label: 'Success' },
    warning: { icon: AlertTriangle, bg: 'bg-amber-100 dark:bg-amber-900/30', text: 'text-amber-700 dark:text-amber-300', label: 'Warning' },
    error: { icon: XCircle, bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-300', label: 'Error' },
  }[status as RowStatus] || { icon: Clock, bg: 'bg-slate-100', text: 'text-slate-700', label: status };

  const Icon = cfg.icon;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-semibold ${cfg.bg} ${cfg.text}`}>
      <Icon className="w-3 h-3" />
      {cfg.label}
    </span>
  );
}

export default function ETLMonitor() {
  const { data: healthData } = useQuery({
    queryKey: ['db-health'],
    queryFn: etlService.getDatabaseHealth,
  });

  const runMutation = useMutation({
    mutationFn: etlService.triggerPipeline,
    onSuccess: () => toast.success('ETL pipeline triggered successfully!'),
    onError: () => toast.error('Failed to trigger ETL pipeline.'),
  });

  const totalRows = MOCK_ETL_HISTORY.reduce((s, r) => s + r.rows, 0);
  const totalFailed = MOCK_ETL_HISTORY.reduce((s, r) => s + r.failed, 0);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">ETL Monitor</h1>
          <p className="text-slate-500 mt-1">Pipeline execution history, load metrics, and data ingestion status.</p>
        </div>
        <Button onClick={() => runMutation.mutate()} disabled={runMutation.isPending} className="flex items-center gap-2">
          <Play className="w-4 h-4" />
          {runMutation.isPending ? 'Running...' : 'Run Pipeline'}
        </Button>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-4">
        {[
          { label: 'Total Rows Loaded', value: totalRows.toLocaleString(), icon: Database, bg: 'bg-blue-50 dark:bg-blue-900/20', color: 'text-blue-600' },
          { label: 'Failed Rows', value: totalFailed.toString(), icon: XCircle, bg: 'bg-red-50 dark:bg-red-900/20', color: 'text-red-600' },
          { label: 'Tables Processed', value: MOCK_ETL_HISTORY.length.toString(), icon: CheckCircle, bg: 'bg-emerald-50 dark:bg-emerald-900/20', color: 'text-emerald-600' },
          { label: 'Total Duration', value: '54.8s', icon: Clock, bg: 'bg-amber-50 dark:bg-amber-900/20', color: 'text-amber-600' },
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

      {/* Execution Log Table */}
      <Card>
        <CardHeader><CardTitle>Last Pipeline Execution Log — Run ID: ETL-024</CardTitle></CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-slate-50 dark:bg-slate-800/50">
                  {['Table', 'Rows Loaded', 'Failed', 'Duration', 'Status', 'Timestamp'].map(h => (
                    <th key={h} className="text-left py-3 px-6 font-semibold text-slate-600 dark:text-slate-400">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {MOCK_ETL_HISTORY.map((row, i) => (
                  <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-6 font-mono text-sm font-medium">{row.table}</td>
                    <td className="py-3 px-6">{row.rows.toLocaleString()}</td>
                    <td className="py-3 px-6">{row.failed > 0 ? <span className="text-red-600 font-semibold">{row.failed}</span> : row.failed}</td>
                    <td className="py-3 px-6 font-mono">{row.duration}</td>
                    <td className="py-3 px-6"><StatusBadge status={row.status} /></td>
                    <td className="py-3 px-6 text-slate-400 text-xs">{row.timestamp}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
