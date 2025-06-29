from . import db # Alterado de 'from .user import db'
from datetime import datetime

class Conversation(db.Model):
    """Modelo para representar uma conversa de atendimento."""
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)
    contact_name = db.Column(db.String(150), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='open', nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    assigned_agent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    assigned_agent = db.relationship('User', backref='assigned_conversations')
    department = db.relationship('Department', backref='conversations')

    def to_dict(self):
        return {
            'id': self.id,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'status': self.status,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z',
            'assigned_agent_id': self.assigned_agent_id,
            'assigned_agent_name': self.assigned_agent.name if self.assigned_agent else None,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
        }
