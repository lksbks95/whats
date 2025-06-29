from . import db
from datetime import datetime

class Message(db.Model):
    """Modelo para cada mensagem dentro de uma conversa."""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    
    # Define quem enviou a mensagem: 'agent', 'customer', ou 'system'
    sender_type = db.Column(db.String(20), nullable=False) 
    
    # ID do agente que enviou (se aplicável)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 
    
    content = db.Column(db.Text, nullable=False)
    # Define o tipo de mensagem: 'text', 'image', 'audio', 'file'
    message_type = db.Column(db.String(20), default='text')
    file_path = db.Column(db.String(255), nullable=True) # Caminho para ficheiros anexados
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    conversation = db.relationship('Conversation', backref=db.backref('messages', lazy=True, cascade="all, delete-orphan"))
    sender = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_type': self.sender_type,
            'sender_id': self.sender_id,
            'sender_name': self.sender.name if self.sender else 'Cliente',
            'content': self.content,
            'message_type': self.message_type,
            'file_path': self.file_path,
            'timestamp': self.timestamp.isoformat() + 'Z'
        }
