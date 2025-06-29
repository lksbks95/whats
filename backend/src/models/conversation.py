from . import db
from datetime import datetime

class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    contact_name = db.Column(db.String(150), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='open', nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_agent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    def to_dict(self):
        # Acedemos aos relacionamentos a partir do objeto 'self'
        assigned_agent = db.session.get(User, self.assigned_agent_id)
        department = db.session.get(Department, self.department_id)
        return {
            'id': self.id,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'status': self.status,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z',
            'assigned_agent_id': self.assigned_agent_id,
            'assigned_agent_name': assigned_agent.name if assigned_agent else None,
            'department_id': self.department_id,
            'department_name': department.name if department else None,
        }
