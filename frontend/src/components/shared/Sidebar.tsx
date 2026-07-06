import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  TrendingUp, 
  Users, 
  Target, 
  Megaphone, 
  Box, 
  LifeBuoy, 
  Activity, 
  Brain, 
  Bot, 
  Database, 
  ShieldCheck, 
  FileBarChart,
  Settings
} from 'lucide-react';
import { cn } from '@/utils/cn';

const NAVIGATION_GROUPS = [
  {
    title: 'Overview',
    items: [
      { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    ]
  },
  {
    title: 'Intelligence',
    items: [
      { name: 'Revenue', path: '/intelligence/revenue', icon: TrendingUp },
      { name: 'Sales', path: '/intelligence/sales', icon: Target },
      { name: 'Marketing', path: '/intelligence/marketing', icon: Megaphone },
      { name: 'Customer', path: '/intelligence/customer', icon: Users },
      { name: 'Product', path: '/intelligence/product', icon: Box },
      { name: 'Support', path: '/intelligence/support', icon: LifeBuoy },
    ]
  },
  {
    title: 'Advanced AI',
    items: [
      { name: 'Account Health', path: '/health', icon: Activity },
      { name: 'ML Intelligence', path: '/ml', icon: Brain },
      { name: 'AI Copilot', path: '/copilot', icon: Bot },
    ]
  },
  {
    title: 'Data & Reports',
    items: [
      { name: 'ETL Monitor', path: '/data/etl', icon: Database },
      { name: 'Data Quality', path: '/data/quality', icon: ShieldCheck },
      { name: 'Reports', path: '/reports', icon: FileBarChart },
    ]
  }
];

export function Sidebar() {
  return (
    <aside className="w-64 flex-shrink-0 bg-sidebar-bg text-sidebar-fg hidden md:flex flex-col border-r border-slate-800">
      <div className="h-16 flex items-center px-6 border-b border-slate-800">
        <Activity className="w-6 h-6 text-brand-500 mr-2" />
        <span className="font-bold text-lg tracking-tight">RevenuePulse <span className="text-brand-500">AI</span></span>
      </div>
      
      <div className="flex-1 overflow-y-auto py-4 scrollbar-thin scrollbar-thumb-slate-700">
        {NAVIGATION_GROUPS.map((group, i) => (
          <div key={i} className="mb-6">
            <h3 className="px-6 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              {group.title}
            </h3>
            <ul className="space-y-1">
              {group.items.map((item) => (
                <li key={item.path}>
                  <NavLink
                    to={item.path}
                    className={({ isActive }) =>
                      cn(
                        "flex items-center px-6 py-2 text-sm font-medium transition-colors border-l-2",
                        isActive
                          ? "bg-sidebar-hover text-white border-brand-500"
                          : "text-slate-300 border-transparent hover:bg-sidebar-hover hover:text-white"
                      )
                    }
                  >
                    <item.icon className="w-4 h-4 mr-3" />
                    {item.name}
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-slate-800">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            cn(
              "flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors",
              isActive
                ? "bg-sidebar-hover text-white"
                : "text-slate-300 hover:bg-sidebar-hover hover:text-white"
            )
          }
        >
          <Settings className="w-4 h-4 mr-3" />
          Settings
        </NavLink>
      </div>
    </aside>
  );
}
