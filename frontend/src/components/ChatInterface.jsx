import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Send, 
  Paperclip, 
  Phone, 
  User, 
  Clock,
  ArrowRight,
  Download,
  Image,
  FileText,
  Volume2
} from 'lucide-react';
import io from 'socket.io-client';

const ChatInterface = () => {
  const { user, token } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [typingUsers, setTypingUsers] = useState([]);
  const [socket, setSocket] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [users, setUsers] = useState([]);
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [transferData, setTransferData] = useState({
    to_department_id: '',
    to_agent_id: '',
    reason: ''
  });
  const [uploadingFile, setUploadingFile] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  // Conectar ao Socket.IO
  useEffect(() => {
    if (token) {
      const newSocket = io(window.location.origin, {
        auth: { token }
      });

      newSocket.on('connect', () => {
        console.log('Conectado ao servidor Socket.IO');
      });

      newSocket.on('new_message', (data) => {
        if (selectedConversation && data.conversation_id === selectedConversation.id) {
          setMessages(prev => [...prev, data.message]);
        }
        // Atualizar lista de conversas
        fetchConversations();
      });

      newSocket.on('conversation_transferred', (data) => {
        if (selectedConversation && data.conversation_id === selectedConversation.id) {
          fetchConversationDetails(selectedConversation.id);
        }
        fetchConversations();
      });

      newSocket.on('user_typing', (data) => {
        if (selectedConversation && data.conversation_id === selectedConversation.id) {
          setTypingUsers(prev => [...prev.filter(u => u !== data.user_name), data.user_name]);
        }
      });

      newSocket.on('user_stop_typing', (data) => {
        if (selectedConversation && data.conversation_id === selectedConversation.id) {
          setTypingUsers(prev => prev.filter(u => u !== data.user_name));
        }
      });

      setSocket(newSocket);

      return () => {
        newSocket.disconnect();
      };
    }
  }, [token, selectedConversation]);

  // Buscar conversas
  const fetchConversations = async () => {
    try {
      const response = await fetch('/api/conversations', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      setConversations(data.conversations || []);
    } catch (error) {
      console.error('Erro ao buscar conversas:', error);
    }
  };

  // Buscar detalhes da conversa
  const fetchConversationDetails = async (conversationId) => {
    try {
      const response = await fetch(`/api/conversations/${conversationId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      setSelectedConversation(data.conversation);
      setMessages(data.messages || []);
      
      // Entrar na sala da conversa
      if (socket) {
        socket.emit('join_conversation', { conversation_id: conversationId });
      }
    } catch (error) {
      console.error('Erro ao buscar detalhes da conversa:', error);
    }
  };

  // Buscar departamentos e usuários
  const fetchDepartmentsAndUsers = async () => {
    try {
      const [deptResponse, usersResponse] = await Promise.all([
        fetch('/api/departments', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('/api/users', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);
      
      const deptData = await deptResponse.json();
      const usersData = await usersResponse.json();
      
      setDepartments(deptData.departments || []);
      setUsers(usersData.users || []);
    } catch (error) {
      console.error('Erro ao buscar departamentos e usuários:', error);
    }
  };

  useEffect(() => {
    if (token) {
      fetchConversations();
      fetchDepartmentsAndUsers();
    }
  }, [token]);

  // Scroll automático para última mensagem
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Enviar mensagem
  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation) return;

    try {
      const response = await fetch(`/api/conversations/${selectedConversation.id}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          content: newMessage,
          message_type: 'text'
        })
      });

      if (response.ok) {
        setNewMessage('');
        // Parar de indicar que está digitando
        if (socket) {
          socket.emit('stop_typing', {
            conversation_id: selectedConversation.id,
            user_name: user.name
          });
        }
        // Recarregar mensagens
        fetchConversationDetails(selectedConversation.id);
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
    }
  };

  // Indicar que está digitando
  const handleTyping = () => {
    if (!socket || !selectedConversation) return;

    if (!isTyping) {
      setIsTyping(true);
      socket.emit('typing', {
        conversation_id: selectedConversation.id,
        user_name: user.name
      });
    }

    // Limpar timeout anterior
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Parar de indicar digitação após 3 segundos
    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
      socket.emit('stop_typing', {
        conversation_id: selectedConversation.id,
        user_name: user.name
      });
    }, 3000);
  };

  // Upload de arquivo
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || !selectedConversation) return;

    setUploadingFile(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const uploadResponse = await fetch('/api/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const uploadData = await uploadResponse.json();

      if (uploadResponse.ok) {
        // Enviar mensagem com arquivo
        const messageResponse = await fetch(`/api/conversations/${selectedConversation.id}/messages`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            content: `Arquivo enviado: ${uploadData.original_name}`,
            message_type: uploadData.file_type,
            file_path: uploadData.file_path
          })
        });

        if (messageResponse.ok) {
          fetchConversationDetails(selectedConversation.id);
        }
      }
    } catch (error) {
      console.error('Erro ao fazer upload:', error);
    } finally {
      setUploadingFile(false);
      event.target.value = '';
    }
  };

  // Transferir conversa
  const handleTransfer = async () => {
    if (!selectedConversation || !transferData.to_department_id) return;

    try {
      const response = await fetch(`/api/conversations/${selectedConversation.id}/transfer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(transferData)
      });

      if (response.ok) {
        setShowTransferModal(false);
        setTransferData({ to_department_id: '', to_agent_id: '', reason: '' });
        fetchConversationDetails(selectedConversation.id);
        fetchConversations();
      }
    } catch (error) {
      console.error('Erro ao transferir conversa:', error);
    }
  };

  // Renderizar ícone do tipo de arquivo
  const renderFileIcon = (messageType) => {
    switch (messageType) {
      case 'image':
        return <Image className="h-4 w-4" />;
      case 'document':
        return <FileText className="h-4 w-4" />;
      case 'audio':
        return <Volume2 className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  // Filtrar usuários por departamento selecionado
  const filteredUsers = users.filter(u => 
    transferData.to_department_id ? u.department_id === parseInt(transferData.to_department_id) : false
  );

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Lista de Conversas */}
      <div className="w-1/3 bg-white border-r border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold">Conversas</h2>
        </div>
        <div className="overflow-y-auto h-full">
          {conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
                selectedConversation?.id === conversation.id ? 'bg-blue-50 border-blue-200' : ''
              }`}
              onClick={() => fetchConversationDetails(conversation.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                    <User className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-medium">{conversation.contact_name}</h3>
                    <p className="text-sm text-gray-500">{conversation.contact_phone}</p>
                  </div>
                </div>
                <div className="text-right">
                  <Badge variant={conversation.status === 'open' ? 'default' : 'secondary'}>
                    {conversation.status}
                  </Badge>
                  <p className="text-xs text-gray-500 mt-1">
                    {conversation.department_name}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Área de Chat */}
      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <>
            {/* Header da Conversa */}
            <div className="bg-white border-b border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                    <User className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-medium">{selectedConversation.contact_name}</h3>
                    <p className="text-sm text-gray-500">
                      {selectedConversation.contact_phone} • {selectedConversation.department_name}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowTransferModal(true)}
                  >
                    <ArrowRight className="h-4 w-4 mr-2" />
                    Transferir
                  </Button>
                  <Button variant="outline" size="sm">
                    <Phone className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>

            {/* Mensagens */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender_type === 'agent' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.sender_type === 'agent'
                        ? 'bg-blue-500 text-white'
                        : message.sender_type === 'system'
                        ? 'bg-gray-200 text-gray-700'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    {message.sender_name && message.sender_type !== 'customer' && (
                      <p className="text-xs opacity-75 mb-1">{message.sender_name}</p>
                    )}
                    
                    {message.file_path ? (
                      <div className="flex items-center space-x-2">
                        {renderFileIcon(message.message_type)}
                        <span className="text-sm">{message.content}</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0"
                          onClick={() => window.open(`/api/files/${message.file_path}`, '_blank')}
                        >
                          <Download className="h-3 w-3" />
                        </Button>
                      </div>
                    ) : (
                      <p className="text-sm">{message.content}</p>
                    )}
                    
                    <p className="text-xs opacity-75 mt-1">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              
              {/* Indicador de digitação */}
              {typingUsers.length > 0 && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg">
                    <p className="text-sm">
                      {typingUsers.join(', ')} está{typingUsers.length > 1 ? 'ão' : ''} digitando...
                    </p>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input de Mensagem */}
            <div className="bg-white border-t border-gray-200 p-4">
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploadingFile}
                >
                  <Paperclip className="h-4 w-4" />
                </Button>
                <Input
                  value={newMessage}
                  onChange={(e) => {
                    setNewMessage(e.target.value);
                    handleTyping();
                  }}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Digite sua mensagem..."
                  className="flex-1"
                />
                <Button onClick={sendMessage} disabled={!newMessage.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                onChange={handleFileUpload}
                accept="image/*,audio/*,.pdf,.doc,.docx,.txt,.xls,.xlsx"
              />
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900">Selecione uma conversa</h3>
              <p className="text-gray-500">Escolha uma conversa para começar a atender</p>
            </div>
          </div>
        )}
      </div>

      {/* Modal de Transferência */}
      {showTransferModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-96">
            <CardHeader>
              <CardTitle>Transferir Conversa</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Departamento de Destino</label>
                <select
                  value={transferData.to_department_id}
                  onChange={(e) => setTransferData(prev => ({
                    ...prev,
                    to_department_id: e.target.value,
                    to_agent_id: ''
                  }))}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="">Selecione um departamento</option>
                  {departments.map(dept => (
                    <option key={dept.id} value={dept.id}>{dept.name}</option>
                  ))}
                </select>
              </div>

              {transferData.to_department_id && (
                <div>
                  <label className="block text-sm font-medium mb-2">Agente (Opcional)</label>
                  <select
                    value={transferData.to_agent_id}
                    onChange={(e) => setTransferData(prev => ({
                      ...prev,
                      to_agent_id: e.target.value
                    }))}
                    className="w-full p-2 border border-gray-300 rounded-md"
                  >
                    <option value="">Qualquer agente disponível</option>
                    {filteredUsers.map(user => (
                      <option key={user.id} value={user.id}>{user.name}</option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium mb-2">Motivo da Transferência</label>
                <textarea
                  value={transferData.reason}
                  onChange={(e) => setTransferData(prev => ({
                    ...prev,
                    reason: e.target.value
                  }))}
                  className="w-full p-2 border border-gray-300 rounded-md"
                  rows="3"
                  placeholder="Descreva o motivo da transferência..."
                />
              </div>

              <div className="flex justify-end space-x-2">
                <Button
                  variant="outline"
                  onClick={() => setShowTransferModal(false)}
                >
                  Cancelar
                </Button>
                <Button
                  onClick={handleTransfer}
                  disabled={!transferData.to_department_id}
                >
                  Transferir
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default ChatInterface;

