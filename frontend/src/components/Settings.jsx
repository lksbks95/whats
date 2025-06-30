import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useSettings } from '../contexts/SettingsContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

const Settings = () => {
  // Busca as configurações atuais do contexto para exibir no formulário
  const { settings, loading: settingsLoading } = useSettings();

  // Cria estados para controlar os campos do formulário
  const [companyName, setCompanyName] = useState('');
  const [logoUrl, setLogoUrl] = useState('');

  // Cria estados para o processo de salvamento
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');

  // Este efeito é executado quando as configurações são carregadas do contexto,
  // preenchendo o formulário com os valores atuais.
  useEffect(() => {
    if (settings) {
      setCompanyName(settings.company_name || '');
      setLogoUrl(settings.logo_url || '');
    }
  }, [settings]);

  // Função chamada quando o formulário é enviado
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setMessage('');

    try {
      const updatedSettings = {
        company_name: companyName,
        logo_url: logoUrl,
      };
      
      // Faz a chamada para a rota da API que criamos no Flask
      await axios.post('/api/settings', updatedSettings);
      
      setMessage('Configurações salvas com sucesso!');
      
      // Opcional: Recarregar a página após 2 segundos para ver as mudanças em todo o site
      setTimeout(() => window.location.reload(), 2000);

    } catch (error) {
      setMessage('Erro ao salvar as configurações. Tente novamente.');
      console.error("Erro ao salvar configurações:", error);
    } finally {
      setIsSaving(false);
    }
  };
  
  // Mostra uma mensagem de "Carregando..." enquanto as configurações iniciais não chegam
  if (settingsLoading) {
      return <div>Carregando...</div>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Configurações Gerais</CardTitle>
        <CardDescription>
          Altere as informações de personalização da sua empresa. As mudanças serão aplicadas em todo o sistema após salvar.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="companyName">Nome da Empresa</Label>
            <Input
              id="companyName"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="O nome que aparecerá no cabeçalho"
              disabled={isSaving}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="logoUrl">URL do Logo</Label>
            <Input
              id="logoUrl"
              value={logoUrl}
              onChange={(e) => setLogoUrl(e.target.value)}
              placeholder="https://... (link para uma imagem .jpg ou .png)"
              disabled={isSaving}
            />
          </div>

          <div className="flex items-center justify-between mt-4">
            <Button type="submit" disabled={isSaving}>
              {isSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Salvar Alterações
            </Button>
            
            {message && <p className="text-sm text-green-600">{message}</p>}
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default Settings;
