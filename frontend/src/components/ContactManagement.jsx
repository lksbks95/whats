import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext'; // Importação do Contexto
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'; // <-- A IMPORTAÇÃO QUE FALTAVA
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Plus, MessageSquare, Loader2, BookUser } from 'lucide-react';
import { IMaskInput } from 'react-imask';

const ContactManagement = ({ setActiveTab }) => {
  const { fetchConversations } = useAuth(); // Pega a função de atualização do contexto
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', phone_number: '', email: '' });
  const [error, setError] = useState('');

  const fetchContacts = async () => {
    try {
      const response = await axios.get('/api/contacts');
      setContacts(response.data.contacts);
    } catch (err) {
      setError('Erro ao carregar contatos.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContacts();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await axios.post('/api/contacts', formData);
      fetchContacts();
      setIsDialogOpen(false);
      setFormData({ name: '', phone_number: '', email: '' });
    } catch (err) {
      setError(err.response?.data?.message || 'Erro ao criar contato.');
    }
  };

  const handleStartConversation = async (contactId) => {
    try {
      const response = await axios.post(`/api/contacts/${contactId}/start_conversation`);
      alert(response.data.message);
      await fetchConversations(); // Avisa o contexto para atualizar a lista de conversas
      if (setActiveTab) {
        setActiveTab('conversations');
      }
    } catch (err) {
      alert(err.response?.data?.message || 'Erro ao iniciar conversa.');
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64"><Loader2 className="h-8 w-8 animate-spin" /></div>;
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle className="flex items-center"><BookUser className="mr-2 h-5 w-5" />Agenda de Contatos</CardTitle>
            <CardDescription>Gerencie seus contatos e inicie novas conversas.</CardDescription>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button><Plus className="mr-2 h-4 w-4" />Novo Contato</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Criar Novo Contato</DialogTitle></DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Nome</Label>
                  <Input id="name" value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} required />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="phone">Número de Telefone</Label>
                  <IMaskInput
                    mask="+{55} (00) 00000-0000"
                    radix="."
                    value={formData.phone_number}
                    unmask={true}
                    onAccept={(value) => setFormData({...formData, phone_number: value})}
                    placeholder="+55 (51) 99999-8888"
                    id="phone"
                    required
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="email">Email (Opcional)</Label>
                  <Input id="email" type="email" value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} />
                </div>
                {error && <p className="text-sm text-red-500">{error}</p>}
                <div className="flex justify-end">
                  <Button type="submit">Salvar Contato</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nome</TableHead>
              <TableHead>Telefone</TableHead>
              <TableHead>Email</TableHead>
              <TableHead className="text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {contacts.map((contact) => (
              <TableRow key={contact.id}>
                <TableCell className="font-medium">{contact.name}</TableCell>
                <TableCell>{contact.phone_number}</TableCell>
                <TableCell>{contact.email || '-'}</TableCell>
                <TableCell className="text-right">
                  <Button size="sm" onClick={() => handleStartConversation(contact.id)}>
                    <MessageSquare className="mr-2 h-4 w-4" />
                    Iniciar Conversa
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
};

export default ContactManagement;
