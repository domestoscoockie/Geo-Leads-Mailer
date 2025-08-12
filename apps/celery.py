import os
from celery import Celery
from .config import config

os.environ.setdefault("DJANGO_SETTINGS_MODULE", config.django_settings_module)

celery_app = Celery(config.app_name, broker=config.rabbitmq_broker_url)

celery_app.config_from_object("django.conf:settings", namespace="CELERY")

celery_app.autodiscover_tasks()


@celery_app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
