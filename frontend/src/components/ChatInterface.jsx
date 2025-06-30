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
  X // Ícone para remover arquivos
} from 'lucide-react';
import io from 'socket.io-client';

const ChatInterface = () => {
  const { user, token } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  
  // --- ALTERAÇÃO 1: ESTADO PARA MÚLTIPLOS ARQUIVOS ---
  const [selectedFiles, setSelectedFiles] = useState([]); // Armazena uma lista de arquivos
  const [isUploading, setIsUploading] = useState(false); // Estado de upload unificado

  // (O resto dos seus estados e hooks permanecem os mesmos)
  const [isTyping, setIsTyping] = useState(false);
  const [typingUsers, setTypingUsers] = useState([]);
  const [socket, setSocket] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [users, setUsers] = useState([]);
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [transferData, setTransferData] = useState({ to_department_id: '', to_agent_id: '', reason: '' });
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  // (Todas as suas funções useEffect e fetch... permanecem as mesmas)
  // ...

  // --- ALTERAÇÃO 2: FUNÇÃO DE ENVIO UNIFICADA ---
  const sendMessage = async () => {
    if ((!newMessage.trim() && selectedFiles.length === 0) || !selectedConversation) return;
    
    setIsUploading(true);
    let uploadedFilesInfo = [];

    // Passo 1: Fazer upload dos arquivos, se houver
    if (selectedFiles.length > 0) {
      const formData = new FormData();
      selectedFiles.forEach(file => {
        formData.append('files[]', file); // Usa 'files[]' para indicar um array
      });

      try {
        const uploadResponse = await fetch('/api/upload_multiple', { // Chama a nova rota de múltiplos uploads
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData,
        });

        const uploadData = await uploadResponse.json();
        if (!uploadResponse.ok) throw new Error(uploadData.message || 'Erro no upload');
        uploadedFilesInfo = uploadData.uploaded_files;

      } catch (error) {
        console.error('Erro ao fazer upload dos arquivos:', error);
        alert('Falha no upload de um ou mais arquivos.');
        setIsUploading(false);
        return;
      }
    }

    // Passo 2: Enviar as mensagens (texto e/ou arquivos)
    try {
      // Envia mensagem de texto se houver
      if (newMessage.trim()) {
        await fetch(`/api/conversations/${selectedConversation.id}/messages`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ content: newMessage, message_type: 'text' })
        });
      }
      // Envia uma mensagem para cada arquivo que foi salvo
      for (const fileInfo of uploadedFilesInfo) {
        await fetch(`/api/conversations/${selectedConversation.id}/messages`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({
            content: `Arquivo: ${fileInfo.original_name}`,
            message_type: fileInfo.file_type,
            file_path: fileInfo.file_path
          })
        });
      }

      // Limpar tudo e atualizar
      setNewMessage('');
      setSelectedFiles([]);
      if (socket) {
        socket.emit('stop_typing', { conversation_id: selectedConversation.id, user_name: user.name });
      }
      fetchConversationDetails(selectedConversation.id);

    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
    } finally {
      setIsUploading(false);
    }
  };

  // --- ALTERAÇÃO 3: FUNÇÃO PARA SELECIONAR ARQUIVOS ---
  const handleFileSelect = (event) => {
    if (event.target.files) {
      setSelectedFiles(prev => [...prev, ...Array.from(event.target.files)]);
    }
    // Limpa o valor do input para permitir selecionar o mesmo arquivo novamente
    event.target.value = ''; 
  };
  
  // Função para remover um arquivo da lista de seleção
  const removeFile = (fileToRemove) => {
    setSelectedFiles(prev => prev.filter(file => file !== fileToRemove));
  };


  // (O resto das suas funções como handleTyping, handleTransfer, etc. permanecem as mesmas)
  // ...

  return (
    <div className="flex h-screen bg-gray-50">
      {/* ... (código da lista de conversas e header do chat) ... */}
      
      {/* Área de Chat */}
      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <>
            {/* ... (código do header da conversa e das mensagens) ... */}

            {/* Input de Mensagem */}
            <div className="bg-white border-t border-gray-200 p-4">
              {/* --- ALTERAÇÃO 4: ÁREA DE PRÉ-VISUALIZAÇÃO DE ARQUIVOS --- */}
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
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                >
                  <Paperclip className="h-4 w-4" />
                </Button>
                <Input
                  value={newMessage}
                  onChange={(e) => {
                    setNewMessage(e.target.value);
                    // handleTyping(); // Você pode querer chamar o handleTyping aqui também
                  }}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Digite sua mensagem..."
                  className="flex-1"
                  disabled={isUploading}
                />
                <Button onClick={sendMessage} disabled={(!newMessage.trim() && selectedFiles.length === 0) || isUploading}>
                  {isUploading ? <Loader2 className="h-4 w-4 animate-spin"/> : <Send className="h-4 w-4" />}
                </Button>
              </div>
              {/* --- ALTERAÇÃO 5: INPUT DE ARQUIVO AGORA SUPORTA MÚLTIPLOS --- */}
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
          // ... (código para quando nenhuma conversa está selecionada)
        )}
      </div>

      {/* ... (código do modal de transferência) ... */}
    </div>
  );
};

export default ChatInterface;
