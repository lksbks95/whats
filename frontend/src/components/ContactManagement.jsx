// frontend/src/components/ContactManagement.jsx

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext'; // --- 1. IMPORTAÇÃO DO CONTEXTO ---
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
// ... outras importações ...
import { Plus, MessageSquare, Loader2, BookUser } from 'lucide-react';
import { IMaskInput } from 'react-imask';

const ContactManagement = ({ setActiveTab }) => {
  const { fetchConversations } = useAuth(); // --- 2. PEGA A FUNÇÃO DE ATUALIZAÇÃO DO CONTEXTO ---
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', phone_number: '', email: '' });
  const [error, setError] = useState('');

  const fetchContacts = async () => { /* ... seu código de fetchContacts ... */ };
  useEffect(() => { fetchContacts(); }, []);
  const handleSubmit = async (e) => { /* ... seu código de handleSubmit ... */ };

  const handleStartConversation = async (contactId) => {
    try {
      const response = await axios.post(`/api/contacts/${contactId}/start_conversation`);
      alert(response.data.message);

      // --- 3. APÓS O SUCESSO, MANDA O CONTEXTO ATUALIZAR A LISTA DE CONVERSAS ---
      await fetchConversations(); 

      if (setActiveTab) {
        setActiveTab('conversations');
      }
    } catch (err) {
      alert(err.response?.data?.message || 'Erro ao iniciar conversa.');
    }
  };

  // ... (resto do seu código do componente)
  return (
    <Card>
      {/* ... seu JSX permanece o mesmo ... */}
    </Card>
  );
};

export default ContactManagement;
