from flask import Blueprint, request, jsonify, send_from_directory
from flask_cors import CORS
from src.routes.auth import token_required
import os
import uuid
from werkzeug.utils import secure_filename

file_bp = Blueprint('file', __name__)
CORS(file_bp)

# Configurações de upload
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'document': {'pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx'},
    'audio': {'mp3', 'wav', 'ogg', 'm4a'}
}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Criar diretório de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verificar se o arquivo é permitido"""
    if '.' not in filename:
        return False, None
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return True, file_type
    
    return False, None

def get_file_size(file):
    """Obter tamanho do arquivo"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size

@file_bp.route('/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    """Upload de um ÚNICO arquivo (rota mantida por compatibilidade)"""
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'Nenhum arquivo selecionado'}), 400
        
        # Verificar tamanho do arquivo
        file_size = get_file_size(file)
        if file_size > MAX_FILE_SIZE:
            return jsonify({'message': f'Arquivo muito grande. Máximo: {MAX_FILE_SIZE // (1024*1024)}MB'}), 400
        
        # Verificar tipo de arquivo
        is_allowed, file_type = allowed_file(file.filename)
        if not is_allowed:
            return jsonify({'message': 'Tipo de arquivo não permitido'}), 400
        
        # Gerar nome único para o arquivo
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Criar subdiretório por tipo
        type_folder = os.path.join(UPLOAD_FOLDER, file_type)
        os.makedirs(type_folder, exist_ok=True)
        
        # Salvar arquivo
        file_path = os.path.join(type_folder, unique_filename)
        file.save(file_path)
        
        # Caminho relativo para armazenar no banco
        relative_path = os.path.join(file_type, unique_filename)
        
        return jsonify({
            'message': 'Arquivo enviado com sucesso',
            'file_path': relative_path,
            'file_type': file_type,
            'file_size': file_size,
            'original_name': secure_filename(file.filename)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao fazer upload: {str(e)}'}), 500

# --- NOVO ENDPOINT PARA MÚLTIPLOS ARQUIVOS ---
@file_bp.route('/upload_multiple', methods=['POST'])
@token_required
def upload_multiple_files(current_user):
    """Upload de múltiplos arquivos"""
    if 'files[]' not in request.files:
        return jsonify({'message': 'Nenhum arquivo enviado'}), 400

    files = request.files.getlist('files[]')
    uploaded_files_info = []
    errors = []

    for file in files:
        if file and file.filename != '':
            original_name = secure_filename(file.filename)
            is_allowed, file_type = allowed_file(original_name)
            file_size = get_file_size(file)

            if not is_allowed:
                errors.append({'filename': original_name, 'error': 'Tipo de arquivo não permitido'})
                continue

            if file_size > MAX_FILE_SIZE:
                errors.append({'filename': original_name, 'error': f'Arquivo muito grande (Máx: {MAX_FILE_SIZE // (1024*1024)}MB)'})
                continue
            
            try:
                file_extension = original_name.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                
                type_folder = os.path.join(UPLOAD_FOLDER, file_type)
                os.makedirs(type_folder, exist_ok=True)
                
                file_path = os.path.join(type_folder, unique_filename)
                file.save(file_path)
                
                relative_path = os.path.join(file_type, unique_filename)

                uploaded_files_info.append({
                    'file_path': relative_path,
                    'file_type': file_type,
                    'file_size': file_size,
                    'original_name': original_name
                })
            except Exception as e:
                errors.append({'filename': original_name, 'error': str(e)})

    if not uploaded_files_info and errors:
        return jsonify({'message': 'Falha no upload de todos os arquivos.', 'errors': errors}), 400

    return jsonify({
        'message': 'Upload concluído.',
        'uploaded_files': uploaded_files_info,
        'errors': errors
    }), 200


# (O resto do seu arquivo file.py com as rotas de download, info, list, delete permanece o mesmo)
# ...
