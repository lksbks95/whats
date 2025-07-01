import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Send, Paperclip, Phone, User, ArrowRight, Download, Image, FileText, Volume2, X, Smile, Loader2 
} from 'lucide-react';
import io from 'socket.io-client';
import Picker from 'emoji-picker-react';
import axios from 'axios';

const ChatInterface = () => {
  const { user, token, conversations, loadingConversations } = useAuth();
  
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [socket, setSocket] = useState(null);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

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

  useEffect(() => {
    if (token) {
      const newSocket = io(window.location.origin, { auth: { token } });
      setSocket(newSocket);

      newSocket.on('new_message', (data) => {
        // Atualiza as mensagens apenas se a conversa correta estiver selecionada
        if (data && data.message && selectedConversation && data.conversation_id === selectedConversation.id) {
            setMessages(prevMessages => [...prevMessages, data.message]);
        }
      });

      return () => newSocket.disconnect();
    }
  }, [token, selectedConversation]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const onEmojiClick = (emojiObject) => {
    setNewMessage(prevMessage => prevMessage + emojiObject.emoji);
    setShowEmojiPicker(false);
  };

  const handleFileSelect = (event) => {
    if (event.target.files) {
      setSelectedFiles(prev => [...prev, ...Array.from(event.target.files)]);
    }
    event.target.value = ''; 
  };

  const removeFile = (fileToRemove) => {
    setSelectedFiles(prev => prev.filter(file => file !== fileToRemove));
  };

  const renderFileIcon = (messageType) => {
    switch (messageType) {
      case 'image': return <Image className="h-5 w-5 mr-2" />;
      case 'document': return <FileText className="h-5 w-5 mr-2" />;
      case 'audio': return <Volume2 className="h-5 w-5 mr-2" />;
      default: return <Paperclip className="h-5 w-5 mr-2" />;
    }
  };

  const sendMessage = async () => {
    if ((!newMessage.trim() && selectedFiles.length === 0) || !selectedConversation) return;

    setIsUploading(true);
    let uploadedFilesInfo = [];

    if (selectedFiles.length > 0) {
      const formData = new FormData();
      selectedFiles.forEach(file => formData.append('files[]', file));

      try {
        const uploadResponse = await axios.post('/api/upload_multiple', formData);
        uploadedFilesInfo = uploadResponse.data.uploaded_files || [];
        if(uploadResponse.data.errors && uploadResponse.data.errors.length > 0){
            alert(`Falha no upload de alguns arquivos: ${uploadResponse.data.errors.map(e => e.filename).join(', ')}`);
        }
      } catch (error) {
        alert('Falha crítica no upload de arquivos.');
        setIsUploading(false);
        return;
      }
    }

    try {
      if (newMessage.trim()) {
        await axios.post(`/api/conversations/${selectedConversation.id}/messages`, {
          content: newMessage,
          message_type: 'text'
        });
      }
      for (const fileInfo of uploadedFilesInfo) {
        await axios.post(`/api/conversations/${selectedConversation.id}/messages`, {
          content: fileInfo.original_name,
          message_type: fileInfo.file_type,
          file_path: fileInfo.file_path
        });
      }

      setNewMessage('');
      setSelectedFiles([]);
      // Não precisa mais do fetch, o socket.io irá atualizar
      // fetchConversationDetails(selectedConversation.id); 
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-gray-50">
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
                className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${selectedConversation?.id === conversation.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''}`}
                onClick={() => fetchConversationDetails(conversation.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0"><User className="h-5 w-5 text-white" /></div>
                    <div>
                      <h3 className="font-medium truncate">{conversation.contact_name}</h3>
                      <p className="text-sm text-gray-500 truncate">{conversation.contact_phone}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="p-4 text-center text-sm text-gray-500">Nenhuma conversa encontrada.</div>
          )}
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <>
            <div className="bg-white border-b border-gray-200 p-4 flex-shrink-0">
              <h3 className="font-medium">{selectedConversation.contact_name}</h3>
              <p className="text-sm text-gray-500">{selectedConversation.contact_phone}</p>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.sender_type === 'agent' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${message.sender_type === 'agent' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-900'}`}>
                    {message.file_path ? (
                      <a href={`/api/files/${message.file_path}`} target="_blank" rel="noopener noreferrer" className="flex items-center underline">
                        {renderFileIcon(message.message_type)}
                        <span>{message.content}</span>
                      </a>
                    ) : (
                      <p className="text-sm">{message.content}</p>
                    )}
                    <p className="text-xs opacity-75 mt-1 text-right">{new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            <div className="bg-white border-t border-gray-200 p-4 relative flex-shrink-0">
              {showEmojiPicker && (
                <div className="absolute bottom-20 right-4 z-10"><Picker onEmojiClick={onEmojiClick} /></div>
              )}
              {selectedFiles.length > 0 && (
                <div className="mb-2 p-2 border rounded-md bg-gray-50">
                  <div className="flex flex-wrap gap-2">
                    {selectedFiles.map((file, index) => (
                      <div key={index} className="flex items-center bg-gray-200 rounded-full px-2 py-1 text-xs">
                        <span>{file.name}</span>
                        <button onClick={() => removeFile(file)} className="ml-2 text-gray-500 hover:text-gray-800"><X className="h-3 w-3" /></button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="icon" onClick={() => setShowEmojiPicker(!showEmojiPicker)}><Smile className="h-4 w-4" /></Button>
                <Button variant="outline" size="icon" onClick={() => fileInputRef.current?.click()} disabled={isUploading}><Paperclip className="h-4 w-4" /></Button>
                <Input value={newMessage} onChange={(e) => setNewMessage(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && sendMessage()} placeholder="Digite sua mensagem..." className="flex-1" disabled={isUploading} />
                <Button onClick={sendMessage} disabled={(!newMessage.trim() && selectedFiles.length === 0) || isUploading}>
                  {isUploading ? <Loader2 className="h-4 w-4 animate-spin"/> : <Send className="h-4 w-4" />}
                </Button>
              </div>
              <input ref={fileInputRef} type="file" className="hidden" multiple onChange={handleFileSelect} accept="image/*,audio/*,.pdf,.doc,.docx,.txt,.xls,.xlsx" />
            </div>
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
    </div>
  );
};

export default ChatInterface;
