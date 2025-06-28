import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- Configuração Robusta de Caminhos ---
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
# ***** CORREÇÃO AQUI: Trocado 'build' por 'dist' *****
frontend_folder = os.path.join(project_root, 'frontend', 'dist')

# Adiciona o diretório 'src' do backend ao path
sys.path.insert(0, os.path.join(backend_dir, 'src'))

# Importa os componentes do seu projeto
from models.user import db, User, Department
from routes.auth import auth_bp
from routes.user import user_bp
from routes.department import department_bp
from routes.whatsapp import whatsapp_bp
from routes.conversation import conversation_bp
from routes.file import file_bp

# Se a pasta de build não existir, avisa no console
if not os.path.exists(frontend_folder):
    print(f"AVISO: Pasta de build do frontend não encontrada em: {frontend_folder}")

# Inicializa o Flask, instruindo-o a servir arquivos da pasta 'dist' do frontend
app = Flask(__name__, static_folder=frontend_folder)

# --- Configurações da Aplicação ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mude-esta-chave-secreta-em-producao')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(backend_dir, 'dev.db')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Inicialização de Extensões ---
CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")
db.init_app(app)
limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["200 per minute"])

# --- Registro de Blueprints da API ---
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(department_bp, url_prefix='/api')
app.register_blueprint(whatsapp_bp, url_prefix='/api')
app.register_blueprint(conversation_bp, url_prefix='/api')
app.register_blueprint(file_bp, url_prefix='/api')

# --- Rota para Servir o Frontend (Single Page Application) ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path.startswith("api/"):
        return "Not Found", 404
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        index_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, 'index.html')
        else:
            return "Erro: index.html não encontrado.", 404

# --- Contexto da Aplicação ---
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', name='Administrador', email='admin@example.com', role='admin', is_active=True)
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("Usuário admin padrão criado.")

# --- Execução ---
if __name__ == '__main__':
    print("🚀 Iniciando servidor de desenvolvimento...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
