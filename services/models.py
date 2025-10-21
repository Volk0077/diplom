from django.db import models


class ServiceCategory(models.Model):
    name = models.CharField(max_length=128, unique=True)
    is_active = models.BooleanField(default=True)    

    class Meta:
        verbose_name = 'Категория услуги'
        verbose_name_plural = 'Категории услуг'
        ordering = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, related_name="services")
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        unique_together = ("category", "name")
        ordering = ["category__name", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.duration_minutes} мин)"
