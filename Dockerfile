# --- Estágio 1: Construir o Frontend ---
FROM node:18 AS frontend-builder
WORKDIR /app
COPY frontend/package.json frontend/pnpm-lock.yaml ./frontend/
RUN cd frontend && npm install -g pnpm && pnpm install
COPY frontend/ ./frontend/
RUN cd frontend && pnpm run build

# --- Estágio 2: Aplicação Final com Python e Nginx ---
FROM python:3.10-slim

# Instala o Nginx e o supervisor (para gerir múltiplos processos)
RUN apt-get update && apt-get install -y nginx supervisor

# Instala as dependências do Python
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do backend
COPY backend/ ./backend/

# Copia o frontend já compilado do estágio anterior
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Copia as configurações do Nginx e do Supervisor
COPY nginx/nginx.conf /etc/nginx/sites-enabled/default
COPY supervisor/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expõe a porta 80, que é a porta do Nginx
EXPOSE 80

# O Supervisor irá iniciar o Nginx e o Gunicorn
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
