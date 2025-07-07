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
    """Upload de arquivo"""
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

@file_bp.route('/files/<path:filename>', methods=['GET'])
@token_required
def download_file(current_user, filename):
    """Download de arquivo"""
    try:
        # Verificar se o arquivo existe
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'message': 'Arquivo não encontrado'}), 404
        
        # Obter diretório e nome do arquivo
        directory = os.path.dirname(file_path)
        basename = os.path.basename(file_path)
        
        return send_from_directory(directory, basename, as_attachment=True)
        
    except Exception as e:
        return jsonify({'message': f'Erro ao baixar arquivo: {str(e)}'}), 500

@file_bp.route('/files/<path:filename>/info', methods=['GET'])
@token_required
def get_file_info(current_user, filename):
    """Obter informações do arquivo"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'message': 'Arquivo não encontrado'}), 404
        
        # Obter informações do arquivo
        file_stats = os.stat(file_path)
        file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        # Determinar tipo do arquivo
        file_type = 'unknown'
        for ftype, extensions in ALLOWED_EXTENSIONS.items():
            if file_extension in extensions:
                file_type = ftype
                break
        
        return jsonify({
            'filename': filename,
            'file_type': file_type,
            'file_size': file_stats.st_size,
            'created_at': file_stats.st_ctime,
            'modified_at': file_stats.st_mtime
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao obter informações: {str(e)}'}), 500

@file_bp.route('/files', methods=['GET'])
@token_required
def list_files(current_user):
    """Listar arquivos do usuário"""
    try:
        files = []
        
        # Percorrer todos os tipos de arquivo
        for file_type in ALLOWED_EXTENSIONS.keys():
            type_folder = os.path.join(UPLOAD_FOLDER, file_type)
            if os.path.exists(type_folder):
                for filename in os.listdir(type_folder):
                    file_path = os.path.join(type_folder, filename)
                    if os.path.isfile(file_path):
                        file_stats = os.stat(file_path)
                        files.append({
                            'filename': filename,
                            'relative_path': os.path.join(file_type, filename),
                            'file_type': file_type,
                            'file_size': file_stats.st_size,
                            'created_at': file_stats.st_ctime,
                            'modified_at': file_stats.st_mtime
                        })
        
        # Ordenar por data de criação (mais recente primeiro)
        files.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'files': files,
            'total': len(files)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao listar arquivos: {str(e)}'}), 500

@file_bp.route('/files/<path:filename>', methods=['DELETE'])
@token_required
def delete_file(current_user, filename):
    """Deletar arquivo"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'message': 'Arquivo não encontrado'}), 404
        
        # Deletar arquivo
        os.remove(file_path)
        
        return jsonify({'message': 'Arquivo deletado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao deletar arquivo: {str(e)}'}), 500

