from . import db
from datetime import datetime

class WhatsAppConnection(db.Model):
    """Modelo para armazenar as configurações de conexão do WhatsApp."""
    __tablename__ = 'whatsapp_connections'

    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    access_token = db.Column(db.String(255), nullable=False)
    webhook_verify_token = db.Column(db.String(100), nullable=False)
    business_account_id = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            # Não expomos tokens sensíveis na API por segurança
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() + 'Z',
            'business_account_id': self.business_account_id
        }
