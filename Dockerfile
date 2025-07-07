# -----------------------------------------------------------------------------
# Dockerfile para a aplicação Backend (Python/FastAPI)
# -----------------------------------------------------------------------------

# Etapa 1: Use uma imagem oficial e leve do Python como base
FROM python:3.11-slim

# Defina variáveis de ambiente para um comportamento ideal do Python
# 1. Impede o Python de gerar arquivos .pyc
# 2. Garante que os logs apareçam imediatamente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de dependências para o diretório de trabalho
# Isso é feito primeiro para aproveitar o cache do Docker. Se o requirements.txt
# não mudar, o Docker não precisará reinstalar as dependências a cada build.
COPY backend/requirements.txt .

# Instale as dependências do projeto
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie o código-fonte do backend para o contêiner.
# O código local da pasta `backend/src` será copiado para a pasta `/app/src` no contêiner.
COPY ./backend/src ./src

# Crie um grupo e um usuário não-root para executar a aplicação (melhor prática de segurança)
RUN addgroup --system app && adduser --system --group app
USER app

# Exponha a porta em que o Gunicorn será executado.
# O Render irá mapear a porta externa (80/443) para esta porta interna.
EXPOSE 10000

# O comando para iniciar a aplicação usando Gunicorn com workers Uvicorn
# - "src.main:app": Aponta para a instância 'app' no arquivo 'src/main.py'
# - "--bind 0.0.0.0:10000": Ouve em todas as interfaces de rede na porta 10000
CMD ["gunicorn", "src.main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:10000"]
