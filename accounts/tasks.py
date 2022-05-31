from celery import shared_task
from accounts.services import send_client_email


@shared_task
def send_client_email_task(user_id, site, subject, template):
    send_client_email(user_id, site, subject, template)

