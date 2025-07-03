# Estágio ÚNICO: Aplicação Python
FROM python:3.10-slim

WORKDIR /app

# Instala dependências Python
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código-fonte do backend
COPY backend/ ./backend/

# Copia o frontend já buildado (assumindo que você tem a pasta 'dist')
COPY frontend/dist ./frontend/dist

# Define o PYTHONPATH para que as importações 'from src...' funcionem
ENV PYTHONPATH /app/backend

# Expõe a porta que a Render irá usar
EXPOSE 10000

# Comando final para iniciar o Gunicorn
CMD ["gunicorn", "src.main:app", "--chdir", "/app/backend", "--worker-class", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "1", "--bind", "0.0.0.0:10000"]
