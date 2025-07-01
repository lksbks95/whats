import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Send, Paperclip, Phone, User, ArrowRight, Download, Image, FileText, Volume2, X, Smile 
} from 'lucide-react';
import io from 'socket.io-client';
import Picker from 'emoji-picker-react';
import axios from 'axios'; // Importe o axios se ainda não o fez

const ChatInterface = () => {
  // Pega dados globais do AuthContext
  const { user, token, conversations, loadingConversations } = useAuth();
  
  // Estados locais específicos deste componente
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [socket, setSocket] = useState(null);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  
  // (outros estados e refs que você já tinha)
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // --- FUNÇÃO RESTAURADA ---
  // Esta função é local e busca os detalhes de UMA conversa específica
  const fetchConversationDetails = async (conversationId) => {
    try {
      const response = await axios.get(`/api/conversations/${conversationId}`);
      setSelectedConversation(response.data.conversation);
      setMessages(response.data.messages || []);
      
      if (socket) {
        socket.emit('join_conversation', { conversation_id: conversationId });
      }
    } catch (error) {
      console.error('Erro ao buscar detalhes da conversa:', error);
    }
  };

  // Conectar ao Socket.IO
  useEffect(() => {
    if (token) {
      const newSocket = io(window.location.origin, { auth: { token } });
      setSocket(newSocket);
      // ... (seu código de listeners do socket.io)
      return () => newSocket.disconnect();
    }
  }, [token]);

  // Scroll automático
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // (outras funções como sendMessage, onEmojiClick, etc., permanecem aqui)
  const onEmojiClick = (emojiObject) => { /* ... */ };
  const sendMessage = async () => { /* ... */ };
  const handleFileSelect = (event) => { /* ... */ };
  const removeFile = (fileToRemove) => { /* ... */ };
  const renderFileIcon = (messageType) => { /* ... */ };


  return (
    <div className="flex h-[calc(100vh-4rem)] bg-gray-50"> {/* Ajuste de altura */}
      {/* Lista de Conversas */}
      <div className="w-1/3 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200 flex-shrink-0">
          <h2 className="text-lg font-semibold">Conversas</h2>
        </div>
        <div className="overflow-y-auto flex-grow">
          {loadingConversations ? (
            <div className="p-4 text-center text-sm text-gray-500">Carregando...</div>
          ) : conversations.length > 0 ? (
            conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
                  selectedConversation?.id === conversation.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                }`}
                // O onClick agora funciona porque a função existe
                onClick={() => fetchConversationDetails(conversation.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                      <User className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <h3 className="font-medium truncate">{conversation.contact_name}</h3>
                      <p className="text-sm text-gray-500 truncate">{conversation.contact_phone}</p>
                    </div>
                  </div>
                  {/* ... (outros detalhes como status, departamento) ... */}
                </div>
              </div>
            ))
          ) : (
            <div className="p-4 text-center text-sm text-gray-500">Nenhuma conversa encontrada.</div>
          )}
        </div>
      </div>

      {/* Área de Chat */}
      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <>
            {/* ... (seu código do header, mensagens e input de mensagem) ... */}
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900">Selecione uma conversa</h3>
              <p className="text-gray-500">Escolha uma conversa da lista para começar a atender.</p>
            </div>
          </div>
        )}
      </div>

       {/* O seu modal de transferência pode continuar aqui */}
    </div>
  );
};

export default ChatInterface;
