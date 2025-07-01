// frontend/src/contexts/AuthContext.jsx

import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  // --- 1. ESTADO CENTRALIZADO PARA CONVERSAS ---
  const [conversations, setConversations] = useState([]);
  const [loadingConversations, setLoadingConversations] = useState(true);

  // --- 2. FUNÇÃO CENTRALIZADA PARA BUSCAR CONVERSAS ---
  const fetchConversations = async () => {
    if (!token) return; // Só busca se houver token
    setLoadingConversations(true);
    try {
      const response = await axios.get('/api/conversations', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setConversations(response.data.conversations || []);
    } catch (error) {
      console.error('AuthContext: Erro ao buscar conversas:', error);
      setConversations([]); // Limpa em caso de erro
    } finally {
      setLoadingConversations(false);
    }
  };

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          const response = await axios.get('/api/me'); // Supondo que você tenha uma rota /api/me ou /api/auth/profile
          setUser(response.data.user);
          // --- 3. BUSCA AS CONVERSAS LOGO APÓS CONFIRMAR O LOGIN ---
          await fetchConversations();
        } catch (error) {
          console.error('Token inválido:', error);
          logout();
        }
      }
      setLoading(false);
    };
    checkAuth();
  }, [token]);

  const login = async (username, password) => {
    try {
      const response = await axios.post('/api/login', { username, password });
      const { token: newToken, user: userData } = response.data;
      setToken(newToken);
      setUser(userData);
      localStorage.setItem('token', newToken);
      return { success: true };
    } catch (error) {
      return { success: false, message: error.response?.data?.message || 'Erro ao fazer login' };
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
    // --- 4. DISPONIBILIZA O ESTADO E A FUNÇÃO PARA TODA A APP ---
    conversations,
    fetchConversations,
    loadingConversations,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
