import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Phone, 
  CheckCircle, 
  AlertCircle, 
  Trash2,
  Plus,
  Settings,
  Key,
  Smartphone
} from 'lucide-react';

const WhatsAppConfig = () => {
  const { token } = useAuth();
  const [connections, setConnections] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [connectionData, setConnectionData] = useState({
    phone_number: '',
    access_token: '',
    webhook_verify_token: '',
    business_account_id: ''
  });

  // Buscar status das conexões
  const fetchConnections = async () => {
    try {
      const response = await fetch('/api/whatsapp/status', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      setConnections(data.connections || []);
      setIsConnected(data.is_connected);
    } catch (error) {
      console.error('Erro ao buscar conexões:', error);
    }
  };

  useEffect(() => {
    if (token) {
      fetchConnections();
    }
  }, [token]);

  // Conectar WhatsApp
  const handleConnect = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/whatsapp/connect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(connectionData)
      });

      const data = await response.json();

      if (response.ok) {
        setShowAddModal(false);
        setConnectionData({
          phone_number: '',
          access_token: '',
          webhook_verify_token: '',
          business_account_id: ''
        });
        fetchConnections();
        alert('WhatsApp conectado com sucesso!');
      } else {
        alert(data.message || 'Erro ao conectar WhatsApp');
      }
    } catch (error) {
      console.error('Erro ao conectar WhatsApp:', error);
      alert('Erro ao conectar WhatsApp');
    } finally {
      setLoading(false);
    }
  };

  // Desconectar WhatsApp
  const handleDisconnect = async (connectionId) => {
    if (!confirm('Tem certeza que deseja desconectar este número?')) return;

    try {
      const response = await fetch(`/api/whatsapp/disconnect/${connectionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        fetchConnections();
        alert('WhatsApp desconectado com sucesso!');
      } else {
        alert('Erro ao desconectar WhatsApp');
      }
    } catch (error) {
      console.error('Erro ao desconectar WhatsApp:', error);
      alert('Erro ao desconectar WhatsApp');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Configuração WhatsApp</h2>
          <p className="text-muted-foreground">
            Configure a integração com WhatsApp Business API
          </p>
        </div>
        <Button onClick={() => setShowAddModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Conectar Número
        </Button>
      </div>

      {/* Status Geral */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Phone className="h-5 w-5" />
            <span>Status da Integração</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            {isConnected ? (
              <>
                <CheckCircle className="h-8 w-8 text-green-500" />
                <div>
                  <h3 className="font-semibold text-green-700">WhatsApp Conectado</h3>
                  <p className="text-sm text-gray-600">
                    {connections.length} número{connections.length !== 1 ? 's' : ''} conectado{connections.length !== 1 ? 's' : ''}
                  </p>
                </div>
              </>
            ) : (
              <>
                <AlertCircle className="h-8 w-8 text-yellow-500" />
                <div>
                  <h3 className="font-semibold text-yellow-700">WhatsApp Não Conectado</h3>
                  <p className="text-sm text-gray-600">
                    Nenhum número conectado. Configure uma conexão para começar.
                  </p>
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Lista de Conexões */}
      <Card>
        <CardHeader>
          <CardTitle>Números Conectados</CardTitle>
        </CardHeader>
        <CardContent>
          {connections.length > 0 ? (
            <div className="space-y-4">
              {connections.map((connection) => (
                <div
                  key={connection.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
                      <Smartphone className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold">{connection.phone_number}</h3>
                      <p className="text-sm text-gray-500">
                        Business Account: {connection.business_account_id}
                      </p>
                      <p className="text-xs text-gray-400">
                        Conectado em: {new Date(connection.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={connection.is_active ? 'default' : 'secondary'}>
                      {connection.is_active ? 'Ativo' : 'Inativo'}
                    </Badge>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDisconnect(connection.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Phone className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Nenhum número conectado
              </h3>
              <p className="text-gray-500 mb-4">
                Conecte um número do WhatsApp Business para começar a receber mensagens
              </p>
              <Button onClick={() => setShowAddModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Conectar Primeiro Número
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Instruções */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>Como Configurar</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-semibold text-blue-900 mb-2">Pré-requisitos</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Conta do WhatsApp Business API</li>
              <li>• Token de acesso válido</li>
              <li>• Business Account ID</li>
              <li>• Token de verificação do webhook</li>
            </ul>
          </div>

          <div className="bg-yellow-50 p-4 rounded-lg">
            <h4 className="font-semibold text-yellow-900 mb-2">Configuração do Webhook</h4>
            <p className="text-sm text-yellow-800 mb-2">
              Configure o webhook no Facebook Developers com a seguinte URL:
            </p>
            <code className="bg-yellow-100 px-2 py-1 rounded text-sm">
              {window.location.origin}/webhook
            </code>
          </div>

          <div className="bg-green-50 p-4 rounded-lg">
            <h4 className="font-semibold text-green-900 mb-2">Teste de Conexão</h4>
            <p className="text-sm text-green-800">
              Após conectar, envie uma mensagem de teste para verificar se a integração está funcionando corretamente.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Modal de Adicionar Conexão */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-96 max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle>Conectar WhatsApp Business</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  <Smartphone className="h-4 w-4 inline mr-1" />
                  Número do WhatsApp
                </label>
                <Input
                  value={connectionData.phone_number}
                  onChange={(e) => setConnectionData(prev => ({
                    ...prev,
                    phone_number: e.target.value
                  }))}
                  placeholder="+5511999999999"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  <Key className="h-4 w-4 inline mr-1" />
                  Token de Acesso
                </label>
                <Input
                  type="password"
                  value={connectionData.access_token}
                  onChange={(e) => setConnectionData(prev => ({
                    ...prev,
                    access_token: e.target.value
                  }))}
                  placeholder="EAAxxxxxxxxxx..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Business Account ID
                </label>
                <Input
                  value={connectionData.business_account_id}
                  onChange={(e) => setConnectionData(prev => ({
                    ...prev,
                    business_account_id: e.target.value
                  }))}
                  placeholder="123456789012345"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Token de Verificação do Webhook
                </label>
                <Input
                  value={connectionData.webhook_verify_token}
                  onChange={(e) => setConnectionData(prev => ({
                    ...prev,
                    webhook_verify_token: e.target.value
                  }))}
                  placeholder="meu_token_secreto"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <Button
                  variant="outline"
                  onClick={() => setShowAddModal(false)}
                  disabled={loading}
                >
                  Cancelar
                </Button>
                <Button
                  onClick={handleConnect}
                  disabled={loading || !connectionData.phone_number || !connectionData.access_token}
                >
                  {loading ? 'Conectando...' : 'Conectar'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default WhatsAppConfig;

