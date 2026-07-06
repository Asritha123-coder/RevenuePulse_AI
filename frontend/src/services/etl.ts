import { apiClient } from './api';

export const etlService = {
  triggerPipeline: (): Promise<any> => apiClient.post('/etl/run'),
  
  getPipelineStatus: (): Promise<any> => apiClient.get('/etl/status'),
  
  getValidationReport: (): Promise<any> => apiClient.get('/etl/validation/report'),
  
  getDatabaseHealth: (): Promise<any> => apiClient.get('/etl/health'),
};
