from flask import Blueprint, request, jsonify
from src.models import db, Setting

settings_bp = Blueprint('settings_bp', __name__)

@settings_bp.route('/settings', methods=['GET'])
def get_settings():
    settings = Setting.query.all()
    # Transforma a lista de configurações em um dicionário fácil de usar (ex: {'company_name': 'Minha Empresa'})
    settings_dict = {s.key: s.value for s in settings}
    return jsonify(settings_dict)

@settings_bp.route('/settings', methods=['POST'])
def update_settings():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    for key, value in data.items():
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            # Cria a configuração se ela não existir
            new_setting = Setting(key=key, value=value)
            db.session.add(new_setting)
    
    db.session.commit()
    return jsonify({"message": "Configurações atualizadas com sucesso!"})
