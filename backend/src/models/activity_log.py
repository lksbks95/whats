from .user import db
from datetime import datetime

class ActivityLog(db.Model):
    """Modelo para registar atividades importantes no sistema."""
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    # O tipo de evento (ex: 'USER_CREATED', 'CONVERSATION_TRANSFERRED')
    event_type = db.Column(db.String(50), nullable=False)
    # O ID do utilizador que realizou a ação
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    # Uma descrição legível da ação
    message = db.Column(db.String(255), nullable=False)
    # A data e hora em que a ação ocorreu
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relação para obter o nome do utilizador facilmente
    user = db.relationship('User', backref='activities')

    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'Sistema',
            'message': self.message,
            'timestamp': self.timestamp.isoformat() + 'Z' # Formato ISO 8601
        }
