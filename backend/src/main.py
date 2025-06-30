import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- CORREÇÃO 1: INICIALIZAÇÃO PRIMEIRO ---
# A aplicação Flask e a extensão SocketIO são criadas ANTES de tudo.
# Isso garante que a variável 'socketio' exista globalmente quando as rotas a importarem.

# Define os caminhos de pastas
backend_src_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(backend_src_dir)
project_root = os.path.dirname(backend_dir)
frontend_folder = os.path.join(project_root, 'frontend', 'dist')

# Cria a instância principal do Flask
app = Flask(__name__, static_folder=frontend_folder, static_url_path='')

# Cria a instância do SocketIO, que o Gunicorn irá usar
# Adicionado async_mode='gevent' para ser compatível com o seu worker do Gunicorn
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

# Importa a instância 'db' e os modelos. O db é inicializado mais tarde.
from src.models import db, User

# --- CORREÇÃO 2: IMPORTAÇÃO DE ROTAS DEPOIS ---
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


# --- CORREÇÃO 3: CONFIGURAÇÃO CENTRALIZADA ---
# O resto da configuração da aplicação é feito aqui, em uma única sequência lógica.
# Isso substitui a função 'create_app'.

# Configurações da aplicação a partir de variáveis de ambiente ou valores padrão
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mude-esta-chave-secreta')
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

# Rota para servir a aplicação React e os seus arquivos estáticos
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path.startswith("api/"):
        return "Not Found", 404
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Cria as tabelas do banco de dados e o usuário admin padrão
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', name='Administrador', email='admin@example.com', role='admin', is_active=True)
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("Usuário admin padrão criado.")

# Bloco para execução direta (python main.py), útil para desenvolvimento local
if __name__ == '__main__':
    # O debug=True do socketio.run religa o servidor a cada alteração.
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
