from flask_sqlalchemy import SQLAlchemy

# Inicializa a instância da base de dados.
db = SQLAlchemy()

# Importa todos os modelos aqui para garantir que eles sejam registados.
from .user import User, Department
from .conversation import Conversation
from .contact import Contact
from .activity_log import ActivityLog
from .whatsapp_connection import WhatsAppConnection
from .message import Message # <--- ADICIONE ESTA LINHA
