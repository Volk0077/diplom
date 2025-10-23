from django.contrib import admin
from .models import Booking, BookingHistory

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "client_name", "staff_name", "service_name", 
        "appointment_date", "appointment_time", "status", "total_price"
    )
    list_filter = ("status", "appointment_date", "staff", "service__category")
    search_fields = ("client__username", "client__first_name", "client__last_name", "notes")
    date_hierarchy = "appointment_date"
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Основная информация", {
            "fields": ("client", "staff", "service")
        }),
        ("Время записи", {
            "fields": ("appointment_date", "appointment_time")
        }),
        ("Статус и заметки", {
            "fields": ("status", "notes")
        }),
        ("Системная информация", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        })
    )
    
    def client_name(self, obj):
        return obj.client.get_full_name()
    client_name.short_description = "Клиент"
    
    def staff_name(self, obj):
        return obj.staff.get_full_name()
    staff_name.short_description = "Мастер"
    
    def service_name(self, obj):
        return obj.service.name
    service_name.short_description = "Услуга"

@admin.register(BookingHistory)
class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ("booking", "action", "user", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("booking__client__username", "notes")
    readonly_fields = ("created_at",)

# Register your models here.
