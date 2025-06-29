import os
import sys
import subprocess

# Este script atua como um wrapper para lançar o Gunicorn de forma robusta.
# Ele garante que o ambiente Python está configurado corretamente.

print("--- A iniciar o runner.py do backend ---")

# 1. Adicionar o diretório 'src' ao caminho do Python
# Isto permite que importações como 'from models import ...' funcionem.
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)
print(f"Caminho 'src' adicionado ao PYTHONPATH: {src_path}")

# 2. Verificar a variável de ambiente da base de dados
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("ERRO FATAL: A variável de ambiente DATABASE_URL não foi encontrada.")
    # Em desenvolvimento, você poderia definir um valor padrão aqui, mas em produção,
    # a aplicação deve falhar se a base de dados não estiver configurada.
    sys.exit(1)
else:
    print("SUCESSO: A variável de ambiente DATABASE_URL foi encontrada.")

# 3. Preparar o comando para executar o Gunicorn
# Apontamos para o ficheiro wsgi.py que criámos anteriormente.
command = [
    'gunicorn',
    'wsgi:socketio', # Aponta para a variável 'socketio' no ficheiro 'wsgi.py'
    '--chdir', src_path, # Define o diretório de trabalho para 'src'
    '--worker-class', 'geventwebsocket.gunicorn.workers.GeventWebSocketWorker',
    '-w', '1',
    '--bind', '0.0.0.0:8000'
]

print(f"A executar o comando Gunicorn: {' '.join(command)}")

# 4. Executar o Gunicorn
# O 'exec' substitui o processo atual pelo Gunicorn, o que é uma boa prática.
os.execvp(command[0], command)
