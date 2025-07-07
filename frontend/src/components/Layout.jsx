import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Users, 
  Building2, 
  MessageSquare, 
  Settings, 
  LogOut,
  Phone,
  FileText
} from 'lucide-react';

const Layout = ({ children, activeTab, setActiveTab }) => {
  const { user, logout } = useAuth();

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: MessageSquare },
    { id: 'users', label: 'Usuários', icon: Users, adminOnly: true },
    { id: 'departments', label: 'Departamentos', icon: Building2, adminOnly: true },
    { id: 'whatsapp', label: 'WhatsApp', icon: Phone, adminOnly: true },
    { id: 'conversations', label: 'Conversas', icon: FileText },
    { id: 'settings', label: 'Configurações', icon: Settings }
  ];

  const filteredMenuItems = menuItems.filter(item => 
    !item.adminOnly || user?.role === 'admin' || user?.role === 'manager'
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <MessageSquare className="h-8 w-8 text-green-600 mr-3" />
              <h1 className="text-xl font-semibold text-gray-900">
                Sistema de Atendimento WhatsApp
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Olá, <strong>{user?.name}</strong>
              </span>
              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                {user?.role === 'admin' ? 'Administrador' : 
                 user?.role === 'manager' ? 'Gerenciador' : 'Agente'}
              </span>
              <Button variant="outline" size="sm" onClick={logout}>
                <LogOut className="h-4 w-4 mr-2" />
                Sair
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Sidebar */}
          <div className="w-64 flex-shrink-0">
            <Card>
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
                        className={`w-full flex items-center px-4 py-3 text-left text-sm font-medium rounded-none transition-colors ${
                          activeTab === item.id
                            ? 'bg-green-50 text-green-700 border-r-2 border-green-600'
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
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Layout;

