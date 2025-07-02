// backend/gateway/index.js

const { Client, LocalAuth } = require('whatsapp-web.js');
const express = require('express');
const cors = require('cors');
const axios = require('axios');
const http = require('http');
const { Server } = require("socket.io");

// --- CONFIGURAÇÃO DO SERVIDOR ---
const app = express();
const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*", // Permite conexões de qualquer origem
        methods: ["GET", "POST"]
    }
});

app.use(express.json());
app.use(cors());

const FLASK_BACKEND_URL = 'http://localhost:10000';

console.log("Iniciando cliente do WhatsApp...");

const client = new Client({
    authStrategy: new LocalAuth({ dataPath: '/app/session_data' }),
    puppeteer: {
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    }
});

// --- LÓGICA DO SOCKET.IO ---
io.on('connection', (socket) => {
    console.log('Frontend conectado ao Gateway via Socket.IO');

    // Quando o frontend se conecta, enviamos o status atual
    client.getState().then((state) => {
        socket.emit('connection_status', state || 'disconnected');
    });

    socket.on('disconnect', () => {
        console.log('Frontend desconectado do Gateway');
    });
});

// --- EVENTOS DO WHATSAPP-WEB.JS ---
client.on('qr', qr => {
    console.log('QR Code gerado. Enviando para o frontend...');
    // Envia o QR code para todos os clientes do frontend conectados
    io.emit('qr_code', qr);
    io.emit('connection_status', 'qr_code_generated');
});

client.on('ready', () => {
    console.log('>>> SUCESSO! Cliente do WhatsApp está pronto! <<<');
    io.emit('connection_status', 'ready');
});

client.on('disconnected', (reason) => {
    console.log('Cliente foi desconectado!', reason);
    io.emit('connection_status', 'disconnected');
    client.initialize(); // Tenta reconectar
});

client.on('message_create', async (message) => {
    if (message.fromMe) return;
    try {
        await axios.post(`${FLASK_BACKEND_URL}/api/whatsapp/webhook_internal`, {
            from: message.from,
            body: message.body,
            author: message.author,
        });
    } catch (error) {
        console.error('Erro ao encaminhar mensagem para o Flask:', error.message);
    }
});

// API para o Flask poder enviar mensagens (continua igual)
app.post('/send-message', async (req, res) => {
    const { to, text } = req.body;
    try {
        await client.sendMessage(to, text);
        res.status(200).json({ success: 'Mensagem enviada!' });
    } catch (error) {
        res.status(500).json({ error: 'Falha ao enviar mensagem' });
    }
});

// Inicia o servidor HTTP (que contém o Express e o Socket.IO)
const PORT = 3001;
server.listen(PORT, () => console.log(`Gateway de WhatsApp rodando na porta ${PORT}`));

client.initialize();
