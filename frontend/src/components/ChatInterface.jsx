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
  Volume2,
  X,
  Smile // --- 1. ÍCONE DE EMOJI IMPORTADO ---
} from 'lucide-react';
import io from 'socket.io-client';
import Picker from 'emoji-picker-react'; // --- 2. SELETOR DE EMOJIS IMPORTADO ---

const ChatInterface = () => {
  const { user, token } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [typingUsers, setTypingUsers] = useState([]);
  const [socket, setSocket] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [users, setUsers] = useState([]);
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [transferData, setTransferData] = useState({ to_department_id: '', to_agent_id: '', reason: '' });
  
  // --- 3. NOVO ESTADO PARA CONTROLAR O SELETOR DE EMOJIS ---
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  // --- 4. NOVA FUNÇÃO PARA ADICIONAR O EMOJI À MENSAGEM ---
  const onEmojiClick = (emojiObject) => {
    setNewMessage(prevMessage => prevMessage + emojiObject.emoji);
    setShowEmojiPicker(false); // Fecha o seletor após escolher um emoji
  };

  // ... (todo o resto do seu código de useEffect, fetch, etc. permanece igual)
  // Conectar ao Socket.IO
  useEffect(() => {
    if (token) {
      const newSocket = io(window.location.origin, {
        auth: { token }
      });

      newSocket.on('connect', () => console.log('Conectado ao servidor Socket.IO'));

      newSocket.on('new_message', (data) => {
        if (selectedConversation && data.conversation_id === selectedConversation.id) {
          setMessages(prev => [...prev, data.message]);
        }
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

      return () => newSocket.disconnect();
    }
  }, [token, selectedConversation]);

  const fetchConversations = async () => { /* ...código... */ };
  const fetchConversationDetails = async (conversationId) => { /* ...código... */ };
  const fetchDepartmentsAndUsers = async () => { /* ...código... */ };
  useEffect(() => { if (token) { fetchConversations(); fetchDepartmentsAndUsers(); } }, [token]);
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);
  const sendMessage = async () => { /* ...código... */ };
  const handleFileSelect = (event) => { /* ...código... */ };
  const removeFile = (fileToRemove) => { /* ...código... */ };
  const handleTransfer = async () => { /* ...código... */ };
  const renderFileIcon = (messageType) => { /* ...código... */ };
  const filteredUsers = users.filter(u => transferData.to_department_id ? u.department_id === parseInt(transferData.to_department_id) : false);


  return (
    <div className="flex h-screen bg-gray-50">
      {/* ... (código da lista de conversas) ... */}

      {/* Área de Chat */}
      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <>
            {/* ... (código do header e das mensagens) ... */}

            {/* Input de Mensagem */}
            <div className="bg-white border-t border-gray-200 p-4 relative"> {/* Adicionado 'relative' */}
              
              {/* --- 5. SELETOR DE EMOJIS RENDERIZADO DE FORMA CONDICIONAL --- */}
              {showEmojiPicker && (
                <div className="absolute bottom-20 right-4 z-10"> {/* Posiciona o seletor */}
                  <Picker onEmojiClick={onEmojiClick} />
                </div>
              )}

              {/* Pré-visualização de arquivos selecionados */}
              {selectedFiles.length > 0 && (
                <div className="mb-2 p-2 border rounded-md bg-gray-50">
                  <p className="text-sm font-medium mb-1">Arquivos selecionados:</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedFiles.map((file, index) => (
                      <div key={index} className="flex items-center bg-gray-200 rounded-full px-2 py-1 text-xs">
                        <span>{file.name}</span>
                        <button onClick={() => removeFile(file)} className="ml-2 text-gray-500 hover:text-gray-800">
                          <X className="h-3 w-3" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex items-center space-x-2">
                {/* --- 6. BOTÃO PARA MOSTRAR/ESCONDER O SELETOR DE EMOJIS --- */}
                <Button variant="outline" size="icon" onClick={() => setShowEmojiPicker(!showEmojiPicker)}>
                  <Smile className="h-4 w-4" />
                </Button>

                <Button variant="outline" size="icon" onClick={() => fileInputRef.current?.click()} disabled={isUploading}>
                  <Paperclip className="h-4 w-4" />
                </Button>
                
                <Input
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Digite sua mensagem..."
                  className="flex-1"
                  disabled={isUploading}
                />
                <Button onClick={sendMessage} disabled={(!newMessage.trim() && selectedFiles.length === 0) || isUploading}>
                  {isUploading ? <Loader2 className="h-4 w-4 animate-spin"/> : <Send className="h-4 w-4" />}
                </Button>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                multiple 
                onChange={handleFileSelect}
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

      {/* ... (código do modal de transferência) ... */}
    </div>
  );
};

export default ChatInterface;
