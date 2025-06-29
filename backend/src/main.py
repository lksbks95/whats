import os
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from src.models import db, User
from src.routes.auth import auth_bp
from src.routes.user import user_bp
# ... importe todos os seus outros blueprints ...

app = Flask(__name__)

# --- Configurações da Aplicação ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mude-esta-chave-secreta')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Inicialização de Extensões ---
CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")
db.init_app(app)
limiter = Limiter(key_func=get_remote_address, app=app)

# --- Registro de Blueprints da API ---
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
# ... registe todos os seus outros blueprints ...

# --- Contexto da Aplicação ---
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', name='Administrador', email='admin@example.com', role='admin', is_active=True)
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("Usuário admin padrão criado.")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)
