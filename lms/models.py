from django.db import models


class Course(models.Model):
    name = models.CharField(
        max_length=150, verbose_name="Название", help_text="Укажите название курса"
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True,
        null=True,
        help_text="Введите описание курса",
    )
    image = models.ImageField(
        upload_to="lms/images/",
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите превью курса",
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    name = models.CharField(
        max_length=150, verbose_name="Название", help_text="Укажите название урока"
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True,
        null=True,
        help_text="Введите описание урока",
    )
    image = models.ImageField(
        upload_to="lms/images/",
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите превью урока",
    )
    video = models.CharField(
        max_length=150,
        verbose_name="Cсылка на видео",
        help_text="Укажите ссылку на видео",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
