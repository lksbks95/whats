import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { QRCode } from 'qrcode.react'; // Importa o componente para renderizar o QR Code
import { CheckCircle, XCircle, Loader2, QrCode } from 'lucide-react';

// A URL do seu gateway. Em produção, a Render irá expor as duas portas no mesmo domínio.
// Em desenvolvimento local, você precisaria usar 'http://localhost:3001'.
const GATEWAY_URL = window.location.origin;

const WhatsAppConfig = () => {
    const [status, setStatus] = useState('connecting');
    const [qrCode, setQrCode] = useState('');

    useEffect(() => {
        // Conecta ao servidor Socket.IO do gateway
        const socket = io(GATEWAY_URL, {
            // Garante que o socket tente se conectar ao caminho correto na Render
            path: '/socket.io'
        });

        socket.on('connect', () => {
            console.log('Conectado ao Gateway de WhatsApp');
        });
        
        socket.on('connect_error', (err) => {
            console.error('Erro de conexão com o Socket.IO:', err.message);
            setStatus('disconnected');
        });

        // Ouve o evento que envia o status da conexão
        socket.on('connection_status', (newStatus) => {
            console.log('Novo status recebido:', newStatus);
            setStatus(newStatus || 'disconnected');
            if (newStatus !== 'qr_code_generated') {
                setQrCode(''); // Limpa o QR code se o status mudar
            }
        });

        // Ouve o evento que envia o QR Code
        socket.on('qr_code', (qr) => {
            console.log('QR Code recebido');
            setQrCode(qr);
        });

        // Limpa a conexão quando o componente é desmontado
        return () => {
            socket.disconnect();
        };
    }, []);

    const renderStatus = () => {
        switch (status) {
            case 'ready':
                return (
                    <div className="flex flex-col items-center text-center text-green-600">
                        <CheckCircle className="h-16 w-16 mb-4" />
                        <h3 className="text-xl font-semibold">Conectado</h3>
                        <p className="text-sm text-gray-500">A sua sessão do WhatsApp está ativa.</p>
                    </div>
                );
            case 'qr_code_generated':
                return (
                    <div className="flex flex-col items-center text-center">
                        <QrCode className="h-12 w-12 mb-4 text-blue-600" />
                        <h3 className="text-xl font-semibold">Escaneie para Conectar</h3>
                        <p className="text-sm text-gray-500 mb-4">Abra o WhatsApp no seu celular e escaneie o código abaixo.</p>
                        {qrCode && <QRCode value={qrCode} size={256} bgColor="#ffffff" fgColor="#000000" />}
                    </div>
                );
            case 'disconnected':
                return (
                     <div className="flex flex-col items-center text-center text-red-600">
                        <XCircle className="h-16 w-16 mb-4" />
                        <h3 className="text-xl font-semibold">Desconectado</h3>
                        <p className="text-sm text-gray-500">O serviço está a tentar reconectar. Verifique os logs do servidor se o problema persistir.</p>
                    </div>
                );
            default:
                return (
                    <div className="flex flex-col items-center text-center text-gray-600">
                        <Loader2 className="h-16 w-16 mb-4 animate-spin" />
                        <h3 className="text-xl font-semibold">A conectar ao Gateway...</h3>
                        <p className="text-sm text-gray-500">A aguardar o status do serviço de WhatsApp.</p>
                    </div>
                );
        }
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Conexão com o WhatsApp</CardTitle>
                <CardDescription>
                    Monitore o status da sua conexão com o WhatsApp e escaneie o QR Code quando necessário.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div className="flex justify-center items-center p-8 border-2 border-dashed rounded-lg min-h-[350px]">
                    {renderStatus()}
                </div>
            </CardContent>
        </Card>
    );
};

export default WhatsAppConfig;
