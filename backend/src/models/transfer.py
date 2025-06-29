from . import db
from datetime import datetime

class Transfer(db.Model):
    """Modelo para registar a transferência de uma conversa."""
    __tablename__ = 'transfers'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    
    # IDs para rastrear a transferência
    from_agent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    to_agent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    to_department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    
    reason = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos para obter os nomes facilmente
    conversation = db.relationship('Conversation', backref='transfers')
    from_agent = db.relationship('User', foreign_keys=[from_agent_id])
    to_agent = db.relationship('User', foreign_keys=[to_agent_id])
    to_department = db.relationship('Department')

    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'from_agent_name': self.from_agent.name if self.from_agent else 'Sistema',
            'to_agent_name': self.to_agent.name if self.to_agent else 'Qualquer Agente',
            'to_department_name': self.to_department.name,
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat() + 'Z'
        }
