from app.celery_app import celery
from app.services.data_collector import DataCollector

@celery.task
def atualizar_cotacoes():
    """Task que atualiza cotações"""
    try:
        collector = DataCollector()
        num_cotacoes = collector.coletar_cotacoes()
        print(f"✅ Cotações atualizadas: {num_cotacoes}")
        return num_cotacoes
    except Exception as e:
        print(f"❌ Erro ao atualizar cotações: {e}")
        return None