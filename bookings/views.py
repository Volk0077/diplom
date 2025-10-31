from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Booking
from .forms import BookingForm
from django.contrib import messages
from users.models import User
from services.models import Service
from datetime import datetime
from django.utils import timezone



@login_required
def my_bookings(request):
    """Записи клиента"""
    bookings = Booking.objects.filter(client=request.user).order_by(
        "appointment_date", "appointment_time"
    )

    # Текущая дата и время для проверки прошедших записей
    from django.utils import timezone
    context = {
        "bookings": bookings,
        "today": timezone.now().date(),
        "now_time": timezone.now().time()
    }
    return render(request, "bookings/my_bookings.html", context)


@login_required
def create_booking(request):
    # Проверяем, что пользователь имеет роль клиента
    if request.user.role != 'client':
        messages.error(request, 'Только клиенты могут создавать записи')
        return redirect('services:list')

    if request.method == "POST":
        form = BookingForm(request.POST)
        # Устанавливаем client до валидации
        form.instance.client = request.user

        if form.is_valid():
            # Конвертируем время в правильный формат перед сохранением
            time_str = form.cleaned_data['appointment_time']
            form.instance.appointment_time = datetime.strptime(time_str, "%H:%M").time()

            form.save()
            messages.success(request, 'Запись успешно создана!')
            return redirect('bookings:my_bookings')
    else:
        form = BookingForm()
    return render(request, 'bookings/create_booking.html', {'form': form})


def cancel_booking(request, booking_id):
    """Отмена записи клиентом"""
    try:
        booking = Booking.objects.get(
            id=booking_id,
            client=request.user
        )

        # Нельзя отменить уже отмененную запись
        if booking.status == 'cancelled':
            messages.error(request, 'Эта запись уже отменена')
            return redirect('bookings:my_bookings')

        # Проверяем, что запись не в прошлом
        if booking.appointment_date < timezone.now().date() or \
            (booking.appointment_date == timezone.now().date() and \
            booking.appointment_time <= timezone.now().time()):
            messages.error(request, 'Нельзя отменить прошедшую запись')
            return redirect('bookings:my_bookings')
        
        booking.status = 'cancelled'
        booking.save(user=request.user)
        messages.success(request, f'Запись на {booking.appointment_date} в {booking.appointment_time} отменена')

    except Booking.DoesNotExist:
        messages.error(request, 'Запись не найдена или уже отменена')
    
    return redirect('bookings:my_bookings')


def api_services_list(request):
    """API для получения списка услуг по категории"""
    category_id = request.GET.get('category')
    
    if category_id:
        try:
            from services.models import ServiceCategory
            category = ServiceCategory.objects.get(pk=category_id)
            # Возвращаем услуги этой категории
            services = Service.objects.filter(category=category).values('id', 'name').order_by('name')
        except ServiceCategory.DoesNotExist:
            services = Service.objects.none()
    else:
        # Если категория не указана, возвращаем все услуги
        services = Service.objects.filter(is_active=True).values('id', 'name').order_by('name')
    
    return JsonResponse(list(services), safe=False)


def api_staff_list(request):
    """API для получения списка мастеров"""
    service_id = request.GET.get('service')

    if service_id:
        try:
            service = Service.objects.get(pk=service_id)
            # Возвращаем мастеров, специализирующихся на категории услуги
            staff = User.objects.filter(
                role='staff',
                specialization=service.category
            ).values('id', 'first_name').order_by('first_name')
        except Service.DoesNotExist:
            staff = User.objects.filter(role='staff').values('id', 'first_name').order_by('first_name')
    else:
        # Если услуга не указана, возвращаем всех мастеров
        staff = User.objects.filter(role='staff').values('id', 'first_name').order_by('first_name')

    return JsonResponse(list(staff), safe=False)
