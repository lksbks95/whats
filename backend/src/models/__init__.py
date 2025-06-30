from flask_sqlalchemy import SQLAlchemy

# Inicializa a instância da base de dados.
# Este objeto 'db' será importado por todos os outros modelos.
db = SQLAlchemy()

# Importa todos os modelos aqui para garantir que eles sejam registados
# com o SQLAlchemy antes que a aplicação tente usá-los.
# A ordem aqui não importa, pois o Python irá resolver as dependências.
from .user import User, Department
from .conversation import Conversation
from .contact import Contact
from .activity_log import ActivityLog
from .whatsapp_connection import WhatsAppConnection
