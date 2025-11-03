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
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings", verbose_name="Клиент")
    staff = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="staff_bookings", verbose_name="Мастер"
    )
    service = models.ForeignKey(Service, on_delete=models.PROTECT, verbose_name="Услуга")

    # Время записи
    appointment_date = models.DateField(verbose_name="Дата записи")
    appointment_time = models.TimeField(verbose_name="Время записи")

    # Статус и метаданные
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING,
        verbose_name="Статус"
    )
    notes = models.TextField(blank=True, verbose_name="Заметки", help_text="Дополнительные заметки")

    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["appointment_date", "appointment_time"]
        # Один мастер не может иметь две записи в одно время
        unique_together = ("staff", "appointment_date", "appointment_time")

    def __str__(self) -> str:
        client_name = self.client.get_full_name() if self.client else "Без клиента"
        service_name = self.service.name if self.service else "Без услуги"
        return f"{client_name} → {service_name} ({self.appointment_date} {self.appointment_time})"

    def clean(self):
        """Валидация бронирования"""
        super().clean()

        # Проверяем роли только если объекты установлены
        if self.client and self.client.role != User.Roles.CLIENT:
            raise ValidationError("Бронирование может создать только клиент")

        if self.staff and self.staff.role != User.Roles.STAFF:
            raise ValidationError("Мастер должен иметь роль 'staff'")

        # Проверяем услугу только если она установлена
        if self.service and not self.service.is_active:
            raise ValidationError("Услуга неактивна")

        # Валидация даты перенесена в форму для лучшего UX

    def save(self, *args, **kwargs):
        """Переопределяем save для автоматической валидации и истории изменений"""
        # Извлекаем пользователя из kwargs, если передан
        user = kwargs.pop('user', None)

        # Проверяем, изменился ли статус
        if self.pk:  # Если объект уже существует
            old_booking = Booking.objects.get(pk=self.pk)
            if old_booking.status != self.status:
                # Создаем запись в истории
                from .models import BookingHistory
                BookingHistory.objects.create(
                    booking=self,
                    action=self.status,
                    user=user
                )

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
        PENDING = "pending", "Ожидает подтверждения"
        CONFIRMED = "confirmed", "Подтверждено"
        COMPLETED = "completed", "Завершено"
        CANCELLED = "cancelled", "Отменено"
        NO_SHOW = "no_show", "Клиент не пришел"

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="history", verbose_name="Бронирование"
    )
    action = models.CharField(max_length=16, choices=Action.choices, verbose_name="Действие")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь")
    notes = models.TextField(blank=True, verbose_name="Заметки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "История бронирования"
        verbose_name_plural = "История бронирований"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.booking} - {self.get_action_display()}"
    

class Review(models.Model):
    """Отзывы о мастерах"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, verbose_name="Бронирование")
    rating = models.IntegerField(
        choices=[(i,f"{i} ⭐") for i in range(1,6)],
        verbose_name="Рейтинг"
    )
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at= models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Отзыв на {self.booking} - {self.rating}⭐"
