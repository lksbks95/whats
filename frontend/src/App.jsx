import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Importa todos os componentes de página que o seu sistema usa
import Login from './pages/Login';
import Layout from './pages/Layout';
import Dashboard from './pages/Dashboard';
import UserManagement from './pages/UserManagement';
import DepartmentManagement from './pages/DepartmentManagement';
import WhatsAppConfig from './pages/WhatsAppConfig';
import ChatInterface from './pages/ChatInterface';
import Settings from './pages/Settings';
import ContactManagement from './pages/ContactManagement'; // A nossa nova página de Agenda

/**
 * Componente principal que gere a navegação e o estado.
 */
function AppContent() {
  const { user } = useAuth();
  // O estado 'activeTab' controla qual página é mostrada. Começa no 'dashboard'.
  const [activeTab, setActiveTab] = useState('dashboard');

  // Função que decide qual componente renderizar com base no separador ativo.
  const renderActiveComponent = () => {
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
        return <Settings />;
      case 'contacts': // Adicionado o caso para a Agenda
        return <ContactManagement setActiveTab={setActiveTab} />;
      default:
        return <Dashboard />; // Se algo der errado, mostra o dashboard
    }
  };

  // Se não houver utilizador logado, mostra a página de Login.
  if (!user) {
    return <Login />;
  }

  // Se houver um utilizador, mostra o Layout principal com o conteúdo correto.
  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      {renderActiveComponent()}
    </Layout>
  );
}

// O componente final que envolve toda a aplicação com o provedor de autenticação.
export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
