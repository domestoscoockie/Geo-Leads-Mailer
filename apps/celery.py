import os
from celery import Celery
from .config import config

os.environ.setdefault("DJANGO_SETTINGS_MODULE", config.django_settings_module)

celery_rabbit = Celery(
    'rabbit_tasks',
    broker=config.rabbitmq_broker_url,
    set_as_current=False,
    include=[
        'apps.app.tasks.tasks_rabbit',
    ],
)

celery_rabbit.config_from_object("django.conf:settings", namespace="CELERY")
celery_rabbit.conf.task_default_queue = 'rabbit_tasks'



celery_redis = Celery(
    "redis_tasks",
    broker=config.redis_broker_url,
    set_as_current=False,
    include=[
        'apps.app.tasks.tasks_redis',
    ],
)
celery_redis.config_from_object("django.conf:settings", namespace="CELERY")
celery_redis.conf.task_default_queue = 'redis_tasks'
