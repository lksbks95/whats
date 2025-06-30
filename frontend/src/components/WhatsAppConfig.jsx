import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useSettings } from '../contexts/SettingsContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

const WhatsAppConfig = () => {
  const { settings, loading: settingsLoading } = useSettings();

  // Estados para os campos específicos do WhatsApp
  const [phoneNumberId, setPhoneNumberId] = useState('');
  const [wabaId, setWabaId] = useState('');
  const [accessToken, setAccessToken] = useState('');
  const [verifyToken, setVerifyToken] = useState('');

  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');

  // Preenche o formulário com os dados atuais quando o componente carrega
  useEffect(() => {
    if (settings) {
      setPhoneNumberId(settings.whatsapp_phone_number_id || '');
      setWabaId(settings.whatsapp_waba_id || '');
      setAccessToken(settings.whatsapp_access_token || '');
      setVerifyToken(settings.whatsapp_verify_token || '');
    }
  }, [settings]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setMessage('');

    try {
      const whatsappSettings = {
        whatsapp_phone_number_id: phoneNumberId,
        whatsapp_waba_id: wabaId,
        whatsapp_access_token: accessToken,
        whatsapp_verify_token: verifyToken, // Usado para a verificação do webhook
      };
      
      // A chamada é para a mesma API, mas enviando apenas as chaves do WhatsApp
      await axios.post('/api/settings', whatsappSettings);
      
      setMessage('Configurações do WhatsApp salvas com sucesso!');

    } catch (error) {
      setMessage('Erro ao salvar as configurações.');
      console.error("Erro ao salvar:", error);
    } finally {
      setIsSaving(false);
    }
  };
  
  if (settingsLoading) {
    return <div>Carregando...</div>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Configuração da API do WhatsApp</CardTitle>
        <CardDescription>
          Insira aqui as credenciais obtidas no painel da Meta for Developers.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="phoneNumberId">ID do Número de Telefone</Label>
            <Input id="phoneNumberId" value={phoneNumberId} onChange={(e) => setPhoneNumberId(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="wabaId">ID da Conta do WhatsApp Business (WABA)</Label>
            <Input id="wabaId" value={wabaId} onChange={(e) => setWabaId(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="accessToken">Token de Acesso Permanente</Label>
            <Input id="accessToken" type="password" value={accessToken} onChange={(e) => setAccessToken(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="verifyToken">Token de Verificação do Webhook</Label>
            <Input id="verifyToken" value={verifyToken} onChange={(e) => setVerifyToken(e.target.value)} placeholder="Crie uma senha secreta aqui" />
          </div>
          <div className="flex items-center justify-between mt-4">
            <Button type="submit" disabled={isSaving}>
              {isSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Salvar Credenciais
            </Button>
            {message && <p className="text-sm text-green-600">{message}</p>}
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default WhatsAppConfig;
