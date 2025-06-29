#!/bin/sh
set -e

# Este script serve como o ponto de entrada principal para o container.
# Ele simplesmente executa o Supervisor. O benefício é que este script
# herda todas as variáveis de ambiente do Koyeb (como DATABASE_URL)
# e passa-as para os processos que o Supervisor inicia.

# Inicia o supervisord em primeiro plano (necessário para o Docker)
exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf
