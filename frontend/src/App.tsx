import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Layout
import AppLayout from '@/layouts/AppLayout';

// Fallback Loader
const PageLoader = () => (
  <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-600"></div>
  </div>
);

// Lazy Loaded Pages
const Dashboard = React.lazy(() => import('@/pages/Dashboard'));
const RevenueIntelligence = React.lazy(() => import('@/pages/RevenueIntelligence'));
const CustomerIntelligence = React.lazy(() => import('@/pages/CustomerIntelligence'));
const SalesIntelligence = React.lazy(() => import('@/pages/SalesIntelligence'));
const MarketingIntelligence = React.lazy(() => import('@/pages/MarketingIntelligence'));
const ProductIntelligence = React.lazy(() => import('@/pages/ProductIntelligence'));
const SupportIntelligence = React.lazy(() => import('@/pages/SupportIntelligence'));
const AccountHealth = React.lazy(() => import('@/pages/AccountHealth'));
const MLIntelligence = React.lazy(() => import('@/pages/MLIntelligence'));
const AICopilot = React.lazy(() => import('@/pages/AICopilot'));
const ETLMonitor = React.lazy(() => import('@/pages/ETLMonitor'));
const DataQuality = React.lazy(() => import('@/pages/DataQuality'));
const ReportCenter = React.lazy(() => import('@/pages/ReportCenter'));
const Settings = React.lazy(() => import('@/pages/Settings'));

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          
          <Route path="dashboard" element={
            <Suspense fallback={<PageLoader />}><Dashboard /></Suspense>
          } />
          
          <Route path="intelligence">
            <Route path="revenue" element={<Suspense fallback={<PageLoader />}><RevenueIntelligence /></Suspense>} />
            <Route path="sales" element={<Suspense fallback={<PageLoader />}><SalesIntelligence /></Suspense>} />
            <Route path="marketing" element={<Suspense fallback={<PageLoader />}><MarketingIntelligence /></Suspense>} />
            <Route path="customer" element={<Suspense fallback={<PageLoader />}><CustomerIntelligence /></Suspense>} />
            <Route path="product" element={<Suspense fallback={<PageLoader />}><ProductIntelligence /></Suspense>} />
            <Route path="support" element={<Suspense fallback={<PageLoader />}><SupportIntelligence /></Suspense>} />
          </Route>
          
          <Route path="health" element={<Suspense fallback={<PageLoader />}><AccountHealth /></Suspense>} />
          <Route path="ml" element={<Suspense fallback={<PageLoader />}><MLIntelligence /></Suspense>} />
          <Route path="copilot" element={<Suspense fallback={<PageLoader />}><AICopilot /></Suspense>} />
          
          <Route path="data">
            <Route path="etl" element={<Suspense fallback={<PageLoader />}><ETLMonitor /></Suspense>} />
            <Route path="quality" element={<Suspense fallback={<PageLoader />}><DataQuality /></Suspense>} />
          </Route>
          
          <Route path="reports" element={<Suspense fallback={<PageLoader />}><ReportCenter /></Suspense>} />
          <Route path="settings" element={<Suspense fallback={<PageLoader />}><Settings /></Suspense>} />
          
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Routes>
      
      <ToastContainer position="bottom-right" theme="colored" />
    </>
  );
}

export default App;
