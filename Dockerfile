# -----------------------------------------------------------------------------
# Dockerfile para a aplicação Backend (Python/Flask) - CORRIGIDO
# -----------------------------------------------------------------------------

# Etapa 1: Use uma imagem oficial e leve do Python como base
FROM python:3.11-slim

# Defina variáveis de ambiente para um comportamento ideal do Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de dependências para o diretório de trabalho
COPY backend/requirements.txt .

# Instale as dependências do projeto
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie o código-fonte do backend para o contêiner.
COPY ./backend/src ./src

# Crie e use um usuário não-root por segurança
RUN addgroup --system app && adduser --system --group app
USER app

# Exponha a porta em que o Gunicorn será executado
EXPOSE 10000

# O comando CORRETO para iniciar uma aplicação Flask com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "src.main:app"]
