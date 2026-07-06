import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { mlService } from '@/services/ml';
import { Brain, Target, TrendingUp, Activity, RefreshCw } from 'lucide-react';
import { toast } from 'react-toastify';

const MODEL_CARDS = [
  {
    key: 'lead_scoring',
    title: 'Lead Scoring',
    icon: Target,
    description: 'Classifies opportunity outcomes (Won / Lost) using product signals.',
    color: 'text-blue-600',
    bg: 'bg-blue-50 dark:bg-blue-900/20',
    algorithm: 'Gradient Boosting',
  },
  {
    key: 'churn_model',
    title: 'Churn Prediction',
    icon: Activity,
    description: 'Detects at-risk subscriptions based on usage patterns and support load.',
    color: 'text-red-600',
    bg: 'bg-red-50 dark:bg-red-900/20',
    algorithm: 'Logistic Regression',
  },
  {
    key: 'revenue_forecast',
    title: 'Revenue Forecast',
    icon: TrendingUp,
    description: 'Projects future MRR from historical revenue signals using regression.',
    color: 'text-emerald-600',
    bg: 'bg-emerald-50 dark:bg-emerald-900/20',
    algorithm: 'Gradient Boosting Regressor',
  },
  {
    key: 'account_health',
    title: 'Account Health',
    icon: Brain,
    description: 'Scores customer health as a continuous index using engagement features.',
    color: 'text-violet-600',
    bg: 'bg-violet-50 dark:bg-violet-900/20',
    algorithm: 'Random Forest Regressor',
  },
];

export default function MLIntelligence() {
  const { data: metricsData, isLoading, refetch } = useQuery({
    queryKey: ['model-metrics'],
    queryFn: mlService.getModelMetrics,
  });

  const { data: modelsData } = useQuery({
    queryKey: ['model-list'],
    queryFn: mlService.getModels,
  });

  const metrics = metricsData?.data || {};

  const handleRetrain = async () => {
    try {
      await mlService.trainModels();
      toast.success('Model retraining triggered successfully! This runs in the background.');
    } catch {
      toast.error('Failed to trigger model retraining.');
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">ML Intelligence</h1>
          <p className="text-slate-500 mt-1">Model performance, accuracy metrics, and prediction engines.</p>
        </div>
        <Button onClick={handleRetrain} variant="outline" className="flex items-center gap-2">
          <RefreshCw className="w-4 h-4" />
          Retrain Models
        </Button>
      </div>

      {/* Model Cards */}
      <div className="grid gap-6 md:grid-cols-2">
        {MODEL_CARDS.map(({ key, title, icon: Icon, description, color, bg, algorithm }) => {
          const m = metrics[key] || {};
          const accuracy = m.metrics?.accuracy ? `${(m.metrics.accuracy * 100).toFixed(1)}%` : 
                          m.metrics?.r2 !== undefined ? `R² ${m.metrics.r2.toFixed(3)}` : 'N/A';
          const f1 = m.metrics?.f1 ? `${(m.metrics.f1 * 100).toFixed(1)}%` :
                     m.metrics?.rmse ? `RMSE ${m.metrics.rmse.toFixed(2)}` : 'N/A';
          const roc = m.metrics?.roc_auc ? `${(m.metrics.roc_auc * 100).toFixed(1)}%` : '—';

          return (
            <Card key={key} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-3">
                  <div className={`p-2.5 rounded-lg ${bg} ${color}`}><Icon className="w-5 h-5" /></div>
                  <div>
                    <CardTitle>{title}</CardTitle>
                    <CardDescription>{algorithm}</CardDescription>
                  </div>
                  {m.active_version && (
                    <span className="ml-auto text-xs bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300 font-semibold px-2 py-0.5 rounded-full">
                      {m.active_version}
                    </span>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-slate-500 mb-4">{description}</p>
                {isLoading ? (
                  <div className="grid grid-cols-3 gap-3">
                    {[1, 2, 3].map(i => <div key={i} className="h-12 bg-slate-100 dark:bg-slate-800 animate-pulse rounded-lg" />)}
                  </div>
                ) : (
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { label: 'Accuracy / R²', value: accuracy },
                      { label: 'F1 / RMSE', value: f1 },
                      { label: 'ROC-AUC', value: roc },
                    ].map(({ label, value }) => (
                      <div key={label} className="text-center p-2 rounded-lg bg-slate-50 dark:bg-slate-800">
                        <div className="text-lg font-bold">{value}</div>
                        <div className="text-xs text-slate-400 mt-0.5">{label}</div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Feature Importance Radar */}
      <Card>
        <CardHeader>
          <CardTitle>Model Feature Importance (Conceptual Radar)</CardTitle>
          <CardDescription>Relative signal strength across feature groups used by all models.</CardDescription>
        </CardHeader>
        <CardContent className="flex justify-center">
          <ResponsiveContainer width="100%" height={320}>
            <RadarChart data={[
              { feature: 'Revenue Signals', lead: 88, churn: 72, health: 65 },
              { feature: 'Usage Patterns', lead: 70, churn: 92, health: 88 },
              { feature: 'Support Load', lead: 45, churn: 85, health: 76 },
              { feature: 'Engagement', lead: 60, churn: 80, health: 90 },
              { feature: 'Contract Value', lead: 95, churn: 60, health: 70 },
              { feature: 'Deal History', lead: 90, churn: 40, health: 55 },
            ]}>
              <PolarGrid className="stroke-slate-200 dark:stroke-slate-700" />
              <PolarAngleAxis dataKey="feature" className="text-xs" />
              <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
              <Radar name="Lead Scoring" dataKey="lead" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.15} strokeWidth={2} />
              <Radar name="Churn" dataKey="churn" stroke="#ef4444" fill="#ef4444" fillOpacity={0.15} strokeWidth={2} />
              <Radar name="Account Health" dataKey="health" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.15} strokeWidth={2} />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
