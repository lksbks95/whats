from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='agent')  # admin, manager, agent
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    department = db.relationship('Department', backref='users')
    assigned_conversations = db.relationship('Conversation', backref='assigned_agent', foreign_keys='Conversation.assigned_agent_id')
    sent_messages = db.relationship('Message', backref='sender', foreign_keys='Message.sender_id')
    transfers_from = db.relationship('Transfer', backref='from_agent', foreign_keys='Transfer.from_agent_id')
    transfers_to = db.relationship('Transfer', backref='to_agent', foreign_keys='Transfer.to_agent_id')

    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    conversations = db.relationship('Conversation', backref='department')
    transfers_from = db.relationship('Transfer', backref='from_department', foreign_keys='Transfer.from_department_id')
    transfers_to = db.relationship('Transfer', backref='to_department', foreign_keys='Transfer.to_department_id')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'user_count': len(self.users),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class WhatsAppConnection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    access_token = db.Column(db.String(500), nullable=False)
    webhook_verify_token = db.Column(db.String(100), nullable=False)
    business_account_id = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'business_account_id': self.business_account_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    whatsapp_contact_id = db.Column(db.String(50), nullable=False)
    contact_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    assigned_agent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    status = db.Column(db.String(20), default='open')  # open, closed, transferred
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    messages = db.relationship('Message', backref='conversation', cascade='all, delete-orphan')
    transfers = db.relationship('Transfer', backref='conversation', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'whatsapp_contact_id': self.whatsapp_contact_id,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'assigned_agent_id': self.assigned_agent_id,
            'assigned_agent_name': self.assigned_agent.name if self.assigned_agent else None,
            'status': self.status,
            'message_count': len(self.messages),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    sender_type = db.Column(db.String(20), nullable=False)  # customer, agent, system
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # null para customer/system
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, image, document, audio, system
    file_path = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_type': self.sender_type,
            'sender_id': self.sender_id,
            'sender_name': self.sender.name if self.sender else None,
            'content': self.content,
            'message_type': self.message_type,
            'file_path': self.file_path,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    from_department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    to_department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    from_agent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    to_agent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'from_department_id': self.from_department_id,
            'from_department_name': self.from_department.name if self.from_department else None,
            'to_department_id': self.to_department_id,
            'to_department_name': self.to_department.name if self.to_department else None,
            'from_agent_id': self.from_agent_id,
            'from_agent_name': self.from_agent.name if self.from_agent else None,
            'to_agent_id': self.to_agent_id,
            'to_agent_name': self.to_agent.name if self.to_agent else None,
            'reason': self.reason,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

