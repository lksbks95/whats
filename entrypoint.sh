#!/bin/sh
# Este script é o ponto de entrada principal para o container.
# Ele irá iniciar o Nginx em segundo plano e depois o Gunicorn em primeiro plano.
# Por ser o processo principal, ele herda todas as variáveis de ambiente do Koyeb.

set -e

echo "--- A iniciar o entrypoint.sh ---"

# Inicia o servidor Nginx em segundo plano.
echo "A iniciar o Nginx..."
nginx -g "daemon off;" &

# Inicia o servidor Gunicorn em primeiro plano.
# Ele irá herdar as variáveis de ambiente (como DATABASE_URL) deste script.
# O 'exec' substitui o processo do script pelo Gunicorn, o que é uma boa prática.
echo "A iniciar o Gunicorn..."
exec gunicorn src.main:socketio \
    --chdir /app/backend \
    --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
    -w 1 \
    --bind 127.0.0.1:8000
