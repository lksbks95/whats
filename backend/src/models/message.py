from . import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    sender_type = db.Column(db.String(20), nullable=False) 
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')
    file_path = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        sender = db.session.get(User, self.sender_id)
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_type': self.sender_type,
            'sender_id': self.sender_id,
            'sender_name': sender.name if sender else 'Cliente',
            'content': self.content,
            'message_type': self.message_type,
            'file_path': self.file_path,
            'timestamp': self.timestamp.isoformat() + 'Z'
        }
