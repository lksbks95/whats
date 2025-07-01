import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useSettings } from '../contexts/SettingsContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Users, Building2, MessageSquare, Settings, LogOut, Phone, FileText, BookUser, LayoutDashboard
} from 'lucide-react';

const Layout = ({ children, activeTab, setActiveTab }) => {
  const { user, logout } = useAuth();
  const { settings } = useSettings();

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'contacts', label: 'Agenda', icon: BookUser },
    { id: 'conversations', label: 'Conversas', icon: MessageSquare },
    { id: 'users', label: 'Usuários', icon: Users, adminOnly: true },
    { id: 'departments', label: 'Departamentos', icon: Building2, adminOnly: true },
    { id: 'whatsapp', label: 'WhatsApp', icon: Phone, adminOnly: true },
    { id: 'settings', label: 'Configurações', icon: Settings }
  ];

  const filteredMenuItems = menuItems.filter(item => 
    !item.adminOnly || user?.role === 'admin' || user?.role === 'manager'
  );

  return (
    // --- ALTERAÇÃO 1: ESTRUTURA FLEXBOX VERTICAL PARA A PÁGINA INTEIRA ---
    <div className="flex flex-col h-screen bg-gray-50 overflow-hidden">
      {/* Header (não muda, mas agora é um filho direto do flex container) */}
      <header className="bg-white shadow-sm border-b flex-shrink-0">
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <img 
                src={settings.logo_url || "https://placehold.co/40x40/2563eb/ffffff?text=Logo"} 
                alt="Logo da Empresa" 
                className="h-10 w-10 mr-3 rounded-md"
              />
              <h1 className="text-xl font-semibold text-gray-900">
                {settings.company_name || "Sistema de Atendimento"}
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Olá, <strong>{user?.name}</strong></span>
              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                {user?.role === 'admin' ? 'Administrador' : user?.role === 'manager' ? 'Gerenciador' : 'Agente'}
              </span>
              <Button variant="outline" size="sm" onClick={logout}>
                <LogOut className="h-4 w-4 mr-2" />
                Sair
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* --- ALTERAÇÃO 2: CONTAINER PRINCIPAL QUE OCUPA O RESTO DO ESPAÇO --- */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar (agora dentro do container flex principal) */}
        <aside className="w-64 flex-shrink-0 bg-white p-4">
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="text-lg">Menu</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <nav className="space-y-1">
                  {filteredMenuItems.map((item) => {
                    const Icon = item.icon;
                    return (
                      <button
                        key={item.id}
                        onClick={() => setActiveTab(item.id)}
                        className={`w-full flex items-center px-4 py-3 text-left text-sm font-medium rounded-md transition-colors ${
                          activeTab === item.id
                            ? 'bg-blue-50 text-blue-700'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                        }`}
                      >
                        <Icon className="mr-3 h-5 w-5" />
                        {item.label}
                      </button>
                    );
                  })}
                </nav>
              </CardContent>
            </Card>
        </aside>

        {/* --- ALTERAÇÃO 3: ÁREA DE CONTEÚDO PRINCIPAL COM SCROLL PRÓPRIO --- */}
        <main className="flex-1 p-8 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
