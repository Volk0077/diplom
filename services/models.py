from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode


def transliterate_slug(text):
    """Транслитерация кириллицы в латиницу для slug"""
    return slugify(unidecode(text))


class ServiceCategory(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=128, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Категория услуги"
        verbose_name_plural = "Категории услуг"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = transliterate_slug(self.name)
        super().save(*args, **kwargs)


class Service(models.Model):
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.PROTECT, related_name="services"
    )
    name = models.CharField(max_length=128, verbose_name="Название")
    slug = models.SlugField(max_length=128, unique=True, null=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Описание")
    duration_minutes = models.PositiveIntegerField(verbose_name="Длительность (минуты)")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Цена")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        unique_together = ("category", "name")
        ordering = ["name"]  # Изменено на алфавитный порядок по названию

    def __str__(self) -> str:
        return f"{self.name} ({self.duration_minutes} мин)"

    def get_absolute_url(self):
        return reverse("services:detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = transliterate_slug(self.name)
        super().save(*args, **kwargs)
