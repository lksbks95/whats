# --- Estágio 1: Builder Híbrido (Node.js + Python) ---
# Usamos uma imagem Node para ter acesso ao npm/pnpm
FROM node:18-slim AS builder

# Define o diretório de trabalho
WORKDIR /app

# --- Instalação do Frontend ---
COPY frontend/package.json frontend/pnpm-lock.yaml ./frontend/
RUN npm install -g pnpm
RUN cd frontend && pnpm install
COPY frontend/ ./frontend/
RUN cd frontend && pnpm run build

# --- Instalação do Gateway ---
COPY backend/gateway/package.json ./backend/gateway/
RUN cd backend/gateway && npm install

# --- Estágio 2: Aplicação Final com Python ---
# Usamos uma imagem Python para a versão final, mais leve
FROM python:3.10-slim

# --- ALTERAÇÃO PRINCIPAL AQUI ---
# Instala o Node.js E as dependências necessárias para o Puppeteer/Chromium
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    # --- DEPENDÊNCIAS DO PUPPETEER/CHROMIUM ---
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    wget \
    xdg-utils \
    # --- FIM DAS DEPENDÊNCIAS ---
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia as dependências do Python e instala-as
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do backend (incluindo o gateway com seu package.json)
COPY backend/ ./backend/
# Copia os módulos já instalados do gateway do estágio anterior
COPY --from=builder /app/backend/gateway/node_modules ./backend/gateway/node_modules

# Copia o frontend já compilado
COPY --from=builder /app/frontend/dist ./frontend/dist

# --- Script de Inicialização ---
# Copia e torna o script de inicialização executável
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Expõe a porta 8000, onde o Gunicorn irá ouvir
EXPOSE 8000

# O comando final agora chama o nosso script para iniciar os dois serviços
CMD ["./entrypoint.sh"]
