# backend/src/main.py

import os
import subprocess
import atexit
import logging
import socket
from urllib.parse import urlparse
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# --- INICIALIZAÇÃO DE OBJETOS GLOBAIS ---
backend_src_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(backend_src_dir)
project_root = os.path.dirname(backend_dir)
frontend_folder = os.path.join(project_root, 'frontend', 'dist')

app = Flask(__name__, static_folder=frontend_folder, static_url_path='')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

# Importação dos modelos e rotas
from src.models import db, User
from src.routes.auth import auth_bp
from src.routes.user import user_bp
from src.routes.department import department_bp
from src.routes.whatsapp import whatsapp_bp
from src.routes.conversation import conversation_bp
from src.routes.file import file_bp
from src.routes.profile import profile_bp
from src.routes.activity import activity_bp
from src.routes.contact import contact_bp
from src.routes.dashboard import dashboard_bp
from src.routes.settings import settings_bp

# --- CONFIGURAÇÃO CENTRALIZADA DA APLICAÇÃO ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma-chave-secreta-forte-e-aleatoria')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# ==============================================================================
# --- CÓDIGO DE DEPURAÇÃO DE CONECTIVIDADE ---
# ==============================================================================
print("--- INICIANDO TESTE DE CONEXÃO DE REDE ---", flush=True)
database_url_from_env = os.environ.get("SQLALCHEMY_DATABASE_URI")

if not database_url_from_env:
    print("ERRO DE DEBUG: Variável de ambiente SQLALCHEMY_DATABASE_URI não foi encontrada.", flush=True)
else:
    print(f"DEBUG: URL do banco encontrada: {database_url_from_env}", flush=True)
    try:
        # Extrai o hostname e a porta da URL
        parsed_url = urlparse(database_url_from_env)
        db_host = parsed_url.hostname
        db_port = parsed_url.port
        print(f"DEBUG: Tentando conectar ao Host: {db_host} na Porta: {db_port}", flush=True)

        # Tenta criar uma conexão de socket de baixo nível
        socket.setdefaulttimeout(10)  # Timeout de 10 segundos
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((db_host, db_port))
        
        if result == 0:
            print(">>> SUCESSO: A porta está aberta. A conexão de rede com o banco de dados é POSSÍVEL.", flush=True)
        else:
            print(f">>> FALHA: A porta NÃO está aberta. Código de erro do socket: {result}. A conexão de rede FALHOU.", flush=True)
        sock.close()

    except Exception as e:
        print(f"ERRO DE DEBUG: Ocorreu uma exceção durante o teste de conexão: {e}", flush=True)

print("--- FIM DO TESTE DE CONEXÃO DE REDE ---", flush=True)
# ==============================================================================
# Fim do código de depuração
# ==============================================================================


db.init_app(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})
limiter = Limiter(key_func=get_remote_address, app=app)

# --- REGISTRO DOS BLUEPRINTS DA API ---
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(department_bp, url_prefix='/api')
app.register_blueprint(whatsapp_bp, url_prefix='/api')
app.register_blueprint(conversation_bp, url_prefix='/api')
app.register_blueprint(file_bp, url_prefix='/api')
app.register_blueprint(profile_bp, url_prefix='/api')
app.register_blueprint(activity_bp, url_prefix='/api')
app.register_blueprint(contact_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api')
app.register_blueprint(settings_bp, url_prefix='/api')

# --- ROTA PARA SERVIR A APLICAÇÃO REACT ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# --- LÓGICA PARA INICIAR O GATEWAY NODE.JS ---
gateway_process = None

def start_gateway():
    global gateway_process
    gateway_path = os.path.join(backend_dir, 'gateway', 'index.js')
    if os.path.exists(gateway_path):
        logging.info("Iniciando o Gateway de WhatsApp como um subprocesso...")
        # Usamos Popen para iniciar o processo sem bloquear a aplicação Flask
        gateway_process = subprocess.Popen(['node', gateway_path])
        logging.info(f"Gateway iniciado com PID: {gateway_process.pid}")
    else:
        logging.warning(f"Arquivo do gateway não encontrado em: {gateway_path}")

def stop_gateway():
    global gateway_process
    if gateway_process:
        logging.info("Finalizando o processo do Gateway...")
        gateway_process.terminate()
        gateway_process.wait()
        logging.info("Processo do Gateway finalizado.")

# Registra a função para ser chamada quando a aplicação Flask for encerrada
atexit.register(stop_gateway)

# Inicia o gateway apenas uma vez quando o módulo é carregado
start_gateway()

# Cria as tabelas do banco de dados (se necessário)
with app.app_context():
    db.create_all()
