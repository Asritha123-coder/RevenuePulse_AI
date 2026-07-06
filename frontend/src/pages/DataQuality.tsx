import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { ShieldCheck, AlertTriangle, XCircle, CheckCircle } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts';

const QUALITY_CHECKS = [
  { check: 'Duplicate Account IDs', table: 'accounts', severity: 'CRITICAL', issues: 0, status: 'pass' },
  { check: 'Missing Company Name', table: 'accounts', severity: 'INFO', issues: 12, status: 'warn' },
  { check: 'Invalid Email Format', table: 'contacts', severity: 'ERROR', issues: 34, status: 'fail' },
  { check: 'Invalid Phone Numbers', table: 'contacts', severity: 'WARNING', issues: 87, status: 'warn' },
  { check: 'Negative Revenue', table: 'subscriptions', severity: 'CRITICAL', issues: 0, status: 'pass' },
  { check: 'Future Contract Dates', table: 'opportunities', severity: 'WARNING', issues: 5, status: 'warn' },
  { check: 'Missing Product Usage', table: 'product_usage', severity: 'INFO', issues: 218, status: 'warn' },
  { check: 'Zero-value Tickets', table: 'support_tickets', severity: 'INFO', issues: 0, status: 'pass' },
];

const SCORE_BY_TABLE = [
  { table: 'accounts', score: 96 },
  { table: 'contacts', score: 78 },
  { table: 'campaigns', score: 91 },
  { table: 'opportunities', score: 94 },
  { table: 'subscriptions', score: 99 },
  { table: 'product_usage', score: 88 },
  { table: 'website_activity', score: 97 },
  { table: 'support_tickets', score: 98 },
];

function getScoreColor(score: number) {
  if (score >= 95) return '#10b981';
  if (score >= 80) return '#f59e0b';
  return '#ef4444';
}

function StatusIcon({ status }: { status: string }) {
  if (status === 'pass') return <CheckCircle className="w-4 h-4 text-emerald-500" />;
  if (status === 'fail') return <XCircle className="w-4 h-4 text-red-500" />;
  return <AlertTriangle className="w-4 h-4 text-amber-500" />;
}

export default function DataQuality() {
  const overall = Math.round(SCORE_BY_TABLE.reduce((s, r) => s + r.score, 0) / SCORE_BY_TABLE.length);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Data Quality Dashboard</h1>
        <p className="text-slate-500 mt-1">Validation results, missing values, and data integrity scores across all tables.</p>
      </div>

      {/* Overall Quality Score */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="border-emerald-200 dark:border-emerald-800 md:col-span-1">
          <CardContent className="pt-6 text-center">
            <div className="relative inline-flex items-center justify-center">
              <svg className="w-24 h-24 -rotate-90" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="15.9155" fill="none" stroke="#e2e8f0" strokeWidth="2.5" />
                <circle cx="18" cy="18" r="15.9155" fill="none" stroke={getScoreColor(overall)}
                  strokeWidth="2.5" strokeDasharray={`${overall} ${100 - overall}`} strokeLinecap="round" />
              </svg>
              <span className="absolute text-2xl font-bold">{overall}</span>
            </div>
            <p className="text-sm font-medium mt-2">Overall Quality Score</p>
            <p className="text-xs text-slate-400">Across 8 tables</p>
          </CardContent>
        </Card>

        {[
          { label: 'Tables Passing', value: '6 / 8', icon: CheckCircle, color: 'text-emerald-600' },
          { label: 'Total Issues Found', value: '356', icon: AlertTriangle, color: 'text-amber-600' },
          { label: 'Critical Issues', value: '0', icon: ShieldCheck, color: 'text-blue-600' },
        ].map(({ label, value, icon: Icon, color }) => (
          <Card key={label}>
            <CardContent className="pt-6 flex flex-col justify-center h-full">
              <Icon className={`w-8 h-8 ${color} mb-2`} />
              <p className="text-3xl font-bold">{value}</p>
              <p className="text-sm text-slate-500 mt-1">{label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quality Score by Table */}
      <Card>
        <CardHeader><CardTitle>Data Quality Score by Table</CardTitle></CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={SCORE_BY_TABLE} margin={{ left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-slate-200 dark:stroke-slate-700" />
              <XAxis dataKey="table" tickLine={false} axisLine={false} className="text-xs" tick={{ fontSize: 11 }} />
              <YAxis domain={[60, 100]} tickLine={false} axisLine={false} className="text-xs" tickFormatter={v => `${v}%`} />
              <Tooltip formatter={(v: any) => [`${v}%`, 'Quality Score']} />
              <Bar dataKey="score" radius={[4, 4, 0, 0]} barSize={36}>
                {SCORE_BY_TABLE.map((row, i) => (
                  <Cell key={i} fill={getScoreColor(row.score)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Validation Check Table */}
      <Card>
        <CardHeader><CardTitle>Validation Check Results</CardTitle></CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-slate-50 dark:bg-slate-800/50">
                  {['Status', 'Check', 'Table', 'Severity', 'Issues'].map(h => (
                    <th key={h} className="text-left py-3 px-6 font-semibold text-slate-600 dark:text-slate-400">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {QUALITY_CHECKS.map((row, i) => (
                  <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-6"><StatusIcon status={row.status} /></td>
                    <td className="py-3 px-6 font-medium">{row.check}</td>
                    <td className="py-3 px-6 font-mono text-sm text-slate-500">{row.table}</td>
                    <td className="py-3 px-6">
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                        row.severity === 'CRITICAL' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300' :
                        row.severity === 'ERROR' ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300' :
                        row.severity === 'WARNING' ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300' :
                        'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
                      }`}>{row.severity}</span>
                    </td>
                    <td className="py-3 px-6">
                      {row.issues > 0 ? <span className="font-semibold text-red-600">{row.issues}</span> : <span className="text-emerald-600 font-semibold">0</span>}
                    </td>
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
