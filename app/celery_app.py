from celery import Celery

celery = Celery(__name__)

def make_celery(app):
    """Inicializa Celery com contexto Flask e schedule de 1 hora."""
    celery.conf.update(app.config)
    celery.conf.beat_schedule_filename = 'celerybeat-schedule'

    # Tarefas periódicas
    celery.conf.beat_schedule = {
        "atualizar-cotacoes-1hora": {
            "task": "cotacoes.atualizar",
            "schedule": 60.0,
        }
    }
    celery.conf.timezone = "UTC"

    # Contexto Flask para tasks
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery