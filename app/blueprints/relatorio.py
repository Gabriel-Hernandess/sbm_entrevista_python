"""
Blueprint da pagina de relatorios.
"""
from flask import Blueprint, request, jsonify, render_template, send_file
from app.services.data_relatorios import RelatorioService

relatorio_bp = Blueprint('relatorio', __name__, url_prefix='/relatorios')

@relatorio_bp.route('/', methods=['GET'])
def index():
    return render_template('dashboard/relatorios.html')

@relatorio_bp.route("/gerar", methods=["POST"])
def gerar_relatorio():
    """Geração de relatório."""
    filtros = request.get_json()

    service = RelatorioService()
    resultado = service.gerar_relatorio(filtros)

    if hasattr(resultado, "direct_passthrough"):
        return resultado

    return jsonify(resultado)
