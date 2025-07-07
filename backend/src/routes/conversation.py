from flask import Blueprint, request, jsonify
from flask_cors import CORS
from src.models.user import db, Conversation, Message, Transfer, Department, User
from src.routes.auth import token_required
from datetime import datetime

conversation_bp = Blueprint('conversation', __name__)
CORS(conversation_bp)

@conversation_bp.route('/conversations', methods=['GET'])
@token_required
def get_conversations(current_user):
    """Listar conversas do usuário/departamento"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', 'open')
        
        # Filtrar conversas baseado no role do usuário
        query = Conversation.query
        
        if current_user.role == 'agent':
            # Agentes veem apenas suas conversas ou do seu departamento
            query = query.filter(
                (Conversation.assigned_agent_id == current_user.id) |
                (Conversation.department_id == current_user.department_id)
            )
        elif current_user.role == 'manager':
            # Gerenciadores veem conversas do seu departamento
            if current_user.department_id:
                query = query.filter(Conversation.department_id == current_user.department_id)
        # Admins veem todas as conversas
        
        if status != 'all':
            query = query.filter(Conversation.status == status)
        
        conversations = query.order_by(Conversation.updated_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'conversations': [conv.to_dict() for conv in conversations.items],
            'total': conversations.total,
            'pages': conversations.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar conversas: {str(e)}'}), 500

@conversation_bp.route('/conversations/<int:conversation_id>', methods=['GET'])
@token_required
def get_conversation(current_user, conversation_id):
    """Obter detalhes de uma conversa"""
    try:
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return jsonify({'message': 'Conversa não encontrada'}), 404
        
        # Verificar permissão
        if not can_access_conversation(current_user, conversation):
            return jsonify({'message': 'Acesso negado'}), 403
        
        # Buscar mensagens da conversa
        messages = Message.query.filter_by(
            conversation_id=conversation_id
        ).order_by(Message.timestamp.asc()).all()
        
        return jsonify({
            'conversation': conversation.to_dict(),
            'messages': [msg.to_dict() for msg in messages]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar conversa: {str(e)}'}), 500

@conversation_bp.route('/conversations/<int:conversation_id>/messages', methods=['POST'])
@token_required
def send_message(current_user, conversation_id):
    """Enviar mensagem em uma conversa"""
    try:
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return jsonify({'message': 'Conversa não encontrada'}), 404
        
        # Verificar permissão
        if not can_access_conversation(current_user, conversation):
            return jsonify({'message': 'Acesso negado'}), 403
        
        data = request.get_json()
        if not data.get('content'):
            return jsonify({'message': 'Conteúdo da mensagem é obrigatório'}), 400
        
        # Criar mensagem
        new_message = Message(
            conversation_id=conversation_id,
            sender_type='agent',
            sender_id=current_user.id,
            content=data['content'],
            message_type=data.get('message_type', 'text'),
            file_path=data.get('file_path')
        )
        
        db.session.add(new_message)
        
        # Atualizar conversa
        conversation.updated_at = datetime.utcnow()
        if not conversation.assigned_agent_id:
            conversation.assigned_agent_id = current_user.id
        
        db.session.commit()
        
        # Aqui você pode adicionar lógica para enviar via WhatsApp
        # send_whatsapp_message(conversation.contact_phone, data['content'])
        
        return jsonify({
            'message': 'Mensagem enviada com sucesso',
            'data': new_message.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao enviar mensagem: {str(e)}'}), 500

@conversation_bp.route('/conversations/<int:conversation_id>/transfer', methods=['POST'])
@token_required
def transfer_conversation(current_user, conversation_id):
    """Transferir conversa para outro departamento/agente"""
    try:
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return jsonify({'message': 'Conversa não encontrada'}), 404
        
        # Verificar permissão
        if not can_access_conversation(current_user, conversation):
            return jsonify({'message': 'Acesso negado'}), 403
        
        data = request.get_json()
        to_department_id = data.get('to_department_id')
        to_agent_id = data.get('to_agent_id')
        reason = data.get('reason', '')
        
        if not to_department_id:
            return jsonify({'message': 'Departamento de destino é obrigatório'}), 400
        
        # Verificar se o departamento existe
        to_department = Department.query.get(to_department_id)
        if not to_department:
            return jsonify({'message': 'Departamento de destino não encontrado'}), 404
        
        # Verificar agente se especificado
        to_agent = None
        if to_agent_id:
            to_agent = User.query.get(to_agent_id)
            if not to_agent or to_agent.department_id != to_department_id:
                return jsonify({'message': 'Agente inválido para o departamento especificado'}), 400
        
        # Criar registro de transferência
        transfer = Transfer(
            conversation_id=conversation_id,
            from_department_id=conversation.department_id,
            to_department_id=to_department_id,
            from_agent_id=current_user.id,
            to_agent_id=to_agent_id,
            reason=reason,
            status='accepted'  # Por simplicidade, aceitar automaticamente
        )
        
        db.session.add(transfer)
        
        # Atualizar conversa
        conversation.department_id = to_department_id
        conversation.assigned_agent_id = to_agent_id
        conversation.status = 'transferred'
        conversation.updated_at = datetime.utcnow()
        
        # Adicionar mensagem de sistema sobre a transferência
        system_message = Message(
            conversation_id=conversation_id,
            sender_type='system',
            content=f'Conversa transferida de {conversation.department.name} para {to_department.name}. Motivo: {reason}',
            message_type='system'
        )
        
        db.session.add(system_message)
        db.session.commit()
        
        # Aqui você pode adicionar notificação via Socket.IO
        # notify_transfer(conversation_id, to_department_id, to_agent_id)
        
        return jsonify({
            'message': 'Conversa transferida com sucesso',
            'transfer': transfer.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao transferir conversa: {str(e)}'}), 500

@conversation_bp.route('/conversations/<int:conversation_id>/close', methods=['POST'])
@token_required
def close_conversation(current_user, conversation_id):
    """Fechar uma conversa"""
    try:
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return jsonify({'message': 'Conversa não encontrada'}), 404
        
        # Verificar permissão
        if not can_access_conversation(current_user, conversation):
            return jsonify({'message': 'Acesso negado'}), 403
        
        conversation.status = 'closed'
        conversation.updated_at = datetime.utcnow()
        
        # Adicionar mensagem de sistema
        system_message = Message(
            conversation_id=conversation_id,
            sender_type='system',
            content=f'Conversa fechada por {current_user.name}',
            message_type='system'
        )
        
        db.session.add(system_message)
        db.session.commit()
        
        return jsonify({'message': 'Conversa fechada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao fechar conversa: {str(e)}'}), 500

@conversation_bp.route('/conversations/<int:conversation_id>/reopen', methods=['POST'])
@token_required
def reopen_conversation(current_user, conversation_id):
    """Reabrir uma conversa"""
    try:
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return jsonify({'message': 'Conversa não encontrada'}), 404
        
        # Verificar permissão
        if not can_access_conversation(current_user, conversation):
            return jsonify({'message': 'Acesso negado'}), 403
        
        conversation.status = 'open'
        conversation.updated_at = datetime.utcnow()
        
        # Adicionar mensagem de sistema
        system_message = Message(
            conversation_id=conversation_id,
            sender_type='system',
            content=f'Conversa reaberta por {current_user.name}',
            message_type='system'
        )
        
        db.session.add(system_message)
        db.session.commit()
        
        return jsonify({'message': 'Conversa reaberta com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao reabrir conversa: {str(e)}'}), 500

def can_access_conversation(user, conversation):
    """Verificar se o usuário pode acessar a conversa"""
    if user.role == 'admin':
        return True
    elif user.role == 'manager':
        return user.department_id == conversation.department_id
    elif user.role == 'agent':
        return (user.id == conversation.assigned_agent_id or 
                user.department_id == conversation.department_id)
    return False

