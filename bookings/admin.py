from django.contrib import admin
from django import forms
from django.contrib import messages
from django.utils.translation import ngettext
from django.contrib.admin import RelatedFieldListFilter, SimpleListFilter
from .models import Booking, BookingHistory, Review
from users.models import User
from services.models import ServiceCategory


class StaffFilter(SimpleListFilter):
    """Фильтр для показа только мастеров"""

    title = "Мастер"
    parameter_name = "staff"

    def lookups(self, request, model_admin):
        # Возвращаем только мастеров
        staff_members = User.objects.filter(role="staff").order_by("first_name")
        return [
            (staff.id, staff.get_full_name() or staff.username)
            for staff in staff_members
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(staff_id=self.value())
        return queryset


class ReviewStaffFilter(SimpleListFilter):
    """Фильтр для показа только мастеров в отзывах"""

    title = "Мастер"
    parameter_name = "booking__staff"

    def lookups(self, request, model_admin):
        # Возвращаем только мастеров
        staff_members = User.objects.filter(role="staff").order_by("first_name")
        return [
            (staff.id, staff.get_full_name() or staff.username)
            for staff in staff_members
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(booking__staff_id=self.value())
        return queryset


class CategoryFilter(SimpleListFilter):
    """Фильтр по категориям услуг"""

    title = "Категория услуги"
    parameter_name = "service__category"

    def lookups(self, request, model_admin):
        # Возвращаем все категории услуг
        categories = ServiceCategory.objects.all().order_by("name")
        return [(cat.id, cat.name) for cat in categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(service__category_id=self.value())
        return queryset


class BookingAdminForm(forms.ModelForm):
    """Форма для админки с явными choices"""

    status = forms.ChoiceField(choices=Booking.Status.choices, label="Статус")

    class Meta:
        model = Booking
        fields = "__all__"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    form = BookingAdminForm
    list_display = (
        "client_name",
        "staff_name",
        "service_name",
        "appointment_date",
        "appointment_time",
        "status",
        "total_price_display",
    )
    list_display_links = ("client_name",)  # Явно указываем, что client_name - ссылка
    list_editable = (
        "status",
        "appointment_date",
        "appointment_time",
    )  # Разрешаем редактирование status прямо в списке
    list_filter = ("status", "appointment_date", StaffFilter, CategoryFilter)
    search_fields = (
        "client__username",
        "client__first_name",
        "client__last_name",
        "notes",
    )
    date_hierarchy = "appointment_date"
    readonly_fields = ("created_at", "updated_at")
    actions = [
        "mark_as_confirmed",
        "mark_as_completed",
        "mark_as_cancelled",
        "mark_as_no_show",
    ]

    fieldsets = (
        ("Основная информация", {"fields": ("client", "staff", "service")}),
        ("Время записи", {"fields": ("appointment_date", "appointment_time")}),
        ("Статус и заметки", {"fields": ("status", "notes")}),
        (
            "Системная информация",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def client_name(self, obj):
        full_name = obj.client.get_full_name()
        return full_name if full_name else obj.client.username

    client_name.short_description = "Клиент"

    def staff_name(self, obj):
        return obj.staff.get_full_name()

    staff_name.short_description = "Мастер"

    def service_name(self, obj):
        return obj.service.name

    service_name.short_description = "Услуга"

    def total_price_display(self, obj):
        return f"{obj.total_price} ₽"

    total_price_display.short_description = "Цена"

    # Actions для массового изменения статуса
    def mark_as_confirmed(self, request, queryset):
        for booking in queryset:
            booking.status = "confirmed"
            booking.save(user=request.user)  # Передаем пользователя
        updated = queryset.count()
        self.message_user(
            request,
            ngettext(
                "%d запись была успешно подтверждена.",
                "%d записей были успешно подтверждены.",
                updated,
            )
            % updated,
        )

    mark_as_confirmed.short_description = "Отметить выбранные записи как подтвержденные"

    def mark_as_completed(self, request, queryset):
        for booking in queryset:
            booking.status = "completed"
            booking.save(user=request.user)
        updated = queryset.count()
        self.message_user(
            request,
            ngettext(
                "%d запись была успешно завершена.",
                "%d записей были успешно завершены.",
                updated,
            )
            % updated,
        )

    mark_as_completed.short_description = "Отметить выбранные записи как завершенные"

    def mark_as_cancelled(self, request, queryset):
        for booking in queryset:
            booking.status = "cancelled"
            booking.save(user=request.user)
        updated = queryset.count()
        self.message_user(
            request,
            ngettext(
                "%d запись была успешно отменена.",
                "%d записей были успешно отменены.",
                updated,
            )
            % updated,
        )

    mark_as_cancelled.short_description = "Отметить выбранные записи как отмененные"

    def mark_as_no_show(self, request, queryset):
        for booking in queryset:
            booking.status = "no_show"
            booking.save(user=request.user)
        updated = queryset.count()
        self.message_user(
            request,
            ngettext(
                "%d запись была отмечена как неявка.",
                "%d записей были отмечены как неявка.",
                updated,
            )
            % updated,
        )

    mark_as_no_show.short_description = "Отметить выбранные записи как неявка клиента"

    def save_model(self, request, obj, form, change):
        """Переопределяем сохранение для отслеживания пользователя"""
        # Передаем пользователя в save()
        obj.save(user=request.user)


@admin.register(BookingHistory)
class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ("booking", "action", "user", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("booking__client__username", "notes")
    readonly_fields = ("created_at",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "booking_info",
        "client_name",
        "staff_name",
        "rating_display",
        "comment_preview",
        "created_at"
    )
    list_filter = ("rating", "created_at", ReviewStaffFilter)
    search_fields = (
        "booking__client__username",
        "booking__client__first_name",
        "booking__client__last_name",
        "comment"
    )
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"

    fieldsets = (
        ("Информация о записи", {
            "fields": ("booking", "client_name", "staff_name")
        }),
        ("Отзыв", {
            "fields": ("rating", "comment")
        }),
        ("Системная информация", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )

    def booking_info(self, obj):
        return f"Запись #{obj.booking.id}"
    booking_info.short_description = "Запись"

    def client_name(self, obj):
        full_name = obj.booking.client.get_full_name()
        return full_name if full_name else obj.booking.client.username
    client_name.short_description = "Клиент"

    def staff_name(self, obj):
        return obj.booking.staff.get_full_name()
    staff_name.short_description = "Мастер"

    def rating_display(self, obj):
        stars = "⭐" * obj.rating
        return f"{obj.rating}/5 {stars}"
    rating_display.short_description = "Рейтинг"

    def comment_preview(self, obj):
        if obj.comment:
            return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment
        return "Без комментария"
    comment_preview.short_description = "Комментарий"

    def has_add_permission(self, request):
        # Отзывы могут добавлять только клиенты через интерфейс
        return False

    def has_change_permission(self, request, obj=None):
        # Администраторы могут только просматривать отзывы
        return False

    def has_delete_permission(self, request, obj=None):
        # Разрешаем удаление отзывов администраторам
        return True
