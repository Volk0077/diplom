from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User


class WorkingHours(models.Model):
    """Рабочие часы мастера по дням недели"""
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name="working_hours")
    day_of_week = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(6)],
        help_text="0=Понедельник, 1=Вторник, ..., 6=Воскресенье"
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Рабочие часы"
        verbose_name_plural = "Рабочие часы"
        unique_together = ("staff", "day_of_week")
        ordering = ["staff", "day_of_week"]

    def __str__(self) -> str:
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        return f"{self.staff.username} - {days[self.day_of_week]} {self.start_time}-{self.end_time}"


class SpecialHours(models.Model):
    """Особые часы работы (праздники, переносы)"""
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name="special_hours")
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True) # None - выходной
    end_time = models.TimeField(null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Особые часы работы"
        verbose_name_plural = "Особые часы"
        unique_together = ("staff", "date")
        ordering = ["staff", "date"]

    def __str__(self) -> str:
        if self.start_time and self.end_time:
            return f"{self.staff.username} - {self.date} {self.start_time}-{self.end_time}"
        else:
            return f"{self.staff.username} - {self.date} (выходной)"