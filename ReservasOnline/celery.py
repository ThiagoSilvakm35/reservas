import os
from celery import Celery
from celery.schedules import crontab

# Define o módulo de configurações padrão do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ReservasOnline.settings')

app = Celery('ReservasOnline')

# Usando namespace 'CELERY' para todas as configurações relacionadas ao Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carrega as tarefas dos arquivos tasks.py em todos os apps registrados no Django
app.autodiscover_tasks()

# Agenda de tarefas periódicas
app.conf.beat_schedule = {
    'enviar-lembretes-diarios': {
        'task': 'notificacoes.tasks.enviar_lembretes_reservas',
        'schedule': crontab(hour=9, minute=0),  # Executa todos os dias às 9h
    },
    'verificar-confirmacoes-reservas': {
        'task': 'reservas.tasks.verificar_confirmacoes_reservas',
        'schedule': crontab(hour='*/1'),  # Executa a cada hora
    },
    'enviar-relatorio-semanal': {
        'task': 'admin_dashboard.tasks.enviar_relatorio_semanal',
        'schedule': crontab(day_of_week=1, hour=8, minute=0),  # Segunda-feira às 8h
    },
    'arquivar-reservas-antigas': {
        'task': 'reservas.tasks.arquivar_reservas_antigas',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),  # Primeiro dia do mês
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 