from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import User
from services.models import Service


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает подтверждения"
        CONFIRMED = "confirmed", "Подтверждено"
        COMPLETED = "completed", "Выполнено"
        CANCELLED = "cancelled", "Отменено"
        NO_SHOW = "no_show", "Клиент не пришёл"

    # Основные поля
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    staff = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="staff_bookings"
    )
    service = models.ForeignKey(Service, on_delete=models.PROTECT)

    # Время записи
    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    # Статус и метаданные
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    notes = models.TextField(blank=True, help_text="Дополнительные заметки")

    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["appointment_date", "appointment_time"]
        # Один мастер не может иметь две записи в одно время
        unique_together = ("staff", "appointment_date", "appointment_time")

    def __str__(self) -> str:
        return f"{self.client.get_full_name()} → {self.service.name} ({self.appointment_date} {self.appointment_time})"

    def clean(self):
        """Валидация бронирования"""
        super().clean()

        # Проверяем, что клиент имеет роль "client"
        if self.client.role != User.Roles.CLIENT:
            raise ValidationError("Бронирование может создать только клиент")

        # Проверяем, что мастер имеет роль "staff"
        if self.staff.role != User.Roles.STAFF:
            raise ValidationError("Мастер должен иметь роль 'staff'")

        # Проверяем, что дата не в прошлом
        if self.appointment_date < timezone.now().date():
            raise ValidationError("Нельзя записаться на прошедшую дату")

        # Проверяем, что услуга активна
        if not self.service.is_active:
            raise ValidationError("Услуга неактивна")

    def save(self, *args, **kwargs):
        """Переопределяем save для автоматической валидации"""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def duration_minutes(self):
        """Длительность услуги в минутах"""
        return self.service.duration_minutes

    @property
    def total_price(self):
        """Общая стоимость услуги"""
        return self.service.price


class BookingHistory(models.Model):
    """История изменений бронирования"""

    class Action(models.TextChoices):
        CREATED = "created", "Создано"
        CONFIRMED = "confirmed", "Подтверждено"
        CANCELLED = "cancelled", "Отменено"
        RESCHEDULED = "rescheduled", "Перенесено"
        COMPLETED = "completed", "Завершено"
        NO_SHOW = "no_show", "Не пришёл"

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="history"
    )
    action = models.CharField(max_length=16, choices=Action.choices)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "История бронирования"
        verbose_name_plural = "История бронирований"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.booking} - {self.get_action_display()}"
