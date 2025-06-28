import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Plus, Edit, Trash2, Loader2 } from 'lucide-react';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    name: '',
    email: '',
    role: 'agent',
    department_id: '',
    is_active: true
  });

  const fetchUsers = async () => {
    try {
      const response = await axios.get('/api/users');
      setUsers(response.data.users);
    } catch (error) {
      setError('Erro ao carregar usuários');
    } finally {
      setLoading(false);
    }
  };

  const fetchDepartments = async () => {
    try {
      console.log("DIAGNÓSTICO: A procurar departamentos em /api/departments...");
      const response = await axios.get('/api/departments');
      console.log("DIAGNÓSTICO: Resposta da API de departamentos:", response.data);

      if (response.data && Array.isArray(response.data.departments)) {
        const validDepartments = response.data.departments.filter(dept => dept.id !== null && dept.id !== undefined && dept.id !== '');
        console.log("DIAGNÓSTICO: Departamentos válidos a serem usados:", validDepartments);
        setDepartments(validDepartments);
      } else {
        console.error("DIAGNÓSTICO: A resposta da API de departamentos não tem o formato esperado.");
        setDepartments([]);
      }
    } catch (error) {
      console.error('DIAGNÓSTICO: Erro ao carregar departamentos:', error);
    }
  };
  
  useEffect(() => {
    fetchUsers();
    fetchDepartments();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      if (editingUser) {
        await axios.put(`/api/users/${editingUser.id}`, formData);
      } else {
        await axios.post('/api/users', formData);
      }
      
      fetchUsers();
      setIsDialogOpen(false);
      resetForm();
    } catch (error) {
      setError(error.response?.data?.message || 'Erro ao salvar usuário');
    }
  };

  const handleDelete = async (userId) => {
    if (window.confirm('Tem certeza que deseja deletar este usuário?')) {
      try {
        await axios.delete(`/api/users/${userId}`);
        fetchUsers();
      } catch (error) {
        setError(error.response?.data?.message || 'Erro ao deletar usuário');
      }
    }
  };

  const openEditDialog = (user) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      password: '',
      name: user.name,
      email: user.email,
      role: user.role,
      department_id: user.department_id ? user.department_id.toString() : '',
      is_active: user.is_active
    });
    setIsDialogOpen(true);
  };

  const resetForm = () => {
    setEditingUser(null);
    setFormData({
      username: '',
      password: '',
      name: '',
      email: '',
      role: 'agent',
      department_id: '',
      is_active: true
    });
  };

  const getRoleBadge = (role) => {
    const variants = { admin: 'destructive', manager: 'default', agent: 'secondary' };
    const labels = { admin: 'Administrador', manager: 'Gerenciador', agent: 'Agente' };
    return <Badge variant={variants[role]}>{labels[role]}</Badge>;
  };

  if (loading) {
    return <Card><CardContent className="flex items-center justify-center py-8"><Loader2 className="h-8 w-8 animate-spin" /></CardContent></Card>;
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Gerenciamento de Usuários</CardTitle>
              <CardDescription>Gerencie usuários do sistema e suas permissões</CardDescription>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button onClick={resetForm}><Plus className="h-4 w-4 mr-2" />Novo Usuário</Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                  <DialogTitle>{editingUser ? 'Editar Usuário' : 'Novo Usuário'}</DialogTitle>
                  <DialogDescription>{editingUser ? 'Edite as informações do usuário' : 'Preencha os dados do novo usuário'}</DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4 py-4">
                  {/* ... outros campos do formulário ... */}
                  <div className="space-y-2">
                    <Label htmlFor="department">Departamento</Label>
                    <Select value={formData.department_id} onValueChange={(value) => setFormData({...formData, department_id: value})}>
                      <SelectTrigger><SelectValue placeholder="Selecione..." /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">Nenhum</SelectItem>
                        {departments.map((dept) => (
                          <SelectItem key={dept.id} value={String(dept.id)}>{dept.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  {/* ... outros campos e botões ... */}
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          {/* ... Tabela de usuários ... */}
        </CardContent>
      </Card>
    </div>
  );
};

export default UserManagement;
