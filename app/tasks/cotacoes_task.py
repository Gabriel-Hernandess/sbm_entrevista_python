from app.services.data_collector import DataCollector
from app.celery_app import celery
from flask import current_app

@celery.task(bind=True, name="cotacoes.atualizar")
def atualizar_cotacoes_task(self):
    """Task Celery para coletar cotações e salvar no banco."""
    try:
        collector = DataCollector()
        total = collector.coletar_cotacoes()
        return {"message": "Cotações atualizadas com sucesso", "total": total}
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar cotações: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)