from flask import Blueprint, jsonify
from src.models.user import Department
from src.routes.auth import token_required

# ***** CORREÇÃO FINAL AQUI *****
# O nome do blueprint foi alterado para ser completamente único e evitar conflitos.
department_bp = Blueprint('department_list_api', __name__)

@department_bp.route('/departments', methods=['GET'])
@token_required
def get_departments(current_user):
    """
    Busca todos os departamentos e garante que os dados retornados são válidos.
    """
    try:
        departments_query = Department.query.all()
        
        departments_list = []
        for dept in departments_query:
            # Garante que o departamento tem um método to_dict e um id válido
            if hasattr(dept, 'to_dict') and dept.id is not None:
                departments_list.append(dept.to_dict())

        return jsonify({'departments': departments_list}), 200
    except Exception as e:
        # Log do erro no servidor para depuração
        print(f"ERRO ao buscar departamentos: {str(e)}")
        return jsonify({'message': f'Erro interno ao buscar departamentos: {str(e)}'}), 500
