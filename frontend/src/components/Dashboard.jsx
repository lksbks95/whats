import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Users, 
  Building2, 
  MessageSquare, 
  Phone,
  CheckCircle,
  Clock,
  AlertCircle
} from 'lucide-react';

const Dashboard = () => {
  // Dados mockados para demonstração
  const stats = {
    totalUsers: 12,
    totalDepartments: 3,
    activeConversations: 8,
    pendingTransfers: 2
  };

  const recentActivity = [
    { id: 1, type: 'user_created', message: 'Novo usuário João Silva criado', time: '2 min atrás' },
    { id: 2, type: 'conversation_transferred', message: 'Conversa transferida para Suporte', time: '5 min atrás' },
    { id: 3, type: 'department_created', message: 'Departamento Marketing criado', time: '1 hora atrás' },
    { id: 4, type: 'whatsapp_connected', message: 'WhatsApp conectado com sucesso', time: '2 horas atrás' }
  ];

  const getActivityIcon = (type) => {
    switch (type) {
      case 'user_created':
        return <Users className="h-4 w-4 text-blue-500" />;
      case 'conversation_transferred':
        return <MessageSquare className="h-4 w-4 text-green-500" />;
      case 'department_created':
        return <Building2 className="h-4 w-4 text-purple-500" />;
      case 'whatsapp_connected':
        return <Phone className="h-4 w-4 text-green-600" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground">
          Visão geral do sistema de atendimento WhatsApp
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Usuários</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalUsers}</div>
            <p className="text-xs text-muted-foreground">
              +2 desde o último mês
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Departamentos</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalDepartments}</div>
            <p className="text-xs text-muted-foreground">
              Vendas, Suporte, Marketing
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conversas Ativas</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeConversations}</div>
            <p className="text-xs text-muted-foreground">
              +3 desde ontem
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Transferências Pendentes</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pendingTransfers}</div>
            <p className="text-xs text-muted-foreground">
              Aguardando aprovação
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Status do Sistema */}
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Status do Sistema</CardTitle>
            <CardDescription>
              Estado atual dos componentes do sistema
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Backend API</span>
              </div>
              <Badge variant="default">Online</Badge>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Banco de Dados</span>
              </div>
              <Badge variant="default">Conectado</Badge>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-yellow-500" />
                <span>WhatsApp Business API</span>
              </div>
              <Badge variant="secondary">Configuração Pendente</Badge>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Socket.IO</span>
              </div>
              <Badge variant="default">Ativo</Badge>
            </div>
          </CardContent>
        </Card>

        {/* Atividade Recente */}
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Atividade Recente</CardTitle>
            <CardDescription>
              Últimas ações no sistema
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start space-x-3">
                  <div className="mt-1">
                    {getActivityIcon(activity.type)}
                  </div>
                  <div className="flex-1 space-y-1">
                    <p className="text-sm font-medium leading-none">
                      {activity.message}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {activity.time}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Próximos Passos */}
      <Card>
        <CardHeader>
          <CardTitle>Próximos Passos</CardTitle>
          <CardDescription>
            Configure seu sistema para começar a usar
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div className="flex items-center space-x-3 p-4 border rounded-lg">
              <Phone className="h-8 w-8 text-green-600" />
              <div>
                <h4 className="font-semibold">Conectar WhatsApp</h4>
                <p className="text-sm text-muted-foreground">
                  Configure a integração com WhatsApp Business
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-4 border rounded-lg">
              <Users className="h-8 w-8 text-blue-600" />
              <div>
                <h4 className="font-semibold">Adicionar Agentes</h4>
                <p className="text-sm text-muted-foreground">
                  Crie contas para sua equipe de atendimento
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-4 border rounded-lg">
              <Building2 className="h-8 w-8 text-purple-600" />
              <div>
                <h4 className="font-semibold">Organizar Departamentos</h4>
                <p className="text-sm text-muted-foreground">
                  Configure departamentos para organizar atendimentos
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;

