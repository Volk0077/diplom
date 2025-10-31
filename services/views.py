from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from .models import ServiceCategory, Service
from bookings.forms import BookingForm, ServiceBookingForm
from bookings.models import Booking
from datetime import datetime


def service_list(request):
    """Список всех услуг"""
    categories = ServiceCategory.objects.filter(is_active=True).prefetch_related(
        "services"
    )
    context = {"categories": categories}
    return render(request, "services/service_list.html", context)


def service_detail(request, slug):
    """Детальная страница услуги с возможностью бронирования"""
    service = get_object_or_404(Service, slug=slug, is_active=True)

    # Форма бронирования с предварительно выбранной услугой
    if request.method == "POST":
        form = ServiceBookingForm(request.POST, initial={'service': service.id})
        if form.is_valid():
            # Создаем booking с выбранной услугой
            time_str = form.cleaned_data['appointment_time']
            time_obj = datetime.strptime(time_str, "%H:%M").time()

            booking = Booking(
                client=request.user,
                staff=form.cleaned_data['staff'],
                service=service,  # Используем текущую услугу из URL
                appointment_date=form.cleaned_data['appointment_date'],
                appointment_time=time_obj
            )
            booking.save()
            messages.success(request, f'Запись на "{service.name}" успешно создана!')
            return redirect('bookings:my_bookings')
        else:
            # Отладка: выводим ошибки формы
            print(f"Form errors: {form.errors}")
            print(f"Non field errors: {form.non_field_errors()}")
    else:
        form = ServiceBookingForm(initial={'service': service.id})

    context = {
        "service": service,
        "booking_form": form
    }
    return render(request, "services/service_detail.html", context)
