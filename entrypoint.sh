#!/bin/sh

# Sai imediatamente se um comando falhar
set -e

echo "--- INICIANDO O ENTRYPOINT DE DIAGNÓSTICO ---"
echo ""
echo "===================================================="
echo ">>> DIAGNÓSTICO 1: Listando todos os arquivos no frontend compilado..."
echo "Verificando o conteúdo de /app/frontend/dist/"
# O comando 'ls -R' lista todos os arquivos e pastas de forma recursiva.
ls -R /app/frontend/dist
echo "===================================================="
echo ""
echo "===================================================="
echo ">>> DIAGNÓSTICO 2: Exibindo o conteúdo do index.html..."
echo "Isto nos mostrará os caminhos exatos (href e src) que o navegador tentará carregar."
# O comando 'cat' exibe o conteúdo de um arquivo.
cat /app/frontend/dist/index.html
echo ""
echo "===================================================="
echo ""
echo "--- DIAGNÓSTICO CONCLUÍDO. TENTANDO INICIAR O SERVIDOR GUNICORN... ---"
echo ""


# Inicia o servidor Gunicorn em primeiro plano.
# O 'exec' substitui o processo do script pelo Gunicorn, o que é uma boa prática.
exec gunicorn src.main:app \
    --chdir /app/backend \
    --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
    -w 1 \
    --bind 0.0.0.0:8000
