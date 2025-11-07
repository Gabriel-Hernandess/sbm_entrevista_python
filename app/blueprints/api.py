"""
Blueprint da API interna.
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app import db
from app.models import Upload
from app.services.data_processor import DataProcessor
from app.tasks.cotacoes_task import atualizar_cotacoes_task

api_bp = Blueprint('api', __name__)


@api_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload de arquivo CSV/Excel.
    
    Form data:
        - file: Arquivo a ser enviado
        - tipo: Tipo de dados (vendas, custos, etc.)
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Arquivo sem nome'}), 400
    
    # Salva registro do upload
    upload = Upload(
        nome_arquivo=secure_filename(file.filename),
        tipo=request.form.get('tipo', 'csv'),
        status='processing'
    )
    db.session.add(upload)
    db.session.commit()
    
    try:
        # Processa arquivo
        processor = DataProcessor()
        num_registros = processor.processar_upload(file, upload.tipo)
        
        # Atualiza status
        upload.status = 'success'
        upload.num_registros = num_registros
        db.session.commit()
        
        return jsonify({
            'message': 'Arquivo processado com sucesso',
            'upload_id': upload.id,
            'registros': num_registros
        }), 201
        
    except Exception as e:
        upload.status = 'error'
        upload.mensagem_erro = str(e)
        db.session.commit()
        
        return jsonify({'error': str(e)}), 500


@api_bp.route('/cotacoes/atualizar', methods=['POST'])
def atualizar_cotacoes():
    """Dispara a task Celery para atualizar cotações."""
    from app.tasks.cotacoes_task import atualizar_cotacoes_task  # import local
    task = atualizar_cotacoes_task.delay()
    return jsonify({
        "message": "Tarefa de atualização iniciada",
        "task_id": task.id
    }), 202


@api_bp.route('/uploads', methods=['GET'])
def listar_uploads():
    """Lista histórico de uploads."""
    uploads = Upload.query.order_by(Upload.created_at.desc()).limit(50).all()
    
    return jsonify({
        'uploads': [u.to_dict() for u in uploads]
    })

