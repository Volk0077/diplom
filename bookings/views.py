from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Booking


@login_required
def my_bookings(request):
    """Мои записи клиента"""
    bookings = Booking.objects.filter(client=request.user).order_by(
        "-appointment_date", "-appointment_time"
    )
    context = {"bookings": bookings}
    return render(request, "bookings/my_bookings.html", context)
