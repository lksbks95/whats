import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import html # Importado para a rota de depuração

# --- INICIALIZAÇÃO DE OBJETOS GLOBAIS ---
backend_src_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(backend_src_dir)
project_root = os.path.dirname(backend_dir)
frontend_folder = os.path.join(project_root, 'frontend', 'dist')

app = Flask(__name__, static_folder=frontend_folder, static_url_path='')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

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
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
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


# ====================================================================
# --- ROTA DE DIAGNÓSTICO TEMPORÁRIA ---
# Este é o bloco de código que foi adicionado para nos ajudar.
# ====================================================================
@app.route('/debug-fs')
def debug_filesystem():
    """
    Esta é uma rota temporária para nos ajudar a depurar o problema dos arquivos estáticos.
    Ela mostra a estrutura de arquivos do frontend e o conteúdo do index.html.
    """
    path_to_check = app.static_folder
    response_html = "<h1>Diagnóstico do Sistema de Arquivos do Servidor</h1>"
    response_html += "<p>Verificando a pasta de arquivos estáticos configurada no Flask.</p>"

    # 1. Lista a estrutura de arquivos usando os.walk
    response_html += f"<h2>1. Estrutura de Arquivos em: '{path_to_check}'</h2>"
    response_html += "<pre style='background-color:#f4f4f4; border:1px solid #ddd; padding: 10px;'>"
    file_list = []
    for root, dirs, files in os.walk(path_to_check):
        level = root.replace(path_to_check, '').count(os.sep)
        indent = ' ' * 4 * level
        file_list.append(f'{indent}{os.path.basename(root)}/')
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            file_list.append(f'{sub_indent}{f}')
    response_html += "\n".join(file_list)
    response_html += "</pre>"

    # 2. Exibe o conteúdo do index.html para vermos os caminhos dos links
    index_path = os.path.join(path_to_check, 'index.html')
    response_html += f"<h2>2. Conteúdo de: '{index_path}'</h2>"
    response_html += "<h4>(Verifique os caminhos 'href' para CSS e 'src' para JS abaixo)</h4>"
    response_html += "<pre style='background-color:#f4f4f4; border:1px solid #ddd; padding: 10px;'>"
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            response_html += html.escape(f.read())
    except Exception as e:
        response_html += f"Erro ao tentar ler o arquivo index.html: {e}"
    response_html += "</pre>"

    return response_html
# ====================================================================
# --- FIM DA ROTA DE DIAGNÓSTICO ---
# ====================================================================


# --- PONTO DE ENTRADA PARA DESENVOLVIMENTO LOCAL ---
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
