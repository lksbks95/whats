from flask import Blueprint, request, jsonify
from flask_cors import CORS # <--- A importação que faltava foi adicionada aqui
from src.models import db, Conversation, Message, Transfer, Department, User
from src.routes.auth import token_required

conversation_bp = Blueprint('conversation', __name__)
CORS(conversation_bp) # Esta linha agora irá funcionar

@conversation_bp.route('/conversations', methods=['GET'])
@token_required
def get_conversations(current_user):
    """Retorna uma lista de conversas baseada na função do utilizador."""
    try:
        # Agentes só veem conversas atribuídas a eles ou ao seu departamento
        if current_user.role == 'agent':
            conversations = Conversation.query.filter(
                (Conversation.assigned_agent_id == current_user.id) |
                (Conversation.department_id == current_user.department_id)
            ).order_by(Conversation.updated_at.desc()).all()
        # Admins e Gerentes veem todas as conversas
        else:
            conversations = Conversation.query.order_by(Conversation.updated_at.desc()).all()
            
        return jsonify({'conversations': [c.to_dict() for c in conversations]}), 200
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar conversas: {str(e)}'}), 500

@conversation_bp.route('/conversations/<int:conv_id>', methods=['GET'])
@token_required
def get_conversation_details(current_user, conv_id):
    """Retorna os detalhes e mensagens de uma conversa específica."""
    try:
        conversation = Conversation.query.get(conv_id)
        if not conversation:
            return jsonify({'message': 'Conversa não encontrada'}), 404
        
        # Verificação simples de autorização
        if current_user.role == 'agent' and conversation.assigned_agent_id != current_user.id and conversation.department_id != current_user.department_id:
             return jsonify({'message': 'Acesso não autorizado a esta conversa'}), 403

        # O SQLAlchemy irá carregar as mensagens automaticamente através do 'backref'
        messages = sorted(conversation.messages, key=lambda m: m.timestamp)

        return jsonify({
            'conversation': conversation.to_dict(),
            'messages': [msg.to_dict() for msg in messages]
        }), 200
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar detalhes da conversa: {str(e)}'}), 500

@conversation_bp.route('/conversations/<int:conv_id>/transfer', methods=['POST'])
@token_required
def transfer_conversation(current_user, conv_id):
    """Transfere uma conversa para outro departamento ou agente."""
    data = request.get_json()
    to_department_id = data.get('to_department_id')
    to_agent_id = data.get('to_agent_id') # Opcional

    if not to_department_id:
        return jsonify({'message': 'Departamento de destino é obrigatório'}), 400

    try:
        conversation = Conversation.query.get(conv_id)
        if not conversation:
            return jsonify({'message': 'Conversa não encontrada'}), 404

        # Atualiza a atribuição da conversa
        conversation.department_id = to_department_id
        conversation.assigned_agent_id = to_agent_id if to_agent_id else None

        # Regista a transferência no log
        new_transfer = Transfer(
            conversation_id=conv_id,
            from_agent_id=current_user.id,
            to_department_id=to_department_id,
            to_agent_id=to_agent_id,
            reason=data.get('reason')
        )
        db.session.add(new_transfer)
        db.session.commit()

        return jsonify({'message': 'Conversa transferida com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao transferir conversa: {str(e)}'}), 500
