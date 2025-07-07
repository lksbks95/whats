from flask import Blueprint, request, jsonify
from flask_cors import CORS
from src.models.user import db, WhatsAppConnection
from src.routes.auth import token_required, admin_required
import requests
import os

whatsapp_bp = Blueprint('whatsapp', __name__)
CORS(whatsapp_bp)

@whatsapp_bp.route('/whatsapp/connect', methods=['POST'])
@token_required
@admin_required
def connect_whatsapp(current_user):
    """Conectar número do WhatsApp Business"""
    try:
        data = request.get_json()
        
        # Validação dos campos obrigatórios
        required_fields = ['phone_number', 'access_token', 'webhook_verify_token', 'business_account_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se o número já está conectado
        existing_connection = WhatsAppConnection.query.filter_by(
            phone_number=data['phone_number']
        ).first()
        
        if existing_connection:
            return jsonify({'message': 'Este número já está conectado'}), 400
        
        # Validar token com a API do WhatsApp (simulado)
        is_valid = validate_whatsapp_token(data['access_token'], data['business_account_id'])
        if not is_valid:
            return jsonify({'message': 'Token de acesso inválido'}), 400
        
        # Criar nova conexão
        new_connection = WhatsAppConnection(
            phone_number=data['phone_number'],
            access_token=data['access_token'],
            webhook_verify_token=data['webhook_verify_token'],
            business_account_id=data['business_account_id'],
            is_active=True
        )
        
        db.session.add(new_connection)
        db.session.commit()
        
        return jsonify({
            'message': 'WhatsApp conectado com sucesso',
            'connection': new_connection.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao conectar WhatsApp: {str(e)}'}), 500

@whatsapp_bp.route('/whatsapp/status', methods=['GET'])
@token_required
def get_whatsapp_status(current_user):
    """Obter status da conexão WhatsApp"""
    try:
        connections = WhatsAppConnection.query.filter_by(is_active=True).all()
        
        return jsonify({
            'connections': [conn.to_dict() for conn in connections],
            'total_connections': len(connections),
            'is_connected': len(connections) > 0
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar status: {str(e)}'}), 500

@whatsapp_bp.route('/whatsapp/disconnect/<int:connection_id>', methods=['DELETE'])
@token_required
@admin_required
def disconnect_whatsapp(current_user, connection_id):
    """Desconectar número do WhatsApp"""
    try:
        connection = WhatsAppConnection.query.get(connection_id)
        if not connection:
            return jsonify({'message': 'Conexão não encontrada'}), 404
        
        connection.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'WhatsApp desconectado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao desconectar WhatsApp: {str(e)}'}), 500

@whatsapp_bp.route('/webhook', methods=['GET'])
def webhook_verify():
    """Verificar webhook do WhatsApp"""
    try:
        # Verificação do webhook
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        # Buscar token de verificação no banco
        connection = WhatsAppConnection.query.filter_by(
            webhook_verify_token=verify_token,
            is_active=True
        ).first()
        
        if connection and challenge:
            return challenge
        else:
            return 'Token de verificação inválido', 403
            
    except Exception as e:
        return f'Erro na verificação: {str(e)}', 500

@whatsapp_bp.route('/webhook', methods=['POST'])
def webhook_receive():
    """Receber mensagens do WhatsApp"""
    try:
        data = request.get_json()
        
        # Processar mensagens recebidas
        if data and 'entry' in data:
            for entry in data['entry']:
                if 'changes' in entry:
                    for change in entry['changes']:
                        if change.get('field') == 'messages':
                            process_whatsapp_message(change['value'])
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        print(f'Erro no webhook: {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 500

def validate_whatsapp_token(access_token, business_account_id):
    """Validar token do WhatsApp Business API (simulado)"""
    try:
        # Em produção, fazer uma chamada real para a API do WhatsApp
        # Por enquanto, simulamos uma validação básica
        if len(access_token) > 20 and len(business_account_id) > 5:
            return True
        return False
    except:
        return False

def process_whatsapp_message(message_data):
    """Processar mensagem recebida do WhatsApp"""
    try:
        from src.models.user import Conversation, Message, Department
        
        if 'messages' in message_data:
            for message in message_data['messages']:
                # Extrair dados da mensagem
                contact_id = message['from']
                message_text = message.get('text', {}).get('body', '')
                message_type = message.get('type', 'text')
                
                # Buscar ou criar conversa
                conversation = Conversation.query.filter_by(
                    whatsapp_contact_id=contact_id
                ).first()
                
                if not conversation:
                    # Criar nova conversa no departamento padrão (Suporte)
                    default_dept = Department.query.filter_by(name='Suporte').first()
                    if default_dept:
                        conversation = Conversation(
                            whatsapp_contact_id=contact_id,
                            contact_name=f'Cliente {contact_id[-4:]}',
                            contact_phone=contact_id,
                            department_id=default_dept.id,
                            status='open'
                        )
                        db.session.add(conversation)
                        db.session.flush()  # Para obter o ID
                
                # Criar mensagem
                if conversation:
                    new_message = Message(
                        conversation_id=conversation.id,
                        sender_type='customer',
                        content=message_text,
                        message_type=message_type
                    )
                    db.session.add(new_message)
                    db.session.commit()
                    
                    # Aqui você pode adicionar lógica para notificar agentes via Socket.IO
                    print(f'Nova mensagem recebida: {message_text}')
                    
    except Exception as e:
        print(f'Erro ao processar mensagem: {str(e)}')
        db.session.rollback()

@whatsapp_bp.route('/whatsapp/send-message', methods=['POST'])
@token_required
def send_whatsapp_message(current_user):
    """Enviar mensagem via WhatsApp"""
    try:
        data = request.get_json()
        
        required_fields = ['to', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Campo {field} é obrigatório'}), 400
        
        # Buscar conexão ativa
        connection = WhatsAppConnection.query.filter_by(is_active=True).first()
        if not connection:
            return jsonify({'message': 'Nenhuma conexão WhatsApp ativa'}), 400
        
        # Enviar mensagem (simulado)
        success = send_message_to_whatsapp(
            connection.access_token,
            data['to'],
            data['message']
        )
        
        if success:
            # Salvar mensagem no banco
            from src.models.user import Conversation, Message
            
            conversation = Conversation.query.filter_by(
                whatsapp_contact_id=data['to']
            ).first()
            
            if conversation:
                new_message = Message(
                    conversation_id=conversation.id,
                    sender_type='agent',
                    sender_id=current_user.id,
                    content=data['message'],
                    message_type='text'
                )
                db.session.add(new_message)
                db.session.commit()
            
            return jsonify({'message': 'Mensagem enviada com sucesso'}), 200
        else:
            return jsonify({'message': 'Erro ao enviar mensagem'}), 500
            
    except Exception as e:
        return jsonify({'message': f'Erro ao enviar mensagem: {str(e)}'}), 500

def send_message_to_whatsapp(access_token, to, message):
    """Enviar mensagem para WhatsApp Business API (simulado)"""
    try:
        # Em produção, fazer chamada real para a API
        # Por enquanto, simulamos o envio
        print(f'Enviando mensagem para {to}: {message}')
        return True
    except:
        return False

