from apps.celery import celery_redis
from apps.web.email_crawler import email_crawler


@celery_redis.task(name='apps.app.crawl_email_addresses', queue='redis_tasks', bind=True)
def crawl_email_addresses(self, url: str):
    email_addresses = email_crawler.crawl_sync(url)
    return {"emails": email_addresses}
