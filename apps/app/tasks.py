from celery import shared_task
from typing import Optional, List


from apps.web.mail_send import MailSend 


@shared_task(bind=True)
def send_email_task(self, to: str, subject: str, text: str, attachments: Optional[List[str]] = None):

    mailer = MailSend()
    # MailSend.send expects first arg to be the recipient email (despite the name userId)
    mailer.send(to, subject, text, attachments)
    return {"to": to, "status": "queued"}

@shared_task(bind=True)
def send_bulk_emails(self, payloads: list, delay_s: int = 5):

    for i, p in enumerate(payloads):
        send_email_task.apply_async(kwargs=p, countdown=i * delay_s)
    return {"count": len(payloads)}
