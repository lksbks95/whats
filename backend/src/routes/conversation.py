# backend/src/routes/conversation.py

from flask import Blueprint, request, jsonify
from src.models import db, Conversation, Message, User, Contact, Transfer, Department
from src.routes.auth import token_required
import os
import requests

conversation_bp = Blueprint('conversation', __name__)

@conversation_bp.route('/conversations', methods=['GET'])
@token_required
def get_conversations(current_user):
    """Retorna uma lista de conversas baseada na função do utilizador."""
    try:
        # Admins e Gerentes veem todas as conversas não fechadas
        if current_user.role in ['admin', 'manager']:
            conversations = Conversation.query.filter(Conversation.status != 'closed').order_by(Conversation.updated_at.desc()).all()
        # Agentes só veem conversas atribuídas a eles ou ao seu departamento
        else:
            conversations = Conversation.query.filter(
                Conversation.status != 'closed',
                (Conversation.assigned_agent_id == current_user.id) |
                (Conversation.department_id == current_user.department_id)
            ).order_by(Conversation.updated_at.desc()).all()
            
        return jsonify({'conversations': [c.to_dict() for c in conversations]}), 200
    except Exception as e:
        print(f"Erro ao buscar conversas: {e}")
        return jsonify({'message': f'Erro ao buscar conversas: {str(e)}'}), 500

@conversation_bp.route('/conversations/<int:conv_id>', methods=['GET'])
@token_required
def get_conversation_details(current_user, conv_id):
    """Retorna os detalhes e mensagens de uma conversa específica."""
    try:
        conversation = Conversation.query.get(conv_id)
        if not conversation:
            return jsonify({'message': 'Conversa não encontrada'}), 404
        
        # Verificação de autorização
        if current_user.role == 'agent' and conversation.assigned_agent_id != current_user.id and conversation.department_id != current_user.department_id:
             return jsonify({'message': 'Acesso não autorizado'}), 403

        messages = sorted(conversation.messages, key=lambda m: m.timestamp)

        return jsonify({
            'conversation': conversation.to_dict(),
            'messages': [msg.to_dict() for msg in messages]
        }), 200
    except Exception as e:
        print(f"Erro ao buscar detalhes da conversa: {e}")
        return jsonify({'message': f'Erro ao buscar detalhes da conversa: {str(e)}'}), 500

@conversation_bp.route('/conversations/<int:conv_id>/messages', methods=['POST'])
@token_required
def add_message_to_conversation(current_user, conv_id):
    """Adiciona uma mensagem a uma conversa e a envia via gateway."""
    data = request.get_json()
    content = data.get('content')
    message_type = data.get('message_type', 'text')
    file_path = data.get('file_path')

    if not content:
        return jsonify({'message': 'O conteúdo da mensagem é obrigatório'}), 400

    try:
        # 1. Salva a mensagem do agente no banco de dados
        new_message = Message(
            conversation_id=conv_id,
            sender_id=current_user.id,
            sender_type='agent',
            content=content,
            message_type=message_type,
            file_path=file_path
        )
        db.session.add(new_message)
        db.session.commit()

        # 2. Envia a mensagem de texto para o Gateway Node.js
        if message_type == 'text':
            conversation = Conversation.query.get(conv_id)
            if not conversation or not conversation.contact:
                raise Exception("Conversa ou contato não encontrado para envio")
            
            contact_phone = conversation.contact.phone_number
            gateway_url = "http://localhost:3001/send-message"
            payload = {"to": contact_phone, "text": content}
            
            response = requests.post(gateway_url, json=payload)
            response.raise_for_status()

        return jsonify({'message': 'Mensagem enviada com sucesso', 'data': new_message.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        print(f"ERRO ao enviar mensagem: {e}")
        return jsonify({'message': f'Erro ao enviar mensagem: {str(e)}'}), 500

# ... (suas outras rotas, como a de transferência, continuam aqui)
