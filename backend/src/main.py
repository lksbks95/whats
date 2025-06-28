import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from src.models.user import db, User, Department
from src.routes.auth import auth_bp
from src.routes.user import user_bp
from src.routes.department import department_bp
from src.routes.whatsapp import whatsapp_bp
from src.routes.conversation import conversation_bp
from src.routes.file import file_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Configuração CORS
CORS(app, origins="*")

# Configuração SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per 15 minutes"]
)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(department_bp, url_prefix='/api')
app.register_blueprint(whatsapp_bp, url_prefix='/api')
app.register_blueprint(conversation_bp, url_prefix='/api')
app.register_blueprint(file_bp, url_prefix='/api')

# Criar tabelas e dados iniciais
with app.app_context():
    db.create_all()
    
    # Criar usuário admin padrão se não existir
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            name='Administrador',
            email='admin@whatsapp-system.com',
            role='admin',
            is_active=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
    
    # Criar usuário manager padrão se não existir
    manager_user = User.query.filter_by(username='manager').first()
    if not manager_user:
        manager_user = User(
            username='manager',
            name='Gerenciador',
            email='manager@whatsapp-system.com',
            role='manager',
            is_active=True
        )
        manager_user.set_password('manager123')
        db.session.add(manager_user)
    
    # Criar departamentos padrão se não existirem
    if not Department.query.first():
        vendas = Department(name='Vendas', description='Departamento de vendas')
        suporte = Department(name='Suporte', description='Departamento de suporte técnico')
        marketing = Department(name='Marketing', description='Departamento de marketing')
        db.session.add(vendas)
        db.session.add(suporte)
        db.session.add(marketing)
    
    db.session.commit()
    print("✅ Banco de dados inicializado com dados padrão")
    print("👤 Usuários criados:")
    print("   - Admin: admin/admin123")
    print("   - Manager: manager/manager123")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    # Se for um arquivo estático específico
    if path.startswith('static/'):
        file_path = os.path.join(static_folder_path, path)
        if os.path.exists(file_path):
            return send_from_directory(static_folder_path, path)
    
    # Se for um arquivo na raiz
    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    
    # Para qualquer outra rota, servir o index.html (SPA)
    index_path = os.path.join(static_folder_path, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(static_folder_path, 'index.html')
    else:
        return "index.html not found", 404

# Socket.IO events para # Socket.IO Events
@socketio.on('connect')
def handle_connect(auth):
    print(f'Cliente conectado: {request.sid}')
    emit('connected', {'message': 'Conectado ao servidor'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Cliente desconectado: {request.sid}')

@socketio.on('join_conversation')
def handle_join_conversation(data):
    """Entrar em uma sala de conversa"""
    conversation_id = data.get('conversation_id')
    if conversation_id:
        join_room(f'conversation_{conversation_id}')
        emit('joined_conversation', {'conversation_id': conversation_id})
        print(f'Cliente {request.sid} entrou na conversa {conversation_id}')

@socketio.on('leave_conversation')
def handle_leave_conversation(data):
    """Sair de uma sala de conversa"""
    conversation_id = data.get('conversation_id')
    if conversation_id:
        leave_room(f'conversation_{conversation_id}')
        emit('left_conversation', {'conversation_id': conversation_id})
        print(f'Cliente {request.sid} saiu da conversa {conversation_id}')

@socketio.on('typing')
def handle_typing(data):
    """Indicar que está digitando"""
    conversation_id = data.get('conversation_id')
    user_name = data.get('user_name')
    if conversation_id and user_name:
        emit('user_typing', {
            'conversation_id': conversation_id,
            'user_name': user_name
        }, room=f'conversation_{conversation_id}', include_self=False)

@socketio.on('stop_typing')
def handle_stop_typing(data):
    """Parar de indicar que está digitando"""
    conversation_id = data.get('conversation_id')
    user_name = data.get('user_name')
    if conversation_id and user_name:
        emit('user_stop_typing', {
            'conversation_id': conversation_id,
            'user_name': user_name
        }, room=f'conversation_{conversation_id}', include_self=False)

def notify_new_message(conversation_id, message_data):
    """Notificar nova mensagem via Socket.IO"""
    socketio.emit('new_message', {
        'conversation_id': conversation_id,
        'message': message_data
    }, room=f'conversation_{conversation_id}')

def notify_conversation_transfer(conversation_id, transfer_data):
    """Notificar transferência de conversa via Socket.IO"""
    socketio.emit('conversation_transferred', {
        'conversation_id': conversation_id,
        'transfer': transfer_data
    }, room=f'conversation_{conversation_id}')

# Servir arquivos estáticos do React
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    if path.startswith('api/'):
        # Se for uma rota da API, retorna 404
        abort(404)
    
    # Verifica se o arquivo existe
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(app.static_folder, path)
    else:
        # Para rotas do React Router, serve o index.html
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    print("🚀 Iniciando Sistema de Atendimento WhatsApp")
    print("📱 Funcionalidades disponíveis:")
    print("   ✅ Gerenciamento de usuários e departamentos")
    print("   ✅ Autenticação JWT")
    print("   ✅ APIs REST completas")
    print("   ✅ Socket.IO para tempo real")
    print("   ✅ Integração WhatsApp (simulada)")
    print("   ✅ Transferência de atendimentos")
    print("   ✅ Upload de arquivos")
    print("🌐 Servidor rodando em: http://0.0.0.0:5000")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

