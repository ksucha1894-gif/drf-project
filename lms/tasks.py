from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.utils import timezone

from lms.models import Course, Lesson, Subscription
from users.models import User


@shared_task
def send_moderator_email(course_id):
    try:
        course = Course.objects.get(id=course_id)
        emails = [sub.user.email for sub in course.subscription_set.all()]

        send_mail(
            subject="Обновление материалов курса",
            message="В курсе появились новые уроки, необходимо пройти обучение",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=emails,
        )
    except ObjectDoesNotExist:
        print(f"Course with id {course_id} does not exist.")


@shared_task
def send_latest_update(course_id):
    try:
        course = Course.objects.get(id=course_id)
        now = timezone.now()

        if now - course.updated_at < timedelta(hours=4):
            emails = [sub.user.email for sub in course.subscription_set.all()]

            send_mail(
                subject="Последнее обновление",
                message="Произведено последнее обновление, необходимо пройти обучение",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=emails,
            )
    except ObjectDoesNotExist:
        print(f"Course with id {course_id} does not exist.")


@shared_task
def deactivate_inactive_users():
    one_month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(last_login__lt=one_month_ago)
    inactive_users.update(is_active=False)
