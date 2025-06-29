#!/bin/sh
set -e

# Este script serve como o ponto de entrada principal para o container.
# Ele herda todas as variáveis de ambiente do Koyeb (como DATABASE_URL).

echo "--- A iniciar o entrypoint.sh ---"

# 1. Define o PYTHONPATH.
# Isto diz ao Python para procurar módulos a partir da pasta /app/backend,
# resolvendo os erros de 'No module named src'.
export PYTHONPATH=/app/backend
echo "PYTHONPATH definido para: $PYTHONPATH"

# 2. Inicia o Supervisor.
# O 'exec' garante que o Supervisor herda o ambiente que acabámos de configurar.
# Ele irá então iniciar o Gunicorn e o Nginx com o ambiente correto.
exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf
