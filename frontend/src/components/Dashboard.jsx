import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { Users, Building2, MessageSquare, Clock, AlertCircle, Loader2 } from 'lucide-react';

const Dashboard = () => {
  const [stats, setStats] = useState({ totalUsers: 0, totalDepartments: 0, activeConversations: 0, pendingTransfers: 0 });
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsResponse, activityResponse] = await Promise.all([
          axios.get('/api/dashboard/stats'),
          axios.get('/api/activity/recent')
        ]);
        setStats(statsResponse.data.stats);
        setRecentActivity(activityResponse.data.activities);
      } catch (error) {
        console.error("Erro ao buscar dados do dashboard:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const getActivityIcon = (type) => {
    switch (type) {
      case 'USER_CREATED': return <Users className="h-4 w-4 text-blue-500" />;
      case 'CONVERSATION_TRANSFERRED': return <MessageSquare className="h-4 w-4 text-green-500" />;
      default: return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64"><Loader2 className="h-8 w-8 animate-spin text-gray-500" /></div>;
  }

  return (
    <div className="space-y-6">
      {/* ... (código dos cartões de estatísticas) ... */}

      {/* Atividade Recente com Dados Reais */}
      <Card className="col-span-3">
        <CardHeader>
          <CardTitle>Atividade Recente</CardTitle>
          <CardDescription>Últimas ações realizadas no sistema</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivity.length > 0 ? (
              recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start space-x-3">
                  <div className="mt-1">{getActivityIcon(activity.event_type)}</div>
                  <div className="flex-1 space-y-1">
                    <p className="text-sm font-medium leading-none">{activity.message}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true, locale: ptBR })} por {activity.user_name}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-center text-gray-500 py-4">Nenhuma atividade recente.</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
