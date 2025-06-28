# --- Estágio 1: Construir o Frontend ---
# Usamos uma imagem Node.js para compilar o nosso React
FROM node:18 AS frontend-builder

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os ficheiros de configuração do frontend primeiro para aproveitar o cache do Docker
COPY frontend/package.json frontend/pnpm-lock.yaml ./frontend/
RUN cd frontend && npm install -g pnpm && pnpm install

# Copia todo o resto do código do frontend
COPY frontend/ ./frontend/

# Executa o comando de build para compilar o React para a pasta /app/frontend/dist
RUN cd frontend && pnpm run build

# --- Estágio 2: Construir a Aplicação Final com Python ---
# Usamos uma imagem Python para o nosso backend Flask
FROM python:3.10-slim

# Define o diretório de trabalho para a raiz da aplicação
WORKDIR /app

# Copia as dependências do backend e instala-as
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copia todo o código do backend para a pasta /app/backend
COPY backend/ ./backend/

# Copia o frontend já compilado (a pasta 'dist') do estágio anterior
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Define a pasta de trabalho final para o diretório do backend.
# A partir daqui, os comandos são executados dentro de /app/backend
WORKDIR /app/backend

# Expõe a porta que o Gunicorn irá usar
EXPOSE 8000

# ***** CORREÇÃO AQUI *****
# Comando para iniciar o servidor, especificando o caminho do módulo a partir da pasta 'src'.
# O Gunicorn irá procurar por um ficheiro 'main.py' dentro da pasta 'src' e usar a variável 'app'.
CMD ["gunicorn", "src.main:app", "--worker-class", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "1", "--bind", "0.0.0.0:8000"]
