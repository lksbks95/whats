import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- INICIALIZAÇÃO DE OBJETOS GLOBAIS ---
# A aplicação Flask e a extensão SocketIO são criadas ANTES de tudo.
# Isso garante que as variáveis 'app' e 'socketio' existam globalmente quando as rotas as importarem.

# Define os caminhos de pastas
backend_src_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(backend_src_dir)
project_root = os.path.dirname(backend_dir)
frontend_folder = os.path.join(project_root, 'frontend', 'dist')

# Cria a instância principal do Flask, que será o ponto de entrada para o Gunicorn
app = Flask(__name__, static_folder=frontend_folder, static_url_path='')

# Cria a instância do SocketIO e a anexa ao 'app'.
# O Gunicorn executará o 'app', e o SocketIO interceptará os pedidos de WebSocket.
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

# Importa a instância 'db' e os modelos. O db é inicializado mais tarde.
from src.models import db, User

# --- IMPORTAÇÃO DE ROTAS (BLUEPRINTS) ---
# As rotas são importadas somente DEPOIS que 'app' e 'socketio' já existem.
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


# --- CONFIGURAÇÃO CENTRALIZADA DA APLICAÇÃO ---

# Configurações da aplicação a partir de variáveis de ambiente ou valores padrão
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mude-esta-chave-secreta-em-producao')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(backend_dir, 'dev.db')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa as extensões com a aplicação
db.init_app(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})
limiter = Limiter(key_func=get_remote_address, app=app)

# Registo de todos os Blueprints
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

# --- ROTAS E COMANDOS FINAIS ---

# Rota para servir a aplicação React e os seus arquivos estáticos
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path.startswith("api/"):
        # Se a rota começar com /api/, o Flask já teria capturado em um blueprint.
        # Se chegou aqui, não foi encontrado.
        return "API endpoint not found", 404
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # Se o caminho não for um arquivo estático existente, serve o index.html do React.
        return send_from_directory(app.static_folder, 'index.html')

# Cria as tabelas do banco de dados e o usuário admin padrão
# O 'with app.app_context()' garante que a aplicação esteja configurada antes deste código rodar.
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', name='Administrador', email='admin@example.com', role='admin', is_active=True)
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("Usuário admin padrão criado.")

# --- PONTO DE ENTRADA PARA DESENVOLVIMENTO LOCAL ---
# Este bloco só será executado quando você rodar 'python src/main.py' diretamente.
# O Gunicorn IGNORA este bloco.
if __name__ == '__main__':
    # Usar socketio.run() permite o funcionamento correto do Flask-SocketIO no modo de desenvolvimento.
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
