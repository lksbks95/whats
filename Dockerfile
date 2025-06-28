# --- Estágio 1: Construir o Frontend ---
# Usamos uma imagem Node.js para compilar o nosso React
FROM node:18 AS frontend-builder

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os ficheiros de configuração do frontend primeiro
COPY frontend/package.json frontend/pnpm-lock.yaml ./frontend/
RUN cd frontend && npm install -g pnpm && pnpm install

# Copia todo o resto do código do frontend
COPY frontend/ ./frontend/

# Executa o comando de build para compilar o React
# Isto irá criar uma pasta /app/frontend/dist
RUN cd frontend && pnpm run build

# --- Estágio 2: Construir a Aplicação Final com Python ---
# Usamos uma imagem Python para o nosso backend Flask
FROM python:3.10-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia as dependências do backend e instala-as
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copia o código do backend
COPY backend/ ./backend/

# Copia o frontend já compilado (a pasta 'dist') do estágio anterior
# Esta é a "ponte" entre o frontend e o backend
# ***** CORREÇÃO AQUI: Trocado 'build' por 'dist' *****
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expõe a porta que o Gunicorn irá usar
EXPOSE 8000

# Comando para iniciar o servidor em produção
# Inicia o Gunicorn a partir da pasta do backend
CMD ["gunicorn", "--chdir", "backend", "main:app", "--worker-class", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "1", "--bind", "0.0.0.0:8000"]

