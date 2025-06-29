#!/bin/sh

# Define o PYTHONPATH para incluir a pasta do backend.
# Isto garante que as importações como 'from src.models' funcionam.
export PYTHONPATH=/app/backend

# Inicia o servidor Gunicorn.
# O comando 'exec' garante que o Gunicorn herda as variáveis de ambiente do Koyeb,
# incluindo a DATABASE_URL.
exec gunicorn src.main:app \
    --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
    -w 1 \
    --bind 0.0.0.0:8000
