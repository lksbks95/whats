# backend/src/routes/conversation.py

from flask import Blueprint, request, jsonify
from src.models import db, Conversation, Message, User, Contact
from src.routes.auth import token_required
import os
import requests # Importe a biblioteca de requisições

conversation_bp = Blueprint('conversation', __name__)

# Rota para listar conversas (já estava correta)
@conversation_bp.route('/conversations', methods=['GET'])
@token_required
def get_conversations(current_user):
    # ... (seu código existente para listar conversas) ...

# Rota para buscar detalhes de uma conversa (já estava correta)
@conversation_bp.route('/conversations/<int:conv_id>', methods=['GET'])
@token_required
def get_conversation_details(current_user, conv_id):
    # ... (seu código existente para buscar detalhes) ...

# --- ROTA MODIFICADA/ADICIONADA PARA ENVIAR MENSAGENS ---
@conversation_bp.route('/conversations/<int:conv_id>/messages', methods=['POST'])
@token_required
def add_message_to_conversation(current_user, conv_id):
    data = request.get_json()
    content = data.get('content')
    message_type = data.get('message_type', 'text')
    file_path = data.get('file_path')

    if not content:
        return jsonify({'message': 'O conteúdo da mensagem é obrigatório'}), 400

    try:
        # 1. Salva a mensagem do agente no banco de dados primeiro
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

        # 2. Pega o telefone do contato para enviar a mensagem
        conversation = Conversation.query.get(conv_id)
        if not conversation or not conversation.contact:
            raise Exception("Conversa ou contato não encontrado")
        
        contact_phone = conversation.contact.phone_number

        # 3. Manda a mensagem de texto para o Gateway Node.js
        if message_type == 'text':
            gateway_url = "http://localhost:3001/send-message"
            payload = {"to": contact_phone, "text": content}
            
            # Envia a requisição para o Gateway
            response = requests.post(gateway_url, json=payload)
            response.raise_for_status() # Lança um erro se a resposta não for 2xx

        # (Aqui você pode adicionar a lógica para enviar arquivos também, se necessário)

        return jsonify({'message': 'Mensagem enviada com sucesso', 'data': new_message.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        print(f"ERRO ao enviar mensagem: {e}")
        return jsonify({'message': f'Erro ao enviar mensagem: {str(e)}'}), 500

# ... (sua rota de transferência pode continuar aqui) ...
