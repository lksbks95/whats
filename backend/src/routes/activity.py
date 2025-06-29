from flask import Blueprint, jsonify
from src.models.activity_log import ActivityLog
from src.routes.auth import token_required

activity_bp = Blueprint('activity', __name__)

@activity_bp.route('/activity/recent', methods=['GET'])
@token_required
def get_recent_activity(current_user):
    """
    Busca as 5 atividades mais recentes do sistema.
    """
    try:
        # Busca os 5 logs mais recentes, ordenados por data e hora
        recent_logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(5).all()
        
        return jsonify({
            'activities': [log.to_dict() for log in recent_logs]
        }), 200
    except Exception as e:
        print(f"ERRO ao buscar atividade recente: {str(e)}")
        return jsonify({'message': f'Erro interno ao buscar atividades: {str(e)}'}), 500
