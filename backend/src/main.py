import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- Importação Simplificada ---
# Importa a instância 'db' e os modelos necessários diretamente.
# O __init__.py já garante que todos os modelos são conhecidos pelo SQLAlchemy.
from src.models import db, User

# Importa todas as rotas
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

def create_app():
    """Cria e configura a instância da aplicação Flask."""
    
    backend_src_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(backend_src_dir)
    project_root = os.path.dirname(backend_dir)
    frontend_folder = os.path.join(project_root, 'frontend', 'dist')
    
    app = Flask(__name__, static_folder=frontend_folder, static_url_path='')

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mude-esta-chave-secreta')
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(backend_dir, 'dev.db')}")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        print("ERRO FATAL: A variável de ambiente DATABASE_URL não está definida.")
        # Fallback para desenvolvimento local, se necessário
        # app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(backend_dir, 'dev.db')}"

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    limiter = Limiter(key_func=get_remote_address, app=app)
    
    # Registo de Blueprints
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

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react_app(path):
        if path.startswith("api/"):
            return "Not Found", 404
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', name='Administrador', email='admin@example.com', role='admin', is_active=True)
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("Usuário admin padrão criado.")

    return app

app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
