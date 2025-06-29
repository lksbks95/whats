from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importa os modelos para que o SQLAlchemy os registe.
# Esta ordem ajuda a resolver dependências antes de a aplicação arrancar.
from .user import User, Department
from .conversation import Conversation
from .message import Message
from .transfer import Transfer
from .contact import Contact
from .activity_log import ActivityLog
from .whatsapp_connection import WhatsAppConnection
