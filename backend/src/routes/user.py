# No topo do ficheiro
from src.models.user import db, User, Department
from src.models.activity_log import ActivityLog # <--- ADICIONE ESTA LINHA

# ... (resto do ficheiro) ...

# Dentro da função create_user, depois de db.session.commit()
@user_bp.route('/users', methods=['POST'])
@token_required
@admin_required
def create_user(current_user):
    # ... (toda a sua lógica de criação de utilizador) ...
    try:
        # ... (código para criar new_user) ...
        db.session.add(new_user)
        db.session.commit()

        # --- ADICIONE ESTAS LINHAS PARA REGISTAR A ATIVIDADE ---
        log_message = f"Novo utilizador '{new_user.name}' foi criado."
        new_log = ActivityLog(
            event_type='USER_CREATED',
            user_id=current_user.id,
            message=log_message
        )
        db.session.add(new_log)
        db.session.commit()
        # --- FIM DO BLOCO DE LOGGING ---

        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': new_user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao criar usuário: {str(e)}'}), 500

# ... (resto do ficheiro) ...
