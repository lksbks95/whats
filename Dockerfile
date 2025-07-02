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

# Instala o Node.js no ambiente Python para poder rodar o gateway
RUN apt-get update && apt-get install -y nodejs npm

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
