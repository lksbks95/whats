# Sistema de Atendimento WhatsApp

Este repositório contém o código-fonte de um sistema de atendimento WhatsApp completo, desenvolvido com Flask (Python) para o backend e React (JavaScript) para o frontend.

## Funcionalidades

- **Autenticação JWT**: Sistema de login seguro com JSON Web Tokens.
- **Gerenciamento de Usuários**: CRUD completo de usuários com diferentes níveis de acesso (admin, gerenciador, agente).
- **Gerenciamento de Departamentos**: Criação e gestão de departamentos para organização de atendimentos.
- **Integração WhatsApp**: Estrutura para conexão com a API do WhatsApp Business, permitindo o envio e recebimento de mensagens.
- **Sistema de Conversas**: Gerenciamento de conversas em tempo real, com histórico e status.
- **Transferência de Atendimentos**: Capacidade de transferir conversas entre agentes e departamentos.
- **Anexo de Arquivos**: Suporte para envio e visualização de arquivos nas conversas.
- **Dashboard Administrativo**: Visão geral e controle do sistema.

## Estrutura do Projeto

O projeto é dividido em duas partes principais:

- `backend/`: Contém o código-fonte do servidor Flask (Python).
- `frontend/`: Contém o código-fonte da aplicação React (JavaScript).

## Como Configurar e Rodar (Desenvolvimento)

### Backend (Flask)

1.  **Navegue até o diretório do backend:**
    ```bash
    cd backend
    ```
2.  **Crie e ative um ambiente virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure as variáveis de ambiente:**
    Crie um arquivo `.env` na raiz do diretório `backend` com as seguintes variáveis (exemplo):
    ```
    SECRET_KEY=sua_chave_secreta_aqui
    DATABASE_URL=sqlite:///app.db
    WHATSAPP_API_URL=https://graph.facebook.com/v18.0
    WHATSAPP_TOKEN=seu_token_do_whatsapp_business_api
    WHATSAPP_PHONE_ID=seu_id_do_telefone_do_whatsapp
    ```
5.  **Execute o servidor Flask:**
    ```bash
    python src/main.py
    ```
    O backend estará disponível em `http://localhost:5000`.

### Frontend (React)

1.  **Navegue até o diretório do frontend:**
    ```bash
    cd frontend
    ```
2.  **Instale as dependências:**
    ```bash
    pnpm install
    # ou npm install
    # ou yarn install
    ```
3.  **Execute a aplicação React:**
    ```bash
    pnpm run dev
    # ou npm start
    # ou yarn start
    ```
    O frontend estará disponível em `http://localhost:5173` (ou outra porta, dependendo da configuração).

## Implantação

Para implantar a aplicação, você precisará configurar um ambiente de produção que sirva tanto o backend Flask quanto o frontend React. Uma abordagem comum é construir o frontend e servir os arquivos estáticos através do servidor Flask.

## Contas de Demonstração

Para testar o sistema, você pode usar as seguintes credenciais:

- **Admin:** `admin` / `admin123`
- **Gerenciador:** `manager` / `manager123`

## Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

