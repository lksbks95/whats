const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
app.use(express.json());
app.use(cors());

// URL do seu backend Flask (você precisará configurar isso como uma variável de ambiente)
const FLASK_BACKEND_URL = process.env.FLASK_BACKEND_URL || 'http://localhost:8000';

console.log("Iniciando cliente do WhatsApp...");

const client = new Client({
    authStrategy: new LocalAuth(), // Salva a sessão para não precisar escanear sempre
    puppeteer: {
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox'] // Necessário para rodar em servidores como o Render
    }
});

client.on('qr', qr => {
    console.log('POR FAVOR, ESCANEIE ESTE QR CODE COM SEU WHATSAPP:');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('Cliente do WhatsApp está pronto e conectado!');
});

// Quando uma mensagem chega do WhatsApp...
client.on('message', async (message) => {
    try {
        console.log(`Mensagem recebida de ${message.from}: ${message.body}`);
        // ... encaminha para o backend Flask
        await axios.post(`${FLASK_BACKEND_URL}/api/whatsapp/webhook_internal`, {
            from: message.from, // ex: 555199... @c.us
            body: message.body,
            author: message.author, // útil para saber quem mandou em um grupo
            // Adicione outros campos que precisar
        });
    } catch (error) {
        console.error('Erro ao encaminhar mensagem para o backend Flask:', error.message);
    }
});

// API para o Flask poder enviar mensagens
app.post('/send-message', async (req, res) => {
    const { to, text } = req.body;
    if (!to || !text) {
        return res.status(400).json({ error: 'Faltam os campos "to" ou "text"' });
    }

    try {
        // O número precisa estar no formato '5551... @c.us'
        await client.sendMessage(to, text);
        res.status(200).json({ success: 'Mensagem enviada com sucesso!' });
    } catch (error) {
        console.error('Erro ao enviar mensagem via Gateway:', error.message);
        res.status(500).json({ error: 'Falha ao enviar mensagem' });
    }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
    console.log(`Gateway de WhatsApp rodando na porta ${PORT}`);
});

client.initialize();