import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import UserManagement from './components/UserManagement';
import DepartmentManagement from './components/DepartmentManagement';
import ChatInterface from './components/ChatInterface';
import WhatsAppConfig from './components/WhatsAppConfig';
import { Loader2 } from 'lucide-react';
import './App.css';

const AppContent = () => {
  const { user, loading, isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login />;
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'users':
        return <UserManagement />;
      case 'departments':
        return <DepartmentManagement />;
      case 'whatsapp':
        return <WhatsAppConfig />;
      case 'conversations':
        return <ChatInterface />;
      case 'settings':
        return (
          <div className="text-center py-8">
            <h3 className="text-lg font-semibold mb-2">Configurações</h3>
            <p className="text-gray-600">Em desenvolvimento...</p>
          </div>
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      {renderContent()}
    </Layout>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;

