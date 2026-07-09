import axios from 'axios';

// The base API URL configured to reach the FastAPI backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout for potentially slow ML/Analytics queries
});

// Request Interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Inject auth token here if authentication is enabled later
    const token = localStorage.getItem('revenuepulse_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor
apiClient.interceptors.response.use(
  (response) => response.data, // Unwrap the axios response and return only the payload body
  (error) => {
    // Global error handler
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);
