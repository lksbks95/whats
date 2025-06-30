import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// --- CORREÇÃO DE ESTILOS ---
// Adicione a importação para os seus arquivos de estilo.
// Se você tiver um arquivo de estilos principal para este componente, importe-o aqui.
import './App.css'; // <--- ADICIONE ESTA LINHA (ajuste o nome do ficheiro se for diferente)

// --- CORREÇÃO AQUI ---
// Os caminhos de importação foram atualizados de './pages/' para './components/'
// para corresponder à sua estrutura de ficheiros.
import Login from './components/Login';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import UserManagement from './components/UserManagement';
import DepartmentManagement from './components/DepartmentManagement';
import WhatsAppConfig from './components/WhatsAppConfig';
import ChatInterface from './components/ChatInterface';
import Settings from './components/Settings';
import ContactManagement from './components/ContactManagement';

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
      case 'contacts':
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
