# --- Estágio 1: Builder do Frontend ---
FROM node:18-slim AS builder
WORKDIR /app

# Build do Frontend
COPY frontend/package.json frontend/pnpm-lock.yaml ./frontend/
RUN npm install -g pnpm && cd frontend && pnpm install
COPY frontend/ ./frontend/
RUN cd frontend && pnpm run build

# --- Estágio 2: Aplicação Final ---
FROM python:3.10-slim

WORKDIR /app

# Instala dependências Python
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código-fonte do backend
COPY backend/ ./backend/

# Copia o frontend JÁ BUILDADO do estágio anterior
COPY --from=builder /app/frontend/dist ./frontend/dist

# Define o PYTHONPATH para que as importações 'from src...' funcionem
ENV PYTHONPATH /app/backend

# Expõe a porta
EXPOSE 10000

# Comando final para iniciar o Gunicorn (o gateway continua desativado no código Python)
CMD ["gunicorn", "src.main:app", "--chdir", "/app/backend", "--bind", "0.0.0.0:10000"]
