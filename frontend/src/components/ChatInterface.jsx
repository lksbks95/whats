// frontend/src/components/ChatInterface.jsx

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext'; // --- 1. IMPORTAÇÃO DO CONTEXTO ---
// ... outras importações ...

const ChatInterface = () => {
  // --- 2. USA OS DADOS DIRETAMENTE DO CONTEXTO ---
  const { user, token, conversations, fetchConversations, loadingConversations } = useAuth();
  
  // --- REMOVA O ESTADO LOCAL DE CONVERSAS DAQUI ---
  // const [conversations, setConversations] = useState([]);

  const [selectedConversation, setSelectedConversation] = useState(null);
  // ... resto dos seus estados ...

  // --- REMOVA A FUNÇÃO fetchConversations DESTE ARQUIVO ---
  // Ela agora é global e está no AuthContext

  // --- REMOVA O useEffect QUE BUSCAVA AS CONVERSAS ---
  // O AuthContext já faz isso quando a app carrega.

  // ... (resto do seu código e funções) ...

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Lista de Conversas */}
      <div className="w-1/3 bg-white border-r border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold">Conversas</h2>
        </div>
        <div className="overflow-y-auto h-full">
          {/* --- 3. RENDERIZA A LISTA VINDA DO CONTEXTO --- */}
          {loadingConversations ? (
            <div className="p-4 text-center text-sm text-gray-500">Carregando conversas...</div>
          ) : (
            conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
                  selectedConversation?.id === conversation.id ? 'bg-blue-50 border-blue-200' : ''
                }`}
                onClick={() => fetchConversationDetails(conversation.id)}
              >
                {/* ... seu código para renderizar cada item ... */}
              </div>
            ))
          )}
        </div>
      </div>

      {/* ... (resto do seu JSX) ... */}
    </div>
  );
};

export default ChatInterface;
