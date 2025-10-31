from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from bookings.models import Booking
from .forms import UserRegistrationForm


def profile(request):
    user_bookings = Booking.objects.filter(client=request.user)
    return render(request, 'users/profile.html', {'bookings': user_bookings})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user =form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('services:list')
    else:
        form = UserRegistrationForm()
    return render(request,'users/register.html', {'form':form})


def logout_redirect(request):
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы')
    return redirect('services:list')
