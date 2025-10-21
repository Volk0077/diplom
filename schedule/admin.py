from django.contrib import admin
from .models import WorkingHours, SpecialHours


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ("staff", "get_day_name", "start_time", "end_time", "is_active")
    list_filter = ("day_of_week", "is_active", "staff")
    search_fields = ("staff__username", "staff__first_name", "staff__last_name")
    
    def get_day_name(self, obj):
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        return days[obj.day_of_week]
    get_day_name.short_description = "День недели"

@admin.register(SpecialHours)
class SpecialHoursAdmin(admin.ModelAdmin):
    list_display = ("staff", "date", "start_time", "end_time", "note")
    list_filter = ("date", "staff")
    search_fields = ("staff__username", "note")
    date_hierarchy = "date"
