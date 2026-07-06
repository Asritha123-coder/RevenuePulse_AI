import { apiClient } from './api';

export interface KPIResponse {
  status: string;
  data: {
    total_revenue: number;
    total_mrr: number;
    total_arr: number;
    revenue_growth_percentage: number;
    pipeline_value: number;
    total_customers: number;
    won_opportunities: number;
    average_csat: number;
  };
}

export interface RevenueTrendResponse {
  status: string;
  data: {
    revenue_by_month: Record<string, number>;
  };
}

export interface RegionDistributionResponse {
  status: string;
  data: {
    country_distribution: Record<string, number>;
  };
}

export interface IndustryDistributionResponse {
  status: string;
  data: {
    industry_distribution: Record<string, number>;
  };
}

export interface PipelineFunnelResponse {
  status: string;
  data: {
    total_opportunities: number;
    status_distribution: Record<string, number>;
  };
}

export const analyticsService = {
  getKPIs: (): Promise<KPIResponse> => apiClient.get('/analytics/kpis'),
  
  getRevenueTrend: (): Promise<RevenueTrendResponse> => apiClient.get('/analytics/revenue/trend'),
  
  getRevenueByRegion: (): Promise<RegionDistributionResponse> => apiClient.get('/analytics/revenue/geography'),
  
  getRevenueByIndustry: (): Promise<IndustryDistributionResponse> => apiClient.get('/analytics/revenue/industry'),
  
  getPipelineFunnel: (): Promise<PipelineFunnelResponse> => apiClient.get('/analytics/sales/pipeline'),
  
  getDashboardSummary: (): Promise<any> => apiClient.get('/analytics/dashboard/summary'),
  
  triggerReportGeneration: (): Promise<any> => apiClient.post('/analytics/reports/generate'),
};
