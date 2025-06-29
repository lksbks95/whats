# --- Estágio 1: Construir o Frontend ---
# Esta parte continua igual: compila o seu código React.
FROM node:18 AS frontend-builder
WORKDIR /app
COPY frontend/package.json frontend/pnpm-lock.yaml ./frontend/
RUN cd frontend && npm install -g pnpm && pnpm install
COPY frontend/ ./frontend/
RUN cd frontend && pnpm run build

# --- Estágio 2: Aplicação Final com Python ---
# Usamos uma imagem Python e nada mais.
FROM python:3.10-slim

# Define a pasta de trabalho principal
WORKDIR /app

# Copia as dependências do Python e instala-as
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do backend
COPY backend/ ./backend/

# Copia o frontend já compilado do estágio anterior
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Define o PYTHONPATH para que as importações 'from src...' funcionem
ENV PYTHONPATH /app/backend

# Expõe a porta 8000, onde o nosso servidor Python irá ouvir
EXPOSE 8000

# --- O Comando Final e Único ---
# Inicia o servidor Gunicorn diretamente.
# Ele irá procurar pela variável 'socketio' no ficheiro 'src/main.py'.
CMD ["gunicorn", "src.main:socketio", "--chdir", "/app/backend", "--worker-class", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "1", "--bind", "0.0.0.0:8000"]
