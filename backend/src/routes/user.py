from flask import Blueprint, request, jsonify
from flask_cors import CORS
from src.models.user import db, User, Department
from src.routes.auth import token_required, admin_required

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
        
        # Validação dos campos obrigatórios
        required_fields = ['username', 'password', 'name', 'email', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se username já existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Nome de usuário já existe'}), 400
        
        # Verificar se email já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email já existe'}), 400
        
        # Validar role
        valid_roles = ['admin', 'manager', 'agent']
        if data['role'] not in valid_roles:
            return jsonify({'message': f'Role deve ser um dos: {", ".join(valid_roles)}'}), 400
        
        # Validar departamento se fornecido
        department_id = data.get('department_id')
        if department_id:
            department = Department.query.get(department_id)
            if not department:
                return jsonify({'message': 'Departamento não encontrado'}), 400
        
        # Criar novo usuário
        new_user = User(
            username=data['username'],
            name=data['name'],
            email=data['email'],
            role=data['role'],
            department_id=department_id,
            is_active=data.get('is_active', True)
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
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
        
        # Atualizar campos se fornecidos
        if 'name' in data:
            user.name = data['name']
        
        if 'email' in data:
            # Verificar se email já existe (exceto o próprio usuário)
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'message': 'Email já existe'}), 400
            user.email = data['email']
        
        if 'role' in data:
            valid_roles = ['admin', 'manager', 'agent']
            if data['role'] not in valid_roles:
                return jsonify({'message': f'Role deve ser um dos: {", ".join(valid_roles)}'}), 400
            user.role = data['role']
        
        if 'department_id' in data:
            department_id = data['department_id']
            if department_id:
                department = Department.query.get(department_id)
                if not department:
                    return jsonify({'message': 'Departamento não encontrado'}), 400
            user.department_id = department_id
        
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
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Não permitir deletar o próprio usuário
        if user.id == current_user.id:
            return jsonify({'message': 'Não é possível deletar seu próprio usuário'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar usuário: {str(e)}'}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
@admin_required
def get_user(current_user, user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar usuário: {str(e)}'}), 500

