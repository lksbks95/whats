from .user import db
from datetime import datetime

class Contact(db.Model):
    """Modelo para a agenda de contatos."""
    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=True)
    # ID do agente que criou o contato, para referência
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamento para obter o nome do criador
    creator = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone_number': self.phone_number,
            'email': self.email,
            'created_by': self.creator.name if self.creator else None,
            'created_at': self.created_at.isoformat() + 'Z'
        }
