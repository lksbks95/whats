import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Importa a instância 'db' e todos os modelos
from .models import db, User

# Importa todos os blueprints (rotas)
from .routes.auth import auth_bp
from .routes.user import user_bp
from .routes.department import department_bp
from .routes.whatsapp import whatsapp_bp
from .routes.conversation import conversation_bp
from .routes.file import file_bp
from .routes.profile import profile_bp
from .routes.activity import activity_bp
from .routes.contact import contact_bp
from .routes.dashboard import dashboard_bp

def create_app():
    """
    Cria e configura a instância da aplicação Flask.
    Este é o Application Factory Pattern.
    """
    # --- Configuração de Caminhos ---
    backend_src_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(backend_src_dir)
    project_root = os.path.dirname(backend_dir)
    frontend_folder = os.path.join(project_root, 'frontend', 'dist')

    if not os.path.exists(frontend_folder):
        print(f"AVISO: Pasta de build do frontend não encontrada em: {frontend_folder}")

    app = Flask(__name__, static_folder=frontend_folder, static_url_path='')

    # --- Configurações da Aplicação ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mude-esta-chave-secreta')
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        print("ERRO FATAL: A variável de ambiente DATABASE_URL não está definida.")
        # Para desenvolvimento local, podemos usar um fallback
        # app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(backend_dir, 'dev.db')}"
    
    # --- Inicialização de Extensões ---
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    limiter = Limiter(key_func=get_remote_address, app=app)
    # O SocketIO será inicializado fora da factory para evitar problemas de contexto
    
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
            return send_from_directory(app.static_folder, 'index.html')

    # --- Contexto da Aplicação para criar tabelas ---
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', name='Administrador', email='admin@example.com', role='admin', is_active=True)
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("Usuário admin padrão criado.")

    return app

# Cria a aplicação usando a factory para ser usada pelo Gunicorn/SocketIO
app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*")

# --- Execução para desenvolvimento local ---
if __name__ == '__main__':
    # Usamos o socketio.run para desenvolvimento para suportar WebSockets
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
