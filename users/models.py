from django.contrib.auth.models import AbstractUser
from django.db import models
from services.models import ServiceCategory


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "admin", "Администратор салона"
        STAFF = "staff", "Мастер"
        CLIENT = "client", "Клиент"

    phone = models.CharField(max_length=32, blank=False, verbose_name="Телефон")
    role = models.CharField(max_length=16, choices=Roles.choices, default=Roles.CLIENT, verbose_name="Роль")
    specialization = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Специализация",
        help_text="Категория услуг, в которой специализируется мастер"
    )

    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"
