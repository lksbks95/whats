import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const SettingsContext = createContext();

export const useSettings = () => useContext(SettingsContext);

export const SettingsProvider = ({ children }) => {
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await axios.get('/api/settings');
        setSettings(response.data);
      } catch (error) {
        console.error("Não foi possível carregar as configurações do sistema.", error);
      } finally {
        setLoading(false);
      }
    };
    fetchSettings();
  }, []);

  const value = { settings, loading };

  // Mostra um loading enquanto as configurações não forem carregadas
  if (loading) {
    return <div>Carregando configurações...</div>;
  }

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
};
