from flask import Blueprint, request, jsonify
from flask_cors import CORS
from src.models.user import db, User, Department
from src.models.activity_log import ActivityLog # Importa o modelo de log
from src.routes.auth import token_required, admin_required

# --- CORREÇÃO AQUI ---
# A criação do Blueprint deve vir ANTES de ser usado para definir as rotas.
user_bp = Blueprint('user', __name__)
CORS(user_bp)


@user_bp.route('/users', methods=['GET'])
@token_required
@admin_required
def get_users(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        users = User.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar usuários: {str(e)}'}), 500

@user_bp.route('/users', methods=['POST'])
@token_required
@admin_required
def create_user(current_user):
    try:
        data = request.get_json()
        
        required_fields = ['username', 'password', 'name', 'email', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Campo {field} é obrigatório'}), 400
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Nome de usuário já existe'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email já existe'}), 400
        
        new_user = User(
            username=data['username'],
            name=data['name'],
            email=data['email'],
            role=data['role'],
            department_id=data.get('department_id'),
            is_active=data.get('is_active', True)
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()

        # Regista a atividade de criação
        log_message = f"Novo utilizador '{new_user.name}' foi criado."
        new_log = ActivityLog(
            event_type='USER_CREATED',
            user_id=current_user.id,
            message=log_message
        )
        db.session.add(new_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao criar usuário: {str(e)}'}), 500

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
@admin_required
def update_user(current_user, user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            user.name = data['name']
        
        if 'email' in data:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'message': 'Email já existe'}), 400
            user.email = data['email']
        
        if 'role' in data:
            user.role = data['role']
        
        if 'department_id' in data:
            user.department_id = data['department_id']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário atualizado com sucesso',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao atualizar usuário: {str(e)}'}), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(current_user, user_id):
    try:
        if user_id == current_user.id:
            return jsonify({'message': 'Não é possível deletar seu próprio usuário'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar usuário: {str(e)}'}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar usuário: {str(e)}'}), 500
