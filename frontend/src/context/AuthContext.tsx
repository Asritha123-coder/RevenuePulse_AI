import React, { createContext, useContext, useState, type ReactNode } from 'react';

type Role = 'Admin' | 'CEO' | 'Sales' | 'Marketing' | 'Analyst' | 'Viewer';

interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  avatar?: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (role?: Role) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  // Mock logged in user for demonstration purposes
  const [user, setUser] = useState<User | null>({
    id: 'u-1',
    name: 'Sarah Executive',
    email: 'sarah.ceo@revenuepulse.ai',
    role: 'CEO',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah'
  });

  const login = (role: Role = 'CEO') => {
    setUser({
      id: `u-${Math.random()}`,
      name: `Demo ${role}`,
      email: `demo.${role.toLowerCase()}@revenuepulse.ai`,
      role,
      avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${role}`
    });
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
