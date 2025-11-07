"""
Serviço de análises e agregações.
"""
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import random
from sqlalchemy import func, extract
from app import db
from app.models import Venda, Custo, Meta, Cotacao


class Analytics:
    """Realiza análises estatísticas e agregações."""
    
    def calcular_kpis(self, data_inicio=None, data_fim=None):
        """
        Calcula KPIs principais.
        
        Args:
            data_inicio: Data inicial (string YYYY-MM-DD)
            data_fim: Data final (string YYYY-MM-DD)
            
        Returns:
            dict: KPIs calculados
        """
        query = db.session.query(
            func.sum(Venda.valor_total).label('receita_total'),
            func.count(Venda.id).label('num_vendas'),
            func.avg(Venda.valor_total).label('ticket_medio')
        )
        
        query = self._aplicar_filtro_data(query, Venda, data_inicio, data_fim)
        resultado = query.first()
        
        return {
            'receita_total': float(resultado.receita_total or 0),
            'num_vendas': int(resultado.num_vendas or 0),
            'ticket_medio': float(resultado.ticket_medio or 0)
        }
    
    def vendas_ao_longo_tempo(self, data_inicio=None, data_fim=None):
        """
        Retorna série temporal de vendas.
        
        Returns:
            dict: Dados para gráfico de linhas
        """
        query = db.session.query(
            Venda.data,
            func.sum(Venda.valor_total).label('valor'),
            func.sum(Venda.quantidade).label('quantidade')
        )
        
        query = self._aplicar_filtro_data(query, Venda, data_inicio, data_fim)
        query = query.group_by(Venda.data).order_by(Venda.data)
        
        resultados = query.all()
        
        return {
            'labels': [r.data.strftime('%Y-%m-%d') for r in resultados],
            'valores': [float(r.valor) for r in resultados],
            'quantidades': [int(r.quantidade) for r in resultados]
        }
    
    def vendas_por_categoria(self, data_inicio=None, data_fim=None):
        """
        Retorna vendas agregadas por categoria.
        
        Returns:
            dict: Dados para gráfico de barras
        """
        query = db.session.query(
            Venda.categoria,
            func.sum(Venda.valor_total).label('valor'),
            func.sum(Venda.quantidade).label('quantidade')
        )
        
        query = self._aplicar_filtro_data(query, Venda, data_inicio, data_fim)
        query = query.group_by(Venda.categoria).order_by(func.sum(Venda.valor_total).desc())
        
        resultados = query.all()
        
        return {
            'labels': [r.categoria for r in resultados],
            'valores': [float(r.valor) for r in resultados],
            'quantidades': [int(r.quantidade) for r in resultados]
        }
    
    def vendas_por_regiao(self, data_inicio=None, data_fim=None):
        """
        Retorna vendas agregadas por região.
        
        Returns:
            dict: Dados para gráfico de pizza
        """
        query = db.session.query(
            Venda.regiao,
            func.sum(Venda.valor_total).label('valor')
        )
        
        query = self._aplicar_filtro_data(query, Venda, data_inicio, data_fim)
        query = query.group_by(Venda.regiao).order_by(func.sum(Venda.valor_total).desc())
        
        resultados = query.all()
        total = sum(r.valor for r in resultados)
        
        return {
            'labels': [r.regiao for r in resultados],
            'valores': [float(r.valor) for r in resultados],
            'percentuais': [round((r.valor / total * 100), 2) if total > 0 else 0 for r in resultados]
        }
    
    def top_produtos(self, data_inicio=None, data_fim=None, limite=10):
        """
        Retorna top produtos mais vendidos.
        
        Args:
            limite: Número de produtos a retornar
            
        Returns:
            dict: Dados para gráfico de barras horizontal
        """
        query = db.session.query(
            Venda.produto,
            func.sum(Venda.valor_total).label('valor'),
            func.sum(Venda.quantidade).label('quantidade')
        )
        
        query = self._aplicar_filtro_data(query, Venda, data_inicio, data_fim)
        query = query.group_by(Venda.produto).order_by(func.sum(Venda.valor_total).desc()).limit(limite)
        
        resultados = query.all()
        
        return {
            'labels': [r.produto for r in resultados],
            'valores': [float(r.valor) for r in resultados],
            'quantidades': [int(r.quantidade) for r in resultados]
        }
    
    def _aplicar_filtro_data(self, query, model, data_inicio=None, data_fim=None):
        """Aplica filtros de data na query."""
        if data_inicio:
            try:
                dt_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                query = query.filter(model.data >= dt_inicio)
            except ValueError:
                pass
        
        if data_fim:
            try:
                dt_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
                query = query.filter(model.data <= dt_fim)
            except ValueError:
                pass
        
        return query
    


    """ CATEGORIA A """
    def margem_lucro(self, data_inicio=None, data_fim=None):
        """
        Calcula margem de lucro por categoria (vendas - custos).
        """
        query = db.session.query(
            Venda.categoria,
            func.sum(Venda.valor_total).label('total_vendas'),
            func.sum(Venda.quantidade * Custo.custo_unitario).label('total_custos'),
            (func.sum(Venda.valor_total) - func.sum(Venda.quantidade * Custo.custo_unitario)).label('lucro')
        ).join(Custo, Custo.produto == Venda.produto)

        query = self._aplicar_filtro_data(query, Venda, data_inicio, data_fim)
        query = query.group_by(Venda.categoria)

        resultados = query.all()
        return {
            'labels': [r.categoria for r in resultados],
            'vendas': [float(r.total_vendas) for r in resultados],
            'custos': [float(r.total_custos) for r in resultados],
            'lucros': [float(r.lucro) for r in resultados]
        }
    

    def comparar_metas(self, data_inicio=None, data_fim=None):
        """
        Compara vendas reais com metas por categoria e região.
        """
        sub_vendas = (
            db.session.query(
                Venda.categoria,
                Venda.regiao,
                func.sum(Venda.valor_total).label('total_vendas')
            )
            .group_by(Venda.categoria, Venda.regiao)
        )
        sub_vendas = self._aplicar_filtro_data(sub_vendas, Venda, data_inicio, data_fim)
        sub_vendas = sub_vendas.subquery()

        query = (
            db.session.query(
                Meta.categoria,
                Meta.regiao,
                func.coalesce(sub_vendas.c.total_vendas, 0).label('total_vendas'),
                Meta.meta_valor,
                (func.coalesce(sub_vendas.c.total_vendas, 0) / Meta.meta_valor * 100).label('percentual_atingido')
            )
            .outerjoin(sub_vendas, (Meta.categoria == sub_vendas.c.categoria) & (Meta.regiao == sub_vendas.c.regiao))
        )

        resultados = query.all()
        return {
            'categorias': [r.categoria for r in resultados],
            'regioes': [r.regiao for r in resultados],
            'vendas': [float(r.total_vendas or 0) for r in resultados],
            'metas': [float(r.meta_valor or 0) for r in resultados],
            'percentual': [round(float(r.percentual_atingido or 0), 2) for r in resultados]
        }
    

    def tendencia_mensal(self, data_inicio=None, data_fim=None):
        """
        Retorna crescimento percentual mês a mês das vendas.
        """
        query = db.session.query(
            extract('year', Venda.data).label('ano'),
            extract('month', Venda.data).label('mes'),
            func.sum(Venda.valor_total).label('total')
        )
        query = self._aplicar_filtro_data(query, Venda, data_inicio, data_fim)
        query = query.group_by('ano', 'mes').order_by('ano', 'mes')

        resultados = query.all()

        labels, valores, crescimento = [], [], []
        total_anterior = None
        for r in resultados:
            label = f"{int(r.mes):02d}/{int(r.ano)}"
            labels.append(label)
            valores.append(float(r.total))
            if total_anterior is not None and total_anterior > 0:
                variacao = ((r.total - total_anterior) / total_anterior) * 100
            else:
                variacao = 0
            crescimento.append(round(float(variacao), 2))
            total_anterior = r.total

        return {
            'labels': labels,
            'valores': valores,
            'crescimento_percentual': crescimento
        }
    

    """ CATEGORIA B """
    def vendas_por_vendedor(self, data_inicio=None, data_fim=None):
        """
        Retorna o total de vendas por vendedor.
        """
        query = db.session.query(
            Venda.vendedor,
            func.sum(Venda.valor_total).label('total_vendas')
        )
        query = self._aplicar_filtro_data(query, Venda, data_inicio, data_fim)
        query = query.group_by(Venda.vendedor)

        resultados = query.all()
        return {
            'labels': [r.vendedor for r in resultados],
            'valores': [float(r.total_vendas or 0) for r in resultados]
        }

    def funil_vendas_categoria(self, data_inicio=None, data_fim=None):
        """
        Gera dados para o funil de vendas por categoria:
        - Simula visitas e orçamentos com base nas vendas.
        """
        query = db.session.query(
            Venda.categoria,
            func.sum(Venda.valor_total).label('total_vendas'),
            func.count(Venda.id).label('num_vendas')
        )

        query = self._aplicar_filtro_data(query, Venda, data_inicio, data_fim)
        query = query.group_by(Venda.categoria)
        resultados = query.all()

        categorias = [r.categoria for r in resultados]
        vendas = [float(r.total_vendas or 0) for r in resultados]

        # Simulação (ajuste se quiser dados reais)
        orcamentos = [v * 1.5 for v in vendas]
        visitas = [v * 3 for v in vendas]

        return {
            "categorias": categorias,
            "visitas": visitas,
            "orcamentos": orcamentos,
            "vendas": vendas
        }
    

    def vendas_meses(self, meses):
        """
        Gera comparativos de vendas por meses selecionados no frontend.
        """
        datasets = []

        for mes in meses:
            if not mes:
                continue
            ano, mes_num = map(int, mes.split('-'))
            inicio = datetime(ano, mes_num, 1)
            fim = (inicio + relativedelta(months=1)) - timedelta(days=1)

            # Consulta vendas por dia
            vendas_dia = db.session.query(
                func.date(Venda.data).label('data'),
                func.sum(Venda.valor_total).label('total')
            ).filter(Venda.data.between(inicio, fim)) \
            .group_by(func.date(Venda.data)) \
            .order_by(func.date(Venda.data)) \
            .all()

            # Converte cada data para dia e monta o dict dia -> total
            dia_totais = {}
            for v in vendas_dia:
                # Converte string para datetime caso necessário
                if isinstance(v.data, str):
                    data_obj = datetime.strptime(v.data, "%Y-%m-%d")
                else:
                    data_obj = v.data
                dia_totais[data_obj.day] = float(v.total or 0)

            # Garante todos os dias do mês, mesmo com zero vendas
            num_dias = (fim - inicio).days + 1
            data_values = [dia_totais.get(dia, 0) for dia in range(1, num_dias + 1)]

            datasets.append({
                "label": inicio.strftime("%m-%Y"),  # label do mês
                "data": data_values,
                "borderColor": f"#{random.randint(0,0xFFFFFF):06x}",
                "backgroundColor": "transparent",
                "tension": 0.3
            })

        # labels = dias do mês, pegando do maior número de dias
        if datasets:
            max_dias = max(len(d["data"]) for d in datasets)
            labels = [str(d) for d in range(1, max_dias + 1)]
        else:
            labels = []

        return {"datas": labels, "datasets": datasets}