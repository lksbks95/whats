from flask import Blueprint, request, jsonify
from flask_cors import CORS
from src.models.user import db, Department
from src.routes.auth import token_required, admin_required

department_bp = Blueprint('department', __name__)
CORS(department_bp)

@department_bp.route('/departments', methods=['GET'])
@token_required
def get_departments(current_user):
    try:
        departments = Department.query.filter_by(is_active=True).all()
        return jsonify({
            'departments': [dept.to_dict() for dept in departments]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar departamentos: {str(e)}'}), 500

@department_bp.route('/departments', methods=['POST'])
@token_required
@admin_required
def create_department(current_user):
    try:
        data = request.get_json()
        
        # Validação dos campos obrigatórios
        if not data.get('name'):
            return jsonify({'message': 'Nome do departamento é obrigatório'}), 400
        
        # Verificar se nome já existe
        if Department.query.filter_by(name=data['name']).first():
            return jsonify({'message': 'Nome do departamento já existe'}), 400
        
        # Criar novo departamento
        new_department = Department(
            name=data['name'],
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(new_department)
        db.session.commit()
        
        return jsonify({
            'message': 'Departamento criado com sucesso',
            'department': new_department.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao criar departamento: {str(e)}'}), 500

@department_bp.route('/departments/<int:dept_id>', methods=['PUT'])
@token_required
@admin_required
def update_department(current_user, dept_id):
    try:
        department = Department.query.get(dept_id)
        if not department:
            return jsonify({'message': 'Departamento não encontrado'}), 404
        
        data = request.get_json()
        
        # Atualizar campos se fornecidos
        if 'name' in data:
            # Verificar se nome já existe (exceto o próprio departamento)
            existing_dept = Department.query.filter_by(name=data['name']).first()
            if existing_dept and existing_dept.id != dept_id:
                return jsonify({'message': 'Nome do departamento já existe'}), 400
            department.name = data['name']
        
        if 'description' in data:
            department.description = data['description']
        
        if 'is_active' in data:
            department.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Departamento atualizado com sucesso',
            'department': department.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao atualizar departamento: {str(e)}'}), 500

@department_bp.route('/departments/<int:dept_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_department(current_user, dept_id):
    try:
        department = Department.query.get(dept_id)
        if not department:
            return jsonify({'message': 'Departamento não encontrado'}), 404
        
        # Verificar se há usuários associados
        if department.users:
            return jsonify({
                'message': 'Não é possível deletar departamento com usuários associados. Remova os usuários primeiro.'
            }), 400
        
        # Verificar se há conversas associadas
        if department.conversations:
            return jsonify({
                'message': 'Não é possível deletar departamento com conversas associadas.'
            }), 400
        
        db.session.delete(department)
        db.session.commit()
        
        return jsonify({'message': 'Departamento deletado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar departamento: {str(e)}'}), 500

@department_bp.route('/departments/<int:dept_id>', methods=['GET'])
@token_required
def get_department(current_user, dept_id):
    try:
        department = Department.query.get(dept_id)
        if not department:
            return jsonify({'message': 'Departamento não encontrado'}), 404
        
        return jsonify({'department': department.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar departamento: {str(e)}'}), 500

