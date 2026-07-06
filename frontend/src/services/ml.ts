import { apiClient } from './api';

export const mlService = {
  getModels: (): Promise<any> => apiClient.get('/ml/models'),
  
  getModelMetrics: (): Promise<any> => apiClient.get('/ml/model-metrics'),
  
  predictLead: (data: any): Promise<any> => apiClient.post('/ml/predict/lead', data),
  
  predictChurn: (data: any): Promise<any> => apiClient.post('/ml/predict/churn', data),
  
  predictRevenue: (data: any): Promise<any> => apiClient.post('/ml/predict/revenue', data),
  
  predictHealth: (data: any): Promise<any> => apiClient.post('/ml/predict/health', data),
  
  trainModels: (): Promise<any> => apiClient.post('/ml/train'),
};
