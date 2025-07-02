#!/bin/sh

# Inicia o Gateway Node.js em segundo plano
echo "Iniciando o Gateway de WhatsApp em segundo plano..."
node backend/gateway/index.js &

# Aguarda um pouco para o gateway iniciar antes do Flask
sleep 5

# Inicia o servidor Gunicorn do Flask em primeiro plano
echo "Iniciando o servidor principal Gunicorn..."
# --- ALTERAÇÃO AQUI: Usa a variável $PORT fornecida pela Render ---
exec gunicorn src.main:app --chdir /app/backend --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 --bind 0.0.0.0:$PORT
