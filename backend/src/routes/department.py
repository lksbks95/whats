from flask import Blueprint, request, jsonify
from flask_cors import CORS
# Certifique-se de que User está importado se a sua relação 'department.users' precisar dele
from src.models.user import db, Department, User 
from src.routes.auth import token_required, admin_required

department_bp = Blueprint('department', __name__)
CORS(department_bp)

# --- FUNÇÃO GET ATUALIZADA ---
# Esta é a versão segura que substitui a sua original.
@department_bp.route('/departments', methods=['GET'])
@token_required
def get_departments(current_user):
    """
    Busca todos os departamentos e garante que os dados retornados são válidos.
    Esta rota é usada para popular os menus de seleção no frontend.
    """
    try:
        departments_query = Department.query.all()
        
        departments_list = []
        for dept in departments_query:
            # Garante que o departamento tem um método to_dict e um id válido
            if hasattr(dept, 'to_dict') and dept.id is not None:
                dept_data = dept.to_dict()
                # Adiciona a contagem de usuários se o método existir no modelo
                if hasattr(dept, 'users'):
                    dept_data['user_count'] = len(dept.users)
                else:
                    dept_data['user_count'] = 0
                departments_list.append(dept_data)

        return jsonify({'departments': departments_list}), 200
    except Exception as e:
        # Log do erro no servidor para depuração
        print(f"ERRO ao buscar departamentos: {str(e)}")
        return jsonify({'message': f'Erro interno ao buscar departamentos: {str(e)}'}), 500

# --- O RESTO DO SEU FICHEIRO (sem alterações) ---

@department_bp.route('/departments', methods=['POST'])
@token_required
@admin_required
def create_department(current_user):
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'message': 'Nome do departamento é obrigatório'}), 400
        
        if Department.query.filter_by(name=data['name']).first():
            return jsonify({'message': 'Nome do departamento já existe'}), 400
        
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
        
        if 'name' in data:
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
        
        if department.users:
            return jsonify({
                'message': 'Não é possível deletar departamento com usuários associados. Remova os usuários primeiro.'
            }), 400
        
        if hasattr(department, 'conversations') and department.conversations:
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
