from datetime import datetime
from io import BytesIO
from flask import send_file
from app import db
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
from app.models import Venda, Custo, Meta, Cotacao, Upload

class RelatorioService:
    """Classe responsável por gerar relatórios analíticos e PDFs usando ORM."""

    def __init__(self):
        # Mapeamento de tipo de relatório para modelo
        self.model_map = {
            "vendas": Venda,
            "custos": Custo,
            "metas": Meta,
            "cotacoes": Cotacao,
            "uploads": Upload,
        }

        # Campos de data para cada modelo
        self.data_field_map = {
            "vendas": "data",
            "custos": "data_atualizacao",
            "metas": "created_at",
            "cotacoes": "data_hora",
            "uploads": "created_at",
        }

    def gerar_relatorio(self, filtros: dict):
        """Gera relatório com base nos filtros."""
        tipo = filtros.get("tipoRelatorio")
        data_inicio = filtros.get("dataInicio")
        data_fim = filtros.get("dataFim")
        exportar_pdf = filtros.get("exportarPDF", False)

        if tipo not in self.model_map:
            return {"erro": "Tipo de relatório inválido."}

        df = self._executar_query(tipo, data_inicio, data_fim)

        if exportar_pdf:
            return self._gerar_pdf(df, tipo, data_inicio, data_fim)

        return {"dados": df.to_dict(orient="records")}

    def _executar_query(self, tipo: str, data_inicio: str, data_fim: str) -> pd.DataFrame:
        """Executa consulta ORM e retorna DataFrame."""
        Model = self.model_map[tipo]
        data_field_name = self.data_field_map[tipo]
        data_field = getattr(Model, data_field_name)

        query = db.session.query(Model).filter(data_field.between(data_inicio, data_fim))
        resultados = query.all()

        if not resultados:
            return pd.DataFrame()

        # Converte ORM para DataFrame
        df = pd.DataFrame([r.__dict__ for r in resultados])
        if "_sa_instance_state" in df.columns:
            df = df.drop("_sa_instance_state", axis=1)
        return df

    def _gerar_pdf(self, df: pd.DataFrame, tipo: str, data_inicio: str, data_fim: str):
        """Gera PDF e retorna send_file."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        content = [
            Paragraph(f"<b>Relatório: {tipo.title()}</b>", styles["Title"]),
            Paragraph(f"Período: {data_inicio} a {data_fim}", styles["Normal"]),
            Spacer(1, 12),
        ]

        if df.empty:
            content.append(Paragraph("Nenhum dado encontrado para o período informado.", styles["Normal"]))
        else:
            tabela = [df.columns.tolist()] + df.values.tolist()
            table = Table(tabela)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007BFF")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]))
            content.append(table)

        doc.build(content)
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"relatorio_{tipo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )