import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- Importação Centralizada de Modelos ---
# Garante que o SQLAlchemy conhece todas as tabelas antes de a aplicação arrancar.
from src.models import db, User, Department, Conversation, Contact, ActivityLog, WhatsAppConnection, Message

# --- Importação de Todas as Rotas (Blueprints) ---
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

# --- Configuração de Caminhos ---
backend_src_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(backend_src_dir)
project_root = os.path.dirname(backend_dir)
frontend_folder = os.path.join(project_root, 'frontend', 'dist')

if not os.path.exists(frontend_folder):
    print(f"AVISO: Pasta de build do frontend não encontrada em: {frontend_folder}")

# Inicializa o Flask
app = Flask(__name__, static_folder=frontend_folder)

# --- Configurações da Aplicação ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mude-esta-chave-secreta')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(backend_dir, 'dev.db')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Inicialização de Extensões ---
CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")
db.init_app(app) # Associa a instância 'db' com a aplicação Flask
limiter = Limiter(key_func=get_remote_address, app=app)

# --- Registro de Blueprints da API ---
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

# --- Rota para Servir o Frontend ---
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
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
