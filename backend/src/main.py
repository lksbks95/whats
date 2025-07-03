# backend/src/main.py

import os
# Removido: import subprocess
# Removido: import atexit
import logging
# Removido: import socket
# Removido: from urllib.parse import urlparse
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


# O código de depuração de rede foi removido daqui.

# --- CÓDIGO DE DEPURAÇÃO DE CONECTIVIDADE ---
print("--- INICIANDO TESTE DE CONEXÃO DE REDE ---", flush=True)
database_url = os.environ.get("SQLALCHEMY_DATABASE_URI")

if not database_url:
    print(">>> ERRO: Variável de ambiente SQLALCHEMY_DATABASE_URI não encontrada.", flush=True)
else:
    try:
        parsed_url = urlparse(database_url)
        db_host = parsed_url.hostname
        db_port = parsed_url.port
        print(f"--- DEBUG: Tentando conectar ao Host: {db_host} na Porta: {db_port}", flush=True)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10) # Timeout de 10 segundos
        result = sock.connect_ex((db_host, db_port))

        if result == 0:
            print(">>> SUCESSO: A conexão de rede foi possível. A porta está aberta.", flush=True)
        else:
            print(f">>> FALHA: A conexão de rede falhou. Código de erro do socket: {result}", flush=True)
        sock.close()
    except Exception as e:
        print(f">>> ERRO: Uma exceção ocorreu durante o teste: {e}", flush=True)

print("--- FIM DO TESTE DE CONEXÃO DE REDE ---", flush=True)
# --- FIM DO CÓDIGO DE DEPURAÇÃO ---


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

# --- LÓGICA DO GATEWAY NODE.JS DESATIVADA ---
# As funções start_gateway, stop_gateway e o registro do atexit foram removidos.
# A chamada start_gateway() também foi removida.

# Cria as tabelas do banco de dados (se necessário)
with app.app_context():
    db.create_all()
