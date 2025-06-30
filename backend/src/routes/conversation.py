from flask import Blueprint, request, jsonify
from flask_cors import CORS
from src.models import db, Conversation, Message, Transfer, Department, User
from src.routes.auth import token_required

conversation_bp = Blueprint('conversation', __name__)
CORS(conversation_bp)

# ... (o resto do seu ficheiro de rotas de conversa continua aqui, sem alterações) ...
