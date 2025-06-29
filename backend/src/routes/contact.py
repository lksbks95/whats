from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.contact import Contact
from src.models.conversation import Conversation # Precisamos disto para iniciar conversas
from src.routes.auth import token_required

contact_bp = Blueprint('contact', __name__)

# Rota para obter todos os contatos
@contact_bp.route('/contacts', methods=['GET'])
@token_required
def get_contacts(current_user):
    try:
        contacts = Contact.query.order_by(Contact.name).all()
        return jsonify({'contacts': [c.to_dict() for c in contacts]}), 200
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar contatos: {str(e)}'}), 500

# Rota para criar um novo contato
@contact_bp.route('/contacts', methods=['POST'])
@token_required
def create_contact(current_user):
    data = request.get_json()
    if not data or not data.get('name') or not data.get('phone_number'):
        return jsonify({'message': 'Nome e número de telefone são obrigatórios'}), 400

    if Contact.query.filter_by(phone_number=data['phone_number']).first():
        return jsonify({'message': 'Este número de telefone já existe na agenda'}), 409

    new_contact = Contact(
        name=data['name'],
        phone_number=data['phone_number'],
        email=data.get('email'),
        created_by_user_id=current_user.id
    )
    db.session.add(new_contact)
    db.session.commit()
    return jsonify({'message': 'Contato criado com sucesso', 'contact': new_contact.to_dict()}), 201

# Rota para iniciar uma conversa a partir de um contato
@contact_bp.route('/contacts/<int:contact_id>/start_conversation', methods=['POST'])
@token_required
def start_conversation_with_contact(current_user, contact_id):
    contact = Contact.query.get(contact_id)
    if not contact:
        return jsonify({'message': 'Contato não encontrado'}), 404

    # Verifica se já existe uma conversa aberta para este contato
    existing_conversation = Conversation.query.filter_by(contact_phone=contact.phone_number, status='open').first()
    if existing_conversation:
        return jsonify({
            'message': 'Já existe uma conversa aberta com este contato.',
            'conversation_id': existing_conversation.id
        }), 409

    # Cria uma nova conversa
    new_conversation = Conversation(
        contact_name=contact.name,
        contact_phone=contact.phone_number,
        status='open',
        # Inicia a conversa atribuída ao agente que a criou
        assigned_agent_id=current_user.id 
    )
    db.session.add(new_conversation)
    db.session.commit()

    # (Lógica futura: enviar uma mensagem de template do WhatsApp para iniciar a conversa)

    return jsonify({
        'message': 'Conversa iniciada com sucesso!',
        'conversation_id': new_conversation.id
    }), 201
