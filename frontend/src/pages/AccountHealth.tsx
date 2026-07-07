import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { mlService } from '@/services/ml';
import { CheckCircle, AlertTriangle, XCircle, Activity } from 'lucide-react';

interface HealthAccount {
  account_id: string;
  company_name: string;
  health_category: 'Healthy' | 'Medium Risk' | 'Critical';
  health_score: number;
  industry: string;
  monthly_spend: number;
}

const MOCK_ACCOUNTS: HealthAccount[] = [
  { account_id: 'ACC-001', company_name: 'Nexus Health Systems', health_category: 'Healthy', health_score: 87, industry: 'Healthcare', monthly_spend: 12400 },
  { account_id: 'ACC-002', company_name: 'Pinnacle Finance Corp', health_category: 'Healthy', health_score: 92, industry: 'Finance', monthly_spend: 18900 },
  { account_id: 'ACC-003', company_name: 'RetailEdge Solutions', health_category: 'Medium Risk', health_score: 61, industry: 'Retail', monthly_spend: 5600 },
  { account_id: 'ACC-004', company_name: 'CloudTech Partners', health_category: 'Critical', health_score: 28, industry: 'Technology', monthly_spend: 2100 },
  { account_id: 'ACC-005', company_name: 'GreenEnergy Inc.', health_category: 'Healthy', health_score: 79, industry: 'Energy', monthly_spend: 9800 },
  { account_id: 'ACC-006', company_name: 'EduGrowth Academy', health_category: 'Medium Risk', health_score: 55, industry: 'Education', monthly_spend: 3200 },
  { account_id: 'ACC-007', company_name: 'MediCare Analytics', health_category: 'Critical', health_score: 19, industry: 'Healthcare', monthly_spend: 1400 },
  { account_id: 'ACC-008', company_name: 'Steel Manufacturing Co.', health_category: 'Healthy', health_score: 82, industry: 'Manufacturing', monthly_spend: 14500 },
];

function HealthBadge({ category }: { category: HealthAccount['health_category'] }) {
  const cfg = {
    'Healthy': { icon: CheckCircle, bg: 'bg-emerald-100 dark:bg-emerald-900/30', text: 'text-emerald-700 dark:text-emerald-300' },
    'Medium Risk': { icon: AlertTriangle, bg: 'bg-amber-100 dark:bg-amber-900/30', text: 'text-amber-700 dark:text-amber-300' },
    'Critical': { icon: XCircle, bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-300' },
  }[category];

  const Icon = cfg.icon;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${cfg.bg} ${cfg.text}`}>
      <Icon className="w-3 h-3" />
      {category}
    </span>
  );
}

function ScoreBar({ score }: { score: number }) {
  const color = score >= 75 ? 'bg-emerald-500' : score >= 50 ? 'bg-amber-500' : 'bg-red-500';
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${score}%` }} />
      </div>
      <span className="text-xs font-semibold w-8 text-right">{score}</span>
    </div>
  );
}

export default function AccountHealth() {
  const healthy = MOCK_ACCOUNTS.filter(a => a.health_category === 'Healthy').length;
  const medRisk = MOCK_ACCOUNTS.filter(a => a.health_category === 'Medium Risk').length;
  const critical = MOCK_ACCOUNTS.filter(a => a.health_category === 'Critical').length;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Account Health</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">ML-powered customer health scoring and risk segmentation.</p>
      </div>

      {/* Summary KPIs */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-emerald-200 dark:border-emerald-800">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600"><CheckCircle className="w-5 h-5" /></div>
              <div>
                <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Healthy Accounts</p>
                <p className="text-3xl font-bold text-emerald-600">{healthy}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-amber-200 dark:border-amber-800">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-amber-50 dark:bg-amber-900/20 text-amber-600"><AlertTriangle className="w-5 h-5" /></div>
              <div>
                <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Medium Risk</p>
                <p className="text-3xl font-bold text-amber-600">{medRisk}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-red-200 dark:border-red-800">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600"><XCircle className="w-5 h-5" /></div>
              <div>
                <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Critical Accounts</p>
                <p className="text-3xl font-bold text-red-600">{critical}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Account Table */}
      <Card>
        <CardHeader><CardTitle>Account Health Overview</CardTitle></CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-slate-50 dark:bg-slate-800/50">
                  <th className="text-left py-3 px-6 font-semibold text-slate-600 dark:text-slate-400 dark:text-slate-400">Account</th>
                  <th className="text-left py-3 px-4 font-semibold text-slate-600 dark:text-slate-400 dark:text-slate-400">Industry</th>
                  <th className="text-left py-3 px-4 font-semibold text-slate-600 dark:text-slate-400 dark:text-slate-400">Status</th>
                  <th className="text-left py-3 px-4 font-semibold text-slate-600 dark:text-slate-400 dark:text-slate-400 min-w-[160px]">Health Score</th>
                  <th className="text-left py-3 px-4 font-semibold text-slate-600 dark:text-slate-400 dark:text-slate-400">MRR</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {MOCK_ACCOUNTS.map((acc) => (
                  <tr key={acc.account_id} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                    <td className="py-4 px-6">
                      <div>
                        <div className="font-medium">{acc.company_name}</div>
                        <div className="text-xs text-slate-400 dark:text-slate-400">{acc.account_id}</div>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-slate-600 dark:text-slate-400 dark:text-slate-400">{acc.industry}</td>
                    <td className="py-4 px-4"><HealthBadge category={acc.health_category} /></td>
                    <td className="py-4 px-4 w-48"><ScoreBar score={acc.health_score} /></td>
                    <td className="py-4 px-4 font-semibold">${acc.monthly_spend.toLocaleString()}</td>
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
