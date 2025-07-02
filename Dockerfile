# --- Estágio 1: Builder Híbrido (Node.js + Python) ---
FROM node:18-slim AS builder
WORKDIR /app

# Build do Frontend
COPY frontend/package.json frontend/pnpm-lock.yaml ./frontend/
RUN npm install -g pnpm && cd frontend && pnpm install
COPY frontend/ ./frontend/
RUN cd frontend && pnpm run build

# Instalação do Gateway
COPY backend/gateway/package.json ./backend/gateway/
RUN cd backend/gateway && npm install

# --- Estágio 2: Aplicação Final ---
FROM python:3.10-slim

# Instala Node.js e as dependências do Puppeteer
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    ca-certificates fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgbm1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 lsb-release wget xdg-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências Python
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia os códigos-fonte e os módulos instalados
COPY backend/ ./backend/
COPY --from=builder /app/backend/gateway/node_modules ./backend/gateway/node_modules
COPY --from=builder /app/frontend/dist ./frontend/dist

# Define o PYTHONPATH para que as importações 'from src...' funcionem
ENV PYTHONPATH /app/backend

# Expõe a porta que a Render irá usar
EXPOSE 10000

# --- COMANDO FINAL SIMPLIFICADO ---
# Inicia o servidor Gunicorn diretamente. Ele irá carregar o main.py, que por sua vez iniciará o gateway.
# Ele ouve na porta 10000, que é o padrão da Render.
CMD ["gunicorn", "src.main:app", "--chdir", "/app/backend", "--worker-class", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "1", "--bind", "0.0.0.0:10000"]
