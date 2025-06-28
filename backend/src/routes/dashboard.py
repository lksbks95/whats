from flask import Blueprint, jsonify
from src.models.user import db, User, Department
# Assumindo que você tem um modelo Conversation
from src.models.conversation import Conversation 
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
        
        # Conta apenas as conversas com status 'open'
        active_conversations = Conversation.query.filter_by(status='open').count()
        
        # A lógica para transferências pendentes pode ser mais complexa,
        # por enquanto, vamos usar um valor fixo como exemplo.
        pending_transfers = 0 # Substitua pela sua lógica real

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
