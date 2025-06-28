import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- Configuração Robusta de Caminhos ---
# O diretório do backend é onde este script está
backend_dir = os.path.dirname(os.path.abspath(__file__))
# O diretório raiz do projeto está um nível acima
project_root = os.path.dirname(backend_dir)
# A pasta de build do frontend está em /frontend/build
frontend_folder = os.path.join(project_root, 'frontend', 'build')

# Adiciona o diretório 'src' do backend ao path para encontrar os módulos
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
    print("Certifique-se de que o comando de build do frontend foi executado com sucesso.")

# Inicializa o Flask, instruindo-o a servir arquivos da pasta 'build' do frontend
app = Flask(__name__, static_folder=frontend_folder)

# --- Configurações da Aplicação ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mude-esta-chave-secreta-em-producao')
# A DATABASE_URL será fornecida pelo Koyeb através das variáveis de ambiente
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
# Esta rota "catch-all" garante que o React Router funcione.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    # Se o caminho for um ficheiro existente na pasta de build, serve-o.
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    # Caso contrário, serve o index.html principal para o React Router.
    else:
        index_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, 'index.html')
        else:
            return "Erro: index.html não encontrado. Execute o build do frontend.", 404

# --- Contexto da Aplicação para criar o DB e dados iniciais ---
# Em produção, a criação de dados deve ser feita com mais cuidado (ex: um comando CLI)
with app.app_context():
    db.create_all()
    # Criar usuário admin padrão se não existir
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin', name='Administrador',
            email='admin@example.com', role='admin', is_active=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("Usuário admin padrão criado.")

# Este bloco só é executado se corrermos "python main.py" diretamente (para desenvolvimento local)
if __name__ == '__main__':
    print("🚀 Iniciando servidor de desenvolvimento...")
    # Em produção, o Koyeb usará o Gunicorn definido no 'koyeb.yaml'
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
