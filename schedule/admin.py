from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from users.models import User
from .models import WorkingHours, SpecialHours


class ScheduleStaffFilter(SimpleListFilter):
    """Фильтр для показа только мастеров в расписании"""
    title = 'Мастер'
    parameter_name = 'staff'

    def lookups(self, request, model_admin):
        # Возвращаем только мастеров
        staff_members = User.objects.filter(role='staff').order_by('first_name')
        return [(staff.id, staff.get_full_name() or staff.username) for staff in staff_members]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(staff_id=self.value())
        return queryset


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ("staff", "get_day_name", "start_time", "end_time", "is_active")
    list_filter = ("day_of_week", "is_active", ScheduleStaffFilter)
    search_fields = ("staff__username", "staff__first_name", "staff__last_name")
    
    def get_day_name(self, obj):
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        return days[obj.day_of_week]
    get_day_name.short_description = "День недели"

@admin.register(SpecialHours)
class SpecialHoursAdmin(admin.ModelAdmin):
    list_display = ("staff", "date", "start_time", "end_time", "note")
    list_filter = ("date", ScheduleStaffFilter)
    search_fields = ("staff__username", "note")
    date_hierarchy = "date"
