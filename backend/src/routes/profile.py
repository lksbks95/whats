from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.routes.auth import token_required

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile/me', methods=['PUT'])
@token_required
def update_my_profile(current_user):
    """
    Permite que o utilizador atualmente logado atualize o seu próprio perfil.
    """
    try:
        data = request.get_json()
        
        # Atualiza o nome se for fornecido
        if 'name' in data:
            current_user.name = data['name']
            
        # Atualiza a senha se for fornecida e válida
        if 'new_password' in data and data['new_password']:
            if 'current_password' not in data or not data['current_password']:
                return jsonify({'message': 'Senha atual é obrigatória para alterar a senha'}), 400
            
            # Verifica se a senha atual está correta
            if not current_user.check_password(data['current_password']):
                return jsonify({'message': 'Senha atual incorreta'}), 400
                
            # Define a nova senha
            current_user.set_password(data['new_password'])

        db.session.commit()
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"ERRO ao atualizar perfil: {str(e)}")
        return jsonify({'message': f'Erro interno ao atualizar perfil: {str(e)}'}), 500
