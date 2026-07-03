from datetime import datetime, timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from lms.models import Lesson
from users.models import User


@shared_task
def send_moderator_email(emails):
    send_mail(
        subject="Обновление материалов курса",
        message="В курсе появились новые уроки, необходимо пройти обучение",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=emails,
    )


@shared_task
def send_latest_update(emails):
    last_update = Lesson.objects.aggregate(Max("updated_at"))["updated_at__max"]
    now = timezone.now()

    if last_update and (now - last_update) > timedelta(hours=4):
        send_mail(
            subject="Последнее обновление",
            message="Произведено последнее обновление, необходимо пройти обучение",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=emails,
        )

@shared_task
def deactivate_inactive_users():
    one_month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(last_login__lt=one_month_ago)
    inactive_users.update(is_active=False)
