from flask import Blueprint, jsonify
from src.models.user import db, User, Department
# A linha abaixo foi comentada para evitar o erro de importação, pois o modelo ainda não existe.
# from src.models.conversation import Conversation 
from src.routes.auth import token_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
@token_required
def get_dashboard_stats(current_user):
    """
    Calcula e retorna as estatísticas principais para o dashboard.
    """
    try:
        total_users = User.query.count()
        total_departments = Department.query.count()
        
        # --- CORREÇÃO AQUI ---
        # Temporariamente, usamos um valor fixo (0) para as conversas ativas
        # para evitar o erro, até que o modelo 'Conversation' seja totalmente implementado.
        active_conversations = 0 
        
        # A lógica para transferências pendentes também usará um valor fixo por agora.
        pending_transfers = 0

        stats = {
            'totalUsers': total_users,
            'totalDepartments': total_departments,
            'activeConversations': active_conversations,
            'pendingTransfers': pending_transfers
        }

        return jsonify({'stats': stats}), 200
    except Exception as e:
        print(f"ERRO ao buscar estatísticas do dashboard: {str(e)}")
        return jsonify({'message': f'Erro interno ao buscar estatísticas: {str(e)}'}), 500
