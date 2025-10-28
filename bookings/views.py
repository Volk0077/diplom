from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Booking
from .forms import BookingForm


@login_required
def my_bookings(request):
    """Записи клиента"""
    bookings = Booking.objects.filter(client=request.user).order_by(
        "-appointment_date", "-appointment_time"
    )
    context = {"bookings": bookings}
    return render(request, "bookings/my_bookings.html", context)


def create_booking(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = BookingForm()
    return render(request, 'bookings/create_booking.html', {'form':form})


