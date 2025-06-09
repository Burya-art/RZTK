import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rztk_project.settings')

app = Celery('rztk_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()