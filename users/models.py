from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def get_by_natural_key(self, email):
        return self.get(email=email)

class User(AbstractBaseUser):
    username = None
    email = models.EmailField(
        unique=True, verbose_name="Почта", help_text="Укажите почту"
    )
    phone = models.CharField(
        max_length=35,
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Укажите телефон",
    )
    city = models.TextField(
        max_length=100, verbose_name="Город", help_text="Введите город проживания"
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        verbose_name="Аватар",
        blank=True,
        null=True,
        help_text="Загрузите свой аватар",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_date = models.DateField()
    paid_course = models.ForeignKey(
        "lms.Course", null=True, blank=True, on_delete=models.SET_NULL
    )
    paid_lesson = models.ForeignKey(
        "lms.Lesson", null=True, blank=True, on_delete=models.SET_NULL
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=20, choices=[("cash", "Наличные"), ("transfer", "Перевод на счет")]
    )

    class Meta:
        db_table = "payment"
        ordering = ["-payment_date"]
