import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- INICIALIZAÇÃO DE OBJETOS GLOBAIS ---
# A aplicação Flask e a extensão SocketIO são criadas ANTES de tudo.
backend_src_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(backend_src_dir)
project_root = os.path.dirname(backend_dir)
# A pasta 'dist' gerada pelo build do frontend é definida como a pasta de arquivos estáticos.
frontend_folder = os.path.join(project_root, 'frontend', 'dist')

# O 'static_url_path' vazio faz com que o Flask procure por arquivos a partir da raiz do site.
app = Flask(__name__, static_folder=frontend_folder, static_url_path='')

# Anexa o SocketIO ao 'app'.
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

# Importa a instância 'db' e os modelos.
from src.models import db, User

# --- IMPORTAÇÃO DE ROTAS (BLUEPRINTS) ---
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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mude-esta-chave-secreta-em-producao')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(backend_dir, 'dev.db')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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


# --- ROTA PARA SERVIR A APLICAÇÃO REACT ---
# Esta rota "catch-all" garante que o React controle a navegação no frontend.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # Se o caminho solicitado existir na pasta de build do frontend (ex: /static/css/main.css),
    # o Flask irá servi-lo automaticamente por causa da configuração 'static_folder'.
    # Se não for um arquivo estático conhecido, servimos o 'index.html' principal.
    # Isso permite que o React-Router lide com as rotas do lado do cliente (ex: /dashboard, /settings).
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


# --- COMANDOS FINAIS ---
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
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
