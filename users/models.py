from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "admin", "Администратор салона"
        STAFF = "staff", "Мастер"
        CLIENT = "client", "Клиент"

    phone = models.CharField(max_length=32, blank=True)
    role = models.CharField(max_length=16, choices=Roles.choices, default=Roles.CLIENT)

    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"